from PySide2.QtCore import QTimer
from numpy import pi, sin
import numpy as np
from ryven.NWENV import *
from ryven.NENV import *
from qtpy.QtWidgets import QWidget, QFormLayout, QComboBox, QLineEdit, \
    QDialogButtonBox, QLabel, QVBoxLayout, QBoxLayout, QLayout
from qtpy.QtGui import QPixmap, QIntValidator, QFont
from scipy.signal import square
from math import sin, pi
from qtpy.QtCore import Qt
import os
import globals



class NodeBase(Node):
    version = 'v0.1'
    color = '#FF0000'


class Int16Widget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        layout.setSizeConstraint(QLayout.SetFixedSize)  # Set the size constraint
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "convert.png")
        image = QPixmap(icon_path)
        imageLabel.setPixmap(image)
        imageLabel.setMargin(0)  # Set the margins of the imageLabel to 0
        layout.addWidget(imageLabel)

        self.currentDataTypeComboBox = QComboBox()
        # self.currentDataTypeComboBox.setMaximumWidth(100)
        self.currentDataTypeComboBox.addItems(["int8", "int16", "float", "double"])
        self.currentDataTypeComboBox.setCurrentText(self.node.currentDataType)
        self.currentDataTypeComboBox.currentIndexChanged.connect(self.currentDataTypeCange)
        layout.addWidget(self.currentDataTypeComboBox)

        # layout.addWidget(label)
        self.setLayout(layout)
        self.setStyleSheet("background-color: white; color: black; font-size: 10pt;")
    
    def currentDataTypeCange(self):
        self.node.currentDataType = self.currentDataTypeComboBox.currentText()


class ToInt16(NodeBase):
    title = 'Convert Type'
    main_widget_class = Int16Widget
    main_widget_pos = 'between ports'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "convert.png")
    icon = icon_path
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    # color = '#5d95de'
    style = 'large'

    def __init__(self, params):
        super().__init__(params)
        self.currentDataType = "int16"

    def update_event(self, inp=-1):
        if inp > -1:
            frame = self.input(0)
            if self.currentDataType == "int16":
                arr_clipped_rounded = np.round(np.clip(frame, -32768, 32767))
                frame = arr_clipped_rounded.astype(np.int16)
            elif self.currentDataType == "int8":
                arr_clipped_rounded = np.round(np.clip(frame, -128, 127))
                frame = arr_clipped_rounded.astype(np.int8)
            elif self.currentDataType == "float":
                # No clipping, direct conversion to float32
                frame = frame.astype(np.float32)
            elif self.currentDataType == "double":
                # No clipping, direct conversion to float64
                frame = frame.astype(np.float64)

            self.set_output_val(0, frame)


class DoubleWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        layout = QVBoxLayout()

        label = QLabel("double")

        # Set the font to be bolder and larger
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)  # Adjust the size as needed
        label.setFont(font)

        # Set the text color to red
        label.setStyleSheet("color: red;")
        self.setStyleSheet("background-color: #adbabd")

        layout.addWidget(label)
        self.setLayout(layout)


class ToDouble(NodeBase):
    title = 'double'
    main_widget_class = DoubleWidget
    main_widget_pos = 'between ports'
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    # color = '#5d95de'
    style = 'large'

    def __init__(self, params):
        super().__init__(params)


    def update_event(self, inp=-1):
        if inp > -1:
            frame = self.input(0)
            # Clip values to be within int16 range and then round
            double_array = frame.astype(np.float64)
            self.set_output_val(0, double_array)


nodes = [
    ToInt16,
    # ToDouble,
]
