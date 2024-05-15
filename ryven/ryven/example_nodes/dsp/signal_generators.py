from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QMainWindow, QGridLayout, QGroupBox, QLayout
from numpy import pi
import numpy as np
from ryven.NWENV import *
from ryven.NENV import *
from qtpy.QtWidgets import QWidget, QComboBox, QLineEdit, \
    QDialogButtonBox, QLabel, QVBoxLayout
from qtpy.QtGui import QPixmap
from scipy.signal import square
from qtpy.QtCore import Qt
import os
import globals


class NodeBase(Node):
    version = 'v0.1'
    color = '#FF0000'


class SignalGeneratorWindow(QMainWindow):
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget  # Keep a reference to the parent widget
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowSystemMenuHint & ~Qt.WindowMinMaxButtonsHint)
        self.setWindowTitle("Block Parameters: Signal Generator")
        self.setWindowIcon(self.parent_widget.windowIcon())
        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create layout
        main_layout = QVBoxLayout(central_widget)

        description_group_box = QGroupBox("Signal Generator")
        layout = QGridLayout()
        layout.addWidget(QLabel("Output various wave forms:"))
        layout.addWidget(QLabel("   Y(t) = Amp*Waveform(Freq, t)"))
        description_group_box.setLayout(layout)
        main_layout.addWidget(description_group_box)

        # Create a group box
        parameters_group_box = QGroupBox("Parameters")
        main_layout.addWidget(parameters_group_box)

        # Create layout for group box
        layout = QGridLayout()
        parameters_group_box.setLayout(layout)

        self.type_label = QLabel("Signal type:")
        self.type_field = QComboBox()
        self.type_field.addItem('sin')
        self.type_field.addItem('square')
        self.type_field.setCurrentText(str(self.parent_widget.fun_type))

        self.amp_label = QLabel("Amplitude:")
        self.amp_field = QLineEdit(str(self.parent_widget.amplitude))

        self.freq_label = QLabel("Frequency (Hz):")
        self.freq_field = QLineEdit(str(self.parent_widget.frequency))

        # Buttons
        self.btnBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btnBox.accepted.connect(self.ok_callback)
        self.btnBox.rejected.connect(self.cancel_callback)

        layout.addWidget(self.type_label, 0, 0)
        layout.addWidget(self.type_field, 1, 0)
        layout.addWidget(self.amp_label, 2, 0)
        layout.addWidget(self.amp_field, 3, 0)
        layout.addWidget(self.freq_label, 4, 0)
        layout.addWidget(self.freq_field, 5, 0)
        layout.addWidget(self.btnBox, 6, 0, 1, 2)  # Span 2 columns for the button box

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")  # Set the text color to red for visibility
        self.error_label.hide()  # Hide it initially

        # Add the error label to the layout
        main_layout.addWidget(self.error_label)

        # Apply stylesheet
        self.setStyleSheet("""
            QGroupBox {
                background-color: #D3D3D3; /* Light grey background */
                color: black; /* Text color */
                border: none; /* No border around the QGroupBox */
                margin-top: 20px; /* Space for the title */
                font-size: 10pt; /* Set font size for all widgets inside QGroupBox */
            }
            QGroupBox::title {
                subcontrol-origin: margin; /* Position the title within the margin area */
                subcontrol-position: top center; /* Center the title at the top */
                padding: 0 15px; /* Padding on the left and right */
                background-color: #D3D3D3; /* Same background color as QGroupBox */
                color: black; /* Text color for the title */
                border: 1px solid black; /* Red border around the title */
            }
            QLabel, QComboBox, QLineEdit, QPushButton {
                color: black;
                font-size: 10pt; /* Set font size to 10 for these widgets */
            }
            QLineEdit, QComboBox{
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: white;
            }
            QComboBox QAbstractItemView {
        background-color: white; /* Set the background color for the item view */
        color: black; /* Set the text color for items */
        selection-color: black; /* Set the text color when an item is selected */
    }
        """)

    def ok_callback(self):
        isNoError = True
        amp = self.amp_field.text()

        freq = self.freq_field.text()

        vars = self.parent_widget.node.get_vars_manager().variables
        # Creating a dictionary to map v.name to an int/float
        vars_dict = {v.name: float(v.val) if '.' in str(v.val) else int(v.val) for v in vars}
        flag = "amp"
        try:
            # Evaluating amp and freq
            eval_amp = eval(amp, {}, vars_dict)
            flag = "freq"
            eval_freq = eval(freq, {}, vars_dict)

            if not isinstance(eval_amp, (int, float)) or not isinstance(eval_freq, (int, float)):
                self.error_label.setText(f"Error: {amp} or {freq} is not number")
                self.error_label.show()
                isNoError = False

        except Exception as e:
            if flag == "amp":
                self.error_label.setText(f"Error: {self.amp_field.text()} not valid")
                self.error_label.show()
            elif flag == "freq":
                self.error_label.setText(f"Error: {self.freq_field.text()} not valid")
                self.error_label.show()
            isNoError = False

        # If both amplitude and frequency evaluations were successful, proceed
        if isNoError:
            self.error_label.hide()
            self.parent_widget.fun_type = self.type_field.currentText()
            self.parent_widget.amplitude = self.amp_field.text()
            self.parent_widget.frequency = self.freq_field.text()
            self.parent_widget.update_amp_and_freq()
            self.close()

    def cancel_callback(self):
        self.close()


class SignalWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.window = None


        self.amplitude = self.node.amplitude
        self.frequency = self.node.frequency
        self.fun_type = str(self.node.function_type)

        self.signal_generator_window = SignalGeneratorWindow(self)

        # layout = QVBoxLayout()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        layout.setSizeConstraint(QLayout.SetFixedSize)  # Set the size constraint

        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "Signal Generator.png")
        image = QPixmap(icon_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        imageLabel.setMargin(0)  # Set the margins of the imageLabel to 0
        layout.addWidget(imageLabel)

        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QWidget * {
                color: black;
                font-size: 10pt;
                font-weight: bold;
            }
            QSlider {
                color: black;
                background-color: white;
                font-size: 10pt;
                
            }
            
            
        """)

        self.setLayout(layout)

        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.singleClickAction)

        self.click_count = 0

    def singleClickAction(self):
        self.click_count = 0  # Reset click count

    def mousePressEvent(self, event):
        self.click_count += 1

        if self.click_count == 1:
            # Start the timer to detect if it's a single click or start of double-click
            self.click_timer.start(250)
        elif self.click_count == 2:
            # If there are two clicks detected before timer expired, then it's a double-click
            self.click_timer.stop()
            self.doubleClickAction()
            self.click_count = 0  # Reset click count
        super().mousePressEvent(event)  # Call base implementation to keep default behaviors intact

    def doubleClickAction(self):
        self.signal_generator_window.show()
        if self.signal_generator_window.isMinimized():
            # If the window is minimized, restore it to its normal size
            self.signal_generator_window.setWindowState(
                self.signal_generator_window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

            # Bring the window to the front and activate it
        self.signal_generator_window.raise_()
        self.signal_generator_window.activateWindow()


    def update_amp_and_freq(self):
        self.node.amplitude = self.amplitude
        self.node.frequency = self.frequency
        self.node.function_type = str(self.fun_type)


class Signal(NodeBase):
    title = 'Signal Generator'
    main_widget_class = SignalWidget
    main_widget_pos = 'between ports'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "Signal Generator.png")
    icon = icon_path
    init_inputs = [
        NodeInputBP(type_='exec'),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    # color = '#adbabd'
    style = 'normal'

    def __init__(self, params):
        super().__init__(params)
        self.amplitude = "1"
        self.frequency = "1"
        self.function_type = 'sin'

        self.fs = self.get_var_val("fs")
        if self.fs is None:
            print("fs from globals")
            self.fs = globals.fs
        
        self.frame_size = self.get_var_val("frame_size")
        if self.frame_size is None:
            print("frame size from globals")
            self.frame_size = globals.frame_size

        self.t = np.arange(self.frame_size) / self.fs

    def update_event(self, inp=-1):
        if inp > -1:
            amp = self.amplitude
            freq = self.frequency

            vars = self.get_vars_manager().variables
            # Creating a dictionary to map v.name to an int/float
            vars_dict = {v.name: float(v.val) if '.' in str(v.val) else int(v.val) for v in vars}

            try:
                # Evaluating amp and freq
                eval_amp = eval(amp, {}, vars_dict)
                eval_freq = eval(freq, {}, vars_dict)

                if not isinstance(eval_amp, (int, float)) or not isinstance(eval_freq, (int, float)):
                    return

            except Exception as e:
                print(e)
                return

            if self.function_type == "sin":
                frame = eval_amp * np.sin(2 * pi * eval_freq * self.t)
                flag = 0
                # flag sign for ZOH plot. init to 0 == no ZOH
                frame = np.append(frame, flag)
                self.set_output_val(0, frame)
            elif self.function_type == "square":
                frame = eval_amp * square(2 * pi * eval_freq * self.t)
                flag = 0
                frame = np.append(frame, flag)
                self.set_output_val(0, frame)

            self.t += self.frame_size / self.fs

    def view_place_event(self):
        self.t = np.arange(self.frame_size) / self.fs
        self.update()

    def get_state(self) -> dict:
        print("get_state called")

        return {
            'amplitude': self.amplitude,
            'frequency': self.frequency,
            'type': self.function_type
        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.amplitude = data['amplitude']
        self.frequency = data['frequency']
        self.function_type = data['type']


nodes = [
    Signal
]
