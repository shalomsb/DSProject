from PySide2.QtCore import QTimer, QSize
from PySide2.QtWidgets import QGroupBox
from numpy import pi, sin
import numpy as np
from ryven.NWENV import *
from ryven.NENV import *
from qtpy.QtWidgets import QWidget, QFormLayout, QComboBox, QLineEdit, \
    QDialogButtonBox, QLabel, QVBoxLayout
from qtpy.QtGui import QPixmap, QIntValidator, QDoubleValidator
from scipy.signal import square
from math import sin, pi
from qtpy.QtCore import Qt
import os
import globals
# import importlib


class NodeBase(Node):
    version = 'v0.1'
    color = '#FFCA00'


class A_Law_Compressor_Widget(MWB, QWidget):
    def __init__(self, params):
        try:
            MWB.__init__(self, params)
            QWidget.__init__(self)
            self.window = None
            self.A_value = self.node.A_value
            self.Peak_signal_magnitude = self.node.Peak_signal_magnitude

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
            imageLabel = QLabel()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "icons", "A Low Compressor.png")
            image = QPixmap(icon_path)
            imageLabel.setPixmap(image)
            layout.addWidget(imageLabel)
            # layout.addWidget(QLineEdit("Quantizer"))
            self.setLayout(layout)

            self.window = QWidget()
            self.window.setWindowTitle("Block Parameters: A-Law Compressor")
            self.window.setWindowIcon(image)

            quantizerGroupBox = QGroupBox()
            quantizerGroupBox.setTitle("A-Law Compressor (mask)")
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Compress the input signal using A-law compression.\n\nThis block processes each element independently."))
            quantizerGroupBox.setLayout(layout)

            parametersGroupBox = QGroupBox()
            parametersGroupBox.setTitle("Parameters")
            layout = QVBoxLayout()
            layout.addWidget(QLabel("A value:"))
            self.A_value_edit = QLineEdit(str(self.A_value))
            self.A_value_edit.setValidator(QDoubleValidator(1.0, 100.0, 2))
            layout.addWidget(self.A_value_edit)
            layout.addWidget(QLabel("Peak signal magnitude:"))
            self.Peak_signal_magnitude_edit = QLineEdit(str(self.Peak_signal_magnitude))
            self.Peak_signal_magnitude_edit.setValidator(QDoubleValidator(1.0, 100.0, 2))
            layout.addWidget(self.Peak_signal_magnitude_edit)
            parametersGroupBox.setLayout(layout)

            layout = QVBoxLayout()
            layout.addWidget(quantizerGroupBox)
            layout.addWidget(parametersGroupBox)

            btnBox = QDialogButtonBox()
            btnBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
            btnBox.accepted.connect(self.ok_callback)
            btnBox.rejected.connect(self.cancel_callback)

            layout.addWidget(btnBox)

            # Set the style for the window and widgets
            self.window.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    font-size: 10pt;
                }
                QGroupBox {
                    margin-top: 6px;
                    border: 1px solid gray;
                    border-radius: 4px;
                }
                QGroupBox:title {
                    subcontrol-origin: margin;
                    left: 7px;
                    padding: 0 3px 0 3px;
                }
                QLabel {
                    margin-bottom: 4px;
                    color: black;
                }
                QLineEdit {
                    border: 1px solid gray;
                    border-radius: 2px;
                    color: black;
                    background-color: white;
                }
                QDialogButtonBox QPushButton {
                    background-color: white;
                    color: black; /* Removed comma here */
                }
            """)

            self.window.setMinimumSize(QSize(350, 300))  # Adjust the size as needed
            layout.setSpacing(10)  # Adjust the spacing as needed
            layout.setContentsMargins(10, 10, 10, 10)  # Adjust the margins as needed

            self.window.setLayout(layout)
            self.click_timer = QTimer(self)
            self.click_timer.setSingleShot(True)
            self.click_timer.timeout.connect(self.singleClickAction)

            self.click_count = 0
        except Exception as e:
            print(e)

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
        self.window.show()
        if self.window.isMinimized():
            # If the window is minimized, restore it to its normal size
            self.window.setWindowState(self.signal_generator_window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

            # Bring the window to the front and activate it
        self.window.raise_()
        self.window.activateWindow()

    def ok_callback(self):
        self.window.close()


    def cancel_callback(self):
        self.window.close()


def a_law_compression(frame, a_value, peak_signal_magnitude):
    # Normalizing the frame based on Peak signal magnitude
    normalized_frame = frame / peak_signal_magnitude

    # Applying A-law compression
    compressed_signal = np.zeros_like(normalized_frame, dtype=np.float32)
    abs_normalized_frame = np.abs(normalized_frame)

    mask = abs_normalized_frame < (1 / a_value)
    compressed_signal[mask] = a_value * abs_normalized_frame[mask] / (1 + np.log(a_value))

    mask = ~mask
    compressed_signal[mask] = (1 + np.log(a_value * abs_normalized_frame[mask])) / (1 + np.log(a_value))

    # Restoring the sign and adjusting back to the original scale
    compressed_signal = np.sign(normalized_frame) * compressed_signal * peak_signal_magnitude
    return compressed_signal


class A_Law_Compressor(NodeBase):
    title = 'A Law Compressor'
    style = 'large'
    main_widget_class = A_Law_Compressor_Widget
    main_widget_pos = 'between ports'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "A Low Compressor.png")
    icon = icon_path
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params)
        self.A_value = 87.6
        self.Peak_signal_magnitude = 1

    def update_event(self, inp=-1):

        if inp == 0:
            frame = self.input(0)
            zoh_flag = frame[-1]
            frame = frame[:-1]
            compress_signal = a_law_compression(frame, self.A_value, self.Peak_signal_magnitude)
            result = np.append(compress_signal, zoh_flag)
            self.set_output_val(0, result)

    def get_state(self) -> dict:
        return {
            'A_value': self.A_value,
            'Peak_signal_magnitude': self.Peak_signal_magnitude
        }

    def set_state(self, data: dict, version):
        self.A_value = data['A_value']
        self.Peak_signal_magnitude = data['Peak_signal_magnitude']

class A_Law_Expander_Widget(MWB, QWidget):
    def __init__(self, params):
        try:
            MWB.__init__(self, params)
            QWidget.__init__(self)
            self.window = None
            self.A_value = self.node.A_value
            self.Peak_signal_magnitude = self.node.Peak_signal_magnitude

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
            imageLabel = QLabel()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "icons", "A Low Expander.png")
            image = QPixmap(icon_path)
            imageLabel.setPixmap(image)
            layout.addWidget(imageLabel)
            # layout.addWidget(QLineEdit("Quantizer"))
            self.setLayout(layout)

            self.window = QWidget()
            self.window.setWindowTitle("Block Parameters: A-Low Expander")
            self.window.setWindowIcon(image)

            quantizerGroupBox = QGroupBox()
            quantizerGroupBox.setTitle("A-Low Expander (mask)")
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Expand the signal using inverse A-law compression.\n\nThis block processes each element independently."))
            quantizerGroupBox.setLayout(layout)

            parametersGroupBox = QGroupBox()
            parametersGroupBox.setTitle("Parameters")
            layout = QVBoxLayout()
            layout.addWidget(QLabel("A value:"))
            self.A_value_edit = QLineEdit(str(self.A_value))
            self.A_value_edit.setValidator(QDoubleValidator(1.0, 100.0, 2))
            layout.addWidget(self.A_value_edit)
            layout.addWidget(QLabel("Peak signal magnitude:"))
            self.Peak_signal_magnitude_edit = QLineEdit(str(self.Peak_signal_magnitude))
            self.Peak_signal_magnitude_edit.setValidator(QDoubleValidator(1.0, 100.0, 2))
            layout.addWidget(self.Peak_signal_magnitude_edit)
            parametersGroupBox.setLayout(layout)

            layout = QVBoxLayout()
            layout.addWidget(quantizerGroupBox)
            layout.addWidget(parametersGroupBox)

            btnBox = QDialogButtonBox()
            btnBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
            btnBox.accepted.connect(self.ok_callback)
            btnBox.rejected.connect(self.cancel_callback)

            layout.addWidget(btnBox)

            # Set the style for the window and widgets
            self.window.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    font-size: 10pt;
                }
                QGroupBox {
                    margin-top: 6px;
                    border: 1px solid gray;
                    border-radius: 4px;
                }
                QGroupBox:title {
                    subcontrol-origin: margin;
                    left: 7px;
                    padding: 0 3px 0 3px;
                }
                QLabel {
                    margin-bottom: 4px;
                    color: black;
                }
                QLineEdit {
                    border: 1px solid gray;
                    border-radius: 2px;
                    color: black;
                    background-color: white;
                }
                QDialogButtonBox QPushButton {
                    background-color: white;
                    color: black; /* Removed comma here */
                }
            """)

            self.window.setMinimumSize(QSize(350, 300))  # Adjust the size as needed
            layout.setSpacing(10)  # Adjust the spacing as needed
            layout.setContentsMargins(10, 10, 10, 10)  # Adjust the margins as needed

            self.window.setLayout(layout)
            self.click_timer = QTimer(self)
            self.click_timer.setSingleShot(True)
            self.click_timer.timeout.connect(self.singleClickAction)

            self.click_count = 0
        except Exception as e:
            print(e)

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
        self.window.show()
        if self.window.isMinimized():
            # If the window is minimized, restore it to its normal size
            self.window.setWindowState(self.signal_generator_window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

            # Bring the window to the front and activate it
        self.window.raise_()
        self.window.activateWindow()

    def ok_callback(self):
        self.window.close()


    def cancel_callback(self):
        self.window.close()


def a_law_expander(frame, a_value, peak_signal_magnitude):
    # Normalizing the frame based on Peak signal magnitude
    normalized_frame = frame / peak_signal_magnitude

    # Applying A-law expansion
    expanded_signal = np.zeros_like(normalized_frame, dtype=np.float32)
    abs_normalized_frame = np.abs(normalized_frame)

    mask = abs_normalized_frame < (1 / (1 + np.log(a_value)))
    expanded_signal[mask] = (1 + np.log(a_value)) * abs_normalized_frame[mask] / a_value

    mask = ~mask
    expanded_signal[mask] = np.exp(abs_normalized_frame[mask] * (1 + np.log(a_value)) - 1) / a_value

    # Restoring the sign and adjusting back to the original scale
    expanded_signal = np.sign(normalized_frame) * expanded_signal * peak_signal_magnitude
    return expanded_signal


class A_Law_Expander(NodeBase):
    title = 'A Law Expander'
    style = 'large'
    main_widget_class = A_Law_Expander_Widget
    main_widget_pos = 'between ports'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "A Low Expander.png")
    icon = icon_path
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params)
        self.A_value = 87.6
        self.Peak_signal_magnitude = 1

    def update_event(self, inp=-1):

        if inp == 0:
            frame = self.input(0)
            zoh_flag = frame[-1]
            frame = frame[:-1]
            expand_signal = a_law_expander(frame, self.A_value, self.Peak_signal_magnitude)
            result = np.append(expand_signal, zoh_flag)
            self.set_output_val(0, result)

    def get_state(self) -> dict:
        return {
            'A_value': self.A_value,
            'Peak_signal_magnitude': self.Peak_signal_magnitude
        }

    def set_state(self, data: dict, version):
        self.A_value = data['A_value']
        self.Peak_signal_magnitude = data['Peak_signal_magnitude']


nodes = [
    A_Law_Compressor,
    A_Law_Expander,

]
