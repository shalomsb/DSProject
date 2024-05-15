from PySide2.QtCore import QTimer, QSize
from PySide2.QtWidgets import QGroupBox
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


class QuantizerWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.window = None
        self.N_parameter = self.node.N_parameter

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "icons8-stairs-100.png")
        image = QPixmap(icon_path)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        # layout.addWidget(QLineEdit("Quantizer"))
        self.setLayout(layout)

        self.window = QWidget()
        self.window.setWindowTitle("Block Parameters: Quantizer")
        self.window.setWindowIcon(image)

        quantizerGroupBox = QGroupBox()
        quantizerGroupBox.setTitle("Quantizer")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Discretize input at given interval."))
        quantizerGroupBox.setLayout(layout)

        parametersGroupBox = QGroupBox()
        parametersGroupBox.setTitle("Parameters")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Quantization interval:"))
        layout.addWidget(QLabel("For power enter '**'!"))
        self.N = QLineEdit(str(self.N_parameter))
        # self.N.setValidator(QIntValidator(1, 100))
        layout.addWidget(self.N)
        parametersGroupBox.setLayout(layout)

        # quantization_interval_label = QLabel("Quantization interval:\nSelect N")
        # self.quantization_interval = QLineEdit(str(self.N_parameter))
        # self.quantization_interval.setValidator(QIntValidator(1, 10000))
        layout = QVBoxLayout()
        # layout.addWidget(quantization_interval_label)
        # layout.addWidget(self.quantization_interval)
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
        try:
            vars = self.node.get_vars_manager().variables
            # Creating a dictionary to map v.name to an int/float
            vars_dict = {v.name: float(v.val) if '.' in str(v.val) else int(v.val) for v in vars}
            n = self.N.text()
            try:
                n_eval = eval(n, {}, vars_dict)
                if not isinstance(n_eval, (int, float)):
                    return
            except Exception as e:
                print(e)
                return
            self.N_parameter = n
            self.node.N_parameter = n
            self.window.close()
        except Exception as e:
            print(e)

    def cancel_callback(self):
        self.window.close()



class Quantizer(NodeBase):
    title = 'Quantizer'
    style = 'large'
    main_widget_class = QuantizerWidget
    main_widget_pos = 'between ports'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "icons8-stairs-100.png")
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
        self.N_parameter = "1"

    def update_event(self, inp=-1):

        if inp == 0:
            frame = self.input(0)
            zoh_flag = frame[-1]
            frame = frame[:-1]
            vars = self.get_vars_manager().variables
            # Creating a dictionary to map v.name to an int/float
            vars_dict = {v.name: float(v.val) if '.' in str(v.val) else int(v.val) for v in vars}
            n = self.N_parameter
            try:
                n_eval = eval(n, {}, vars_dict)
                if not isinstance(n_eval, (int, float)):
                    return
            except Exception as e:
                print(e)
                return
            quantized_signal = self.quantize(frame, n_eval)
            quantized_signal = np.append(quantized_signal, zoh_flag)
            self.set_output_val(0, quantized_signal)

    def quantize(self, signal, quant_factor):
        """Quantizes the input signal based on the given step size."""
        # quant_factor = 2/(2**quant_factor)

        return np.round(signal / quant_factor) * quant_factor

    def get_state(self) -> dict:
        return {
            'N_parameter': self.N_parameter,
        }

    def set_state(self, data: dict, version):
        self.N_parameter = data['N_parameter']


nodes = [
    Quantizer
]
