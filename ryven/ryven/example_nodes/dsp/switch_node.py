from PySide2.QtCore import QTimer
from ryven.NWENV import *
from ryven.NENV import *
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout
from qtpy.QtGui import QPixmap
from qtpy.QtCore import Qt

import os


class TryWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0

        self.imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.up_switch_icon_path = os.path.join(script_dir, "icons", "up_switch.png")
        self.down_switch_icon_path = os.path.join(script_dir, "icons", "down_switch.png")
        self.current_image = QPixmap(self.up_switch_icon_path).scaled(100, 100, Qt.KeepAspectRatio,
                                                                      Qt.SmoothTransformation)

        self.imageLabel.setPixmap(self.current_image)
        self.layout.addWidget(self.imageLabel)

        self.setLayout(self.layout)

        self.is_down = False

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
        if not self.is_down:
            self.current_image = QPixmap(self.down_switch_icon_path).scaled(100, 100, Qt.KeepAspectRatio,
                                                                            Qt.SmoothTransformation)
            self.is_down = True
        else:
            self.current_image = QPixmap(self.up_switch_icon_path).scaled(100, 100, Qt.KeepAspectRatio,
                                                                          Qt.SmoothTransformation)
            self.is_down = False

        self.imageLabel.setPixmap(self.current_image)

    def get_icon(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "up_switch.png")
        return QPixmap(icon_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)



    # def mousePressEvent(self, event):
    #     pass
    #
    # def mouseDoubleClickEvent(self, event):
    #     if not self.is_down:
    #         self.current_image = QPixmap(self.down_switch_icon_path).scaled(120, 160, Qt.KeepAspectRatio,
    #                                                                         Qt.SmoothTransformation)
    #         self.is_down = True
    #     else:
    #         self.current_image = QPixmap(self.up_switch_icon_path).scaled(120, 160, Qt.KeepAspectRatio,
    #                                                                       Qt.SmoothTransformation)
    #         self.is_down = False
    #
    #     self.imageLabel.setPixmap(self.current_image)

    def return_current_inputs(self):
        if not self.is_down:
            return 0
        else:
            return 1


class Switch_Node(Node):
    title = 'Switch'
    main_widget_class = TryWidget
    main_widget_pos = 'between ports'
    style = "large"
    description = 'A manual switch node for switching between two inputs'
    init_inputs = [
        NodeInputBP(),
        NodeInputBP(),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "up_switch.png")
    icon = icon_path

    def __init__(self, params):
        super().__init__(params)
        # self.icon = self.main_widget_class.get_icon()

    def update_event(self, inp=-1):
        data1 = self.input(0)
        data2 = self.input(1)
        current_input = self.main_widget().return_current_inputs()

        if inp == 1:
            if current_input == 0:
                if data1 is not None:
                    self.set_output_val(0, data1)
                else:
                    self.set_output_val(0, None)
            else:
                if data2 is not None:
                    self.set_output_val(0, data2)
                else:
                    self.set_output_val(0, None)


nodes = [
    Switch_Node
]
