from PySide2.QtWidgets import QLayout
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


class NewPlusWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # icon_path = os.path.join(script_dir, "icons", "signal generator.png")
        icon_path = os.path.join(script_dir, "icons", "new_plus.png")
        # image = QPixmap(icon_path).scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image = QPixmap(icon_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        self.setLayout(layout)


class NewPlus(NodeBase):
    title = 'Plus'
    style = 'large'
    main_widget_class = NewPlusWidget
    main_widget_pos = 'between ports'
    init_inputs = [
        NodeInputBP(),
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    color = '#5d95de'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "new_plus.png")
    icon = icon_path

    def __init__(self, params):
        super().__init__(params)

    def update_event(self, inp=-1):

        if inp == 1:
            data1 = self.input(0)
            data2 = self.input(1)
            data1 = data1[:-1]
            data2 = data2[:-1]
            result = data1 + data2
            result = np.append(result, 0)
            self.set_output_val(0, result)





nodes = [
    NewPlus,
]
