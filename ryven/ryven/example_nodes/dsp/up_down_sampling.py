from PySide2.QtCore import QTimer
from numpy import pi, sin
import numpy as np
from ryven.NWENV import *
from ryven.NENV import *
from qtpy.QtWidgets import QWidget, QFormLayout, QComboBox, QLineEdit, \
    QDialogButtonBox, QLabel, QVBoxLayout
from qtpy.QtGui import QPixmap, QIntValidator
from scipy.signal import square
from math import sin, pi
from qtpy.QtCore import Qt
import os
import globals
# import importlib


class NodeBase(Node):
    version = 'v0.1'
    color = '#FFCA00'


class DownSamplingWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.window = None

        layout = QVBoxLayout()
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "downsampling1.png")
        image = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        self.down_factor = self.node.step_size
        self.factor_label = QLabel(str(self.down_factor))
        self.factor_label.setAlignment(Qt.AlignCenter)
        self.factor_label.setStyleSheet("""
        QLabel {
                                background-color: white;
                                color: black;
                                font-size: 20pt;
                            }
                            QWidget{
                background-color: white;
                } 
        """)

        layout.addWidget(self.factor_label)
        self.setLayout(layout)

        self.window = QWidget()
        self.window.setWindowTitle("Block Parameters: Down Sampling")
        self.window.setWindowIcon(image)
        down_sampling_factor_label = QLabel("Down Sampling Factor:")
        self.down_sampling_factor = QLineEdit(str(self.down_factor))
        self.down_sampling_factor.setValidator(QIntValidator(1, 10))
        layout = QFormLayout()
        layout.addWidget(down_sampling_factor_label)
        layout.addWidget(self.down_sampling_factor)

        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btnBox.accepted.connect(self.ok_callback)
        btnBox.rejected.connect(self.cancel_callback)

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

    def ok_callback(self):
        try:
            self.down_factor = int(self.down_sampling_factor.text())
            self.factor_label.setText(str(self.down_factor))
            self.node.step_size = int(self.down_sampling_factor.text())
            self.window.close()
        except Exception as e:
            print(e)

    def cancel_callback(self):
        self.window.close()



class DownSampling(NodeBase):
    title = 'Down Sampling'
    style = 'large'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "downsampling1.png")
    icon = icon_path
    main_widget_class = DownSamplingWidget
    main_widget_pos = 'between ports'
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params)
        self.step_size = 2

    def update_event(self, inp=-1):

        if inp == 0:
            frame = self.input(0)
            zoh_flag = frame[-1]
            frame = frame[:-1]
            down_sample_signal = frame[::self.step_size]
            down_sample_signal = np.append(down_sample_signal, zoh_flag)
            self.set_output_val(0, down_sample_signal)

    def get_state(self) -> dict:
        print("get_state called")
        print(self.step_size)

        return {
            'factor': self.step_size,
        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.step_size = data['factor']
        print(data['factor'])

class UpSamplingWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.window = None

        layout = QVBoxLayout()
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "upsampling1.png")
        image = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        self.up_factor = self.node.step_size
        self.factor_label = QLabel(str(self.up_factor))
        self.factor_label.setAlignment(Qt.AlignCenter)
        self.factor_label.setStyleSheet("""
                QLabel {
                                        background-color: white;
                                        color: black;
                                        font-size: 20pt;
                                    }
                QWidget{
                background-color: white;
                }                    
                """)

        layout.addWidget(self.factor_label)

        self.setLayout(layout)

        self.window = QWidget()
        self.window.setWindowTitle("Block Parameters: Up Sampling")
        self.window.setWindowIcon(image)
        up_sampling_factor_label = QLabel("Up Sampling Factor:")
        self.up_sampling_factor = QLineEdit(str(self.up_factor))
        self.up_sampling_factor.setValidator(QIntValidator(1, 10))
        layout = QFormLayout()
        layout.addWidget(up_sampling_factor_label)
        layout.addWidget(self.up_sampling_factor)

        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btnBox.accepted.connect(self.ok_callback)
        btnBox.rejected.connect(self.cancel_callback)

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

    def ok_callback(self):
        try:
            self.up_factor = int(self.up_sampling_factor.text())
            self.factor_label.setText(str(self.up_factor))
            self.node.step_size = int(self.up_sampling_factor.text())
            self.window.close()
        except Exception as e:
            print(e)

    def cancel_callback(self):
        self.window.close()


class UpSampling(NodeBase):
    title = 'Up Sampling'
    style = 'large'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "upsampling1.png")
    icon = icon_path
    main_widget_class = UpSamplingWidget
    main_widget_pos = 'between ports'
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params)
        self.step_size = 2

    def update_event(self, inp=-1):

        if inp == 0:
            frame = self.input(0)
            zoh_flag = frame[-1]
            frame = frame[:-1]
            upsampled_data = np.zeros(len(frame) * self.step_size)
            upsampled_data[::self.step_size] = frame
            up_sample_signal = np.append(upsampled_data, zoh_flag)
            self.set_output_val(0, up_sample_signal)

    def get_state(self) -> dict:
        print("get_state called")
        print(self.step_size)

        return {
            'factor': self.step_size,
        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.step_size = data['factor']
        print(data['factor'])




nodes = [
    DownSampling,
    UpSampling,
]
