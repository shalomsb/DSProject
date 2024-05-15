from PySide2.QtCore import QTimer, Qt
from PySide2.QtWidgets import QLayout
import numpy as np
from ryven.NWENV import *
from ryven.NENV import *
from PySide2.QtWidgets import QWidget, QFormLayout, QLineEdit, \
    QDialogButtonBox, QLabel, QVBoxLayout
from PySide2.QtGui import QPixmap, QFont

def is_number(s):
    try:
        float(s)  # Try converting the string to a float
        return True
    except ValueError:
        return False

class NodeBase(Node):
    version = 'v0.1'
    color = '#FF0000'


class GainWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.window = None
        self.gain = self.node.gain

        self.widget_layout = QVBoxLayout()
        self.widget_layout.setContentsMargins(5, 5, 5, 5)  # Set the layout margins to 0
        self.widget_layout.setSizeConstraint(QLayout.SetFixedSize)  # Set the size constraint
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QLabel{
                background-color: white;           
                color: black;
                font-size: 16pt; /* Set font size to 10 for these widgets */
            }       
        """)

        font = QFont()
        font.setPointSize(14)  # Set font size to 24 or any other value you'd like

        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "Gain1.png")
        image = QPixmap(icon_path)
        imageLabel.setPixmap(image)
        imageLabel.setMargin(0)  # Set the margins of the imageLabel to 0
        self.widget_layout.addWidget(imageLabel)

        self.current_gain = QLabel(str(self.gain))
        self.current_gain.setAlignment(Qt.AlignCenter)
        self.widget_layout.addWidget(self.current_gain)
        if not is_number(str(self.gain)):
            print(str(self.gain))
            print(is_number(str(self.gain)))
            self.current_gain.setText("-K-")

        self.setLayout(self.widget_layout)

        self.window = QWidget()
        self.window.setWindowTitle("Gain")

        layout = QFormLayout()
        gain_label = QLabel("Gain:")
        self.gain_field = QLineEdit(str(self.gain))
        # self.gain_field.setValidator(QIntValidator(1, 100000))
        layout.addWidget(gain_label)
        layout.addWidget(self.gain_field)

        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btnBox.accepted.connect(self.ok_callback)
        btnBox.rejected.connect(self.cancel_callback)
        layout.addWidget(btnBox)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")  # Set the text color to red for visibility
        self.error_label.hide()  # Hide it initially

        # Add the error label to the layout
        layout.addWidget(self.error_label)

        self.window.setLayout(layout)

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
        self.window.show()
        if self.window.isMinimized():
            # If the window is minimized, restore it to its normal size
            self.window.setWindowState(self.window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

            # Bring the window to the front and activate it
        self.window.raise_()
        self.window.activateWindow()

    def ok_callback(self):
        isNoError = True
        gain = self.gain_field.text()
        vars = self.node.get_vars_manager().variables
        # Creating a dictionary to map v.name to an int/float
        vars_dict = {v.name: float(v.val) if '.' in str(v.val) else int(v.val) for v in vars}
        
        try:
            # Evaluating gain
            eval_gain = eval(gain, {}, vars_dict)

            if not isinstance(eval_gain, (int, float)):
                self.error_label.setText(f"Error: {gain} is not number")
                self.error_label.show()
                isNoError = False

        except Exception as e:
            self.error_label.setText(f"Error: {gain} not valid")
            self.error_label.show()
            isNoError = False

        # If both amplitude and frequency evaluations were successful, proceed
        if isNoError:
            if is_number(str(gain)):
                self.current_gain.setText(str(gain))
            else:
                self.current_gain.setText("-K-")
            self.node.gain = self.gain_field.text()
            print(self.node.gain)
            print(type(self.node.gain))
            self.window.close()

    def cancel_callback(self):
        self.window.close()


class Gain(NodeBase):
    title = 'Gain'
    main_widget_class = GainWidget
    main_widget_pos = 'between ports'
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    style = 'large'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "Gain1.png")
    icon = icon_path

    def __init__(self, params):
        super().__init__(params)
        self.gain = "1"

    def update_event(self, inp=-1):
        if inp > -1:
            gain = str(self.gain)
            vars = self.get_vars_manager().variables
            # Creating a dictionary to map v.name to an int/float
            vars_dict = {v.name: float(v.val) if '.' in str(v.val) else int(v.val) for v in vars}
            try:
                # Evaluating gain
                eval_gain = eval(gain, {}, vars_dict)
                if not isinstance(eval_gain, (int, float)):
                    print(f"{gain} is not number")
                    return

            except Exception as e:
                print(e)

            frame = self.input(0)
            zoh_flag = frame[-1]
            frame = frame[:-1]
            frame = frame*eval_gain
            frame = np.append(frame, zoh_flag)
            self.set_output_val(0, frame)

    def get_state(self) -> dict:
        print("get_state called")
        return {
            'gain': self.gain,
        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.gain = data['gain']


nodes = [
    Gain,
]
