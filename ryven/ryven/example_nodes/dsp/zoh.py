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


class TryWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        layout.setSizeConstraint(QLayout.SetFixedSize)  # Set the size constraint
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "ZOH.png")
        image = QPixmap(icon_path).scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        # layout.addWidget(QLineEdit("Zero Order Hold"))
        self.setLayout(layout)


class ZOH(NodeBase):
    title = 'zoh'
    style = 'large'
    main_widget_class = TryWidget
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "ZOH.png")
    icon = icon_path
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

    def update_event(self, inp=-1):

        # if inp == 0:
        frame = self.input(0)
        if frame[-1] == 0:
            frame[-1] = 1
        self.set_output_val(0, frame)


nodes = [
    ZOH
]
