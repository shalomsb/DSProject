from PySide2.QtCore import QTimer
from numpy import pi, sin
import numpy as np
from ryven.NWENV import *
from ryven.NENV import *
from qtpy.QtWidgets import QWidget, QFormLayout, QComboBox, QLineEdit, \
    QDialogButtonBox, QLabel, QVBoxLayout, QBoxLayout, QSlider
from qtpy.QtGui import QPixmap, QIntValidator, QFont
from scipy.signal import square
from math import sin, pi
from qtpy.QtCore import Qt
import os
import globals



class NodeBase(Node):
    version = 'v0.1'
    color = '#FF0000'


class TryWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.window = None

        self.amp = self.node.amplitude
        self.freq = self.node.frequency
        self.fun_type = str(self.node.function_type)

        self.amp_field = 1
        self.freq_field = 1
        self.type_field = None

        layout = QVBoxLayout()

        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # icon_path = os.path.join(script_dir, "icons", "signal generator.png")
        icon_path = os.path.join(script_dir, "icons", "Signal Generator.png")
        # image = QPixmap(icon_path).scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image = QPixmap(icon_path).scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)

        label = QLabel("Signal Generator")
        font = QFont()
        font.setPointSize(14)  # Set font size to 20 or another desired value
        label.setFont(font)
        layout.addWidget(label)
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setMinimum(1)
        self.freq_slider.setMaximum(10000)
        if self.freq is not None:
            self.freq_slider.setValue(int(self.freq))  # Set initial value to match self.freq
        self.freq_slider.valueChanged.connect(self.update_freq_field)
        self.current_freq = QLabel(str(self.freq))

        # Add the slider to the layout
        layout.addWidget(QLabel("Frequency Slider:"))
        layout.addWidget(self.freq_slider)
        layout.addWidget(self.current_freq)

        self.amp_slider = QSlider(Qt.Horizontal)
        self.amp_slider.setMinimum(1)
        self.amp_slider.setMaximum(5000)
        if self.amp is not None:
            self.amp_slider.setValue(int(self.amp))  # Set initial value to match self.amp
        self.amp_slider.valueChanged.connect(self.update_amp_field)
        self.current_amp = QLabel(str(self.amp))

        # Add the slider to the layout
        layout.addWidget(QLabel("Amplitude Slider:"))
        layout.addWidget(self.amp_slider)
        layout.addWidget(self.current_amp)

        self.setLayout(layout)

        self.window = QWidget()
        self.window.setWindowTitle("Signal Generator")
        self.window.setWindowIcon(image)
        amp_label = QLabel("Amplitude:")
        self.amp_field = QLineEdit(str(self.amp))
        self.amp_field.setValidator(QIntValidator(1, 10000))

        freq_label = QLabel("Frequency (Hz):")
        self.freq_field = QLineEdit(str(self.freq))
        self.freq_field.setValidator(QIntValidator(1, 10000))

        type_label = QLabel("Signal type:")
        self.type_field = QComboBox()
        self.type_field.addItem('sin')
        self.type_field.addItem('square')
        self.type_field.setCurrentText(str(self.fun_type))

        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btnBox.accepted.connect(self.ok_callback)
        btnBox.rejected.connect(self.cancel_callback)

        # Set layout
        layout = QFormLayout()
        layout.addWidget(QLabel("Signal Generator"))
        layout.addWidget(QLabel("Output various wave forms:"))
        layout.addWidget(QLabel("  Y(t) = Amp*Waveform(Freq, t)"))
        layout.addWidget(QLabel("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _"))
        layout.addWidget(QLabel("Parameters"))
        layout.addWidget(type_label)
        layout.addWidget(self.type_field)
        layout.addWidget(amp_label)
        layout.addWidget(self.amp_field)
        layout.addWidget(freq_label)
        layout.addWidget(self.freq_field)
        layout.addWidget(btnBox)

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

    def get_amp(self):
        return self.amp

    def get_freq(self):
        return self.freq

    def get_type(self):
        return self.fun_type

    # def mousePressEvent(self, event):
    #     pass
    #
    # def mouseDoubleClickEvent(self, event):
    #     self.window.show()

    def window1(self):
        self.window.show()

    def ok_callback(self):
        self.fun_type = self.type_field.currentText()
        self.node.function_type = self.type_field.currentText()
        self.amp = int(self.amp_field.text())
        self.amp_slider.setValue(int(self.amp_field.text()))
        self.node.amplitude = int(self.amp_field.text())
        self.freq = int(self.freq_field.text())
        self.freq_slider.setValue(int(self.freq_field.text()))
        self.node.frequency = int(self.freq_field.text())
        self.window.close()

    def update_freq_field(self, value):
        self.freq_field.setText(str(value))
        self.freq = int(self.freq_field.text())
        self.node.frequency = int(self.freq_field.text())
        self.current_freq.setText(str(value))  # Updating the label text

    def update_amp_field(self, value):
        self.amp_field.setText(str(value))
        self.amp = int(self.amp_field.text())
        self.node.amplitude = int(self.amp_field.text())
        self.current_amp.setText(str(value))  # Updating the label text


    def cancel_callback(self):
        self.window.close()


class Sin(NodeBase):
    title = 'Signal Generator'
    main_widget_class = TryWidget
    main_widget_pos = 'below ports'
    init_inputs = [
        NodeInputBP(type_='exec'),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    # color = '#5d95de'
    style = 'large'

    def __init__(self, params):
        super().__init__(params)
        self.amplitude = 1
        self.frequency = 1
        self.function_type = 'sin'
        self.samples_vector = np.array([])
        # self.t = np.arange(globals.frame_size) / 16000
        self.t = np.arange(globals.frame_size) / globals.fs
        # self.first_time = True

    def update_event(self, inp=-1):
        # self.amplitude = self.main_widget().get_amp()
        # self.frequency = self.main_widget().get_freq()
        # self.function_type = self.main_widget().get_type()

        if inp > -1:
            if globals.frame_size_or_fs_change:
                globals.frame_size_or_fs_change = False

                self.t = np.arange(globals.frame_size) / globals.fs
                print(len(self.t))
            if self.function_type == "sin":
                frame = self.amplitude * np.sin(2 * pi * self.frequency * self.t)
                flag = 0
                frame = np.append(frame, flag)
                self.set_output_val(0, frame)
            if self.function_type == "square":
                self.set_output_val(0, self.amplitude * square(2 * pi * self.frequency * self.t))

            self.t += globals.frame_size / globals.fs

    def view_place_event(self):
        # importlib.reload(globals)
        self.t = np.arange(globals.frame_size) / globals.fs
        print(len(self.t))
        self.update()


    def get_state(self) -> dict:
        print("get_state called")
        print(self.amplitude)
        print(self.frequency)
        print(self.function_type)
        return {
            'amp': self.amplitude,
            'freq': self.frequency,
            'type': self.function_type
        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.amplitude = data['amp']
        self.frequency = data['freq']
        self.function_type = data['type']

        print(data['amp'])
        print(data['freq'])
        print(data['type'])


nodes = [
    Sin
]
