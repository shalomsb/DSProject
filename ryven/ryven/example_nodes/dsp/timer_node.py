from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
from ryven.NENV import *
from ryven.NWENV import *
from qtpy.QtWidgets import QPushButton
from PySide2.QtCore import QTimer
from qtpy.QtCore import Qt
import globals




class NodeBase(Node):
    version = 'v0.1'
    color = '#FFCA00'


class ClockNode_MainWidget(MWB, QWidget):

    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        # Setup the layout
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # Set the layout margins to 0

        # Image (QLabel with QPixmap)
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "timer.png")
        image = QPixmap(icon_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)

        # Button
        self.button = QPushButton("Start", self)
        self.button.clicked.connect(self.node.toggle)
        layout.addWidget(self.button)
        self.setStyleSheet("""
                    QWidget {
                        background-color: white;
                        color: black;
                        font-weight: bold;
                    }
                    QPushButton {
                        background-color: red;
                        color: black;
                        font-weight: bold;  
                    } 
                """)

        self.setLayout(layout)

    def change_color_on(self):
        self.button.setStyleSheet("background-color: green; color: black; font-weight: bold;")
        self.button.setText("Stop")

    def change_color_off(self):
        self.button.setStyleSheet("background-color: red; color: black; font-weight: bold;")
        self.button.setText("Start")

class Timer_Node(NodeBase):
    title = 'timer'
    version = 'v0.1'
    style = 'large'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "timer.png")
    icon = icon_path
    init_inputs = [
    ]
    init_outputs = [
        NodeOutputBP(type_='exec')
    ]
    color = '#5d95de'
    main_widget_class = ClockNode_MainWidget
    main_widget_pos = 'between ports'

    def __init__(self, params):
        super().__init__(params)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_event)
        fs = self.get_var_val("fs")
        if fs is None:
            try:
                # fs = self.create_new_var("fs")
                self.get_vars_manager().create_new_var("fs")
                self.get_vars_manager().set_var("fs", globals.fs)
                fs = self.get_var_val("fs")
                print("fs from globals")
            except Exception as e:
                print(e)
        frame_size = self.get_var_val("frame_size")
        if frame_size is None:
            try:
                # fs = self.create_new_var("fs")
                self.get_vars_manager().create_new_var("frame_size")
                self.get_vars_manager().set_var("frame_size", globals.frame_size)
                frame_size = self.get_var_val("frame_size")
                print("frame_size from globals")
            except Exception as e:
                print(e)
        self.timer.setInterval(frame_size/fs*1000*0.9)  # Set the interval to 1 millisecond

    def toggle(self):
        if self.timer.isActive():
            self.timer.stop()
            self.main_widget().change_color_off()
        else:
            self.timer.start()  # Start the timer with the interval set previously
            self.main_widget().change_color_on()

    def update_event(self):
        self.exec_output(0)


nodes = [
    Timer_Node,
]


