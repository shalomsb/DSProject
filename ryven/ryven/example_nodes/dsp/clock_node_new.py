from ryven.NENV import *
from ryven.NWENV import *
from qtpy.QtWidgets import QPushButton, QWidget, QVBoxLayout, QMainWindow, QLabel, QComboBox, QDialogButtonBox
from qtpy.QtGui import QPixmap, QIcon
from qtpy.QtCore import Qt
import globals


# widgets = import_widgets(__file__)


class NodeBase(Node):
    version = 'v0.1'
    color = '#FFCA00'


class ClockNode_MainWidget(MWB, QWidget):

    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        layout = QVBoxLayout()
        # window_button = QPushButton()
        # window_button.clicked.connect(self.show_window)
        # self.setStyleSheet("background-color: white;")  # Set background color to white

        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "my setting.png")
        image = QPixmap(icon_path).scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        # Add the following line to set the background color to white
        imageLabel.setStyleSheet("background-color: white;")
        layout.addWidget(imageLabel)

        self.is_play_icon = True
        self.button1 = QPushButton()
        self.play_icon_path = os.path.join(script_dir, "icons", "play.png")  # Path to your button icon
        self.pause_icon_path = os.path.join(script_dir, "icons", "pause.png")  # Path to your button icon
        button_icon = QIcon(self.play_icon_path)
        self.button1.setIcon(button_icon)
        self.button1.setStyleSheet("background-color: white;")
        self.button1.clicked.connect(self.node.toggle)
        # layout.addWidget(window_button)
        layout.addWidget(self.button1)
        self.setLayout(layout)

        # Parameters Window
        self.parameters_window = QMainWindow()
        self.parameters_window.setWindowTitle("Set Simulation Parameters")

        parameters_layout = QVBoxLayout()

        parameters_layout.addWidget(QLabel("Select frame size:"))
        self.select_box_frame_size = QComboBox()
        self.select_box_frame_size.addItems(["64", "128", "256", "512", "1024", "2048", "4096"])
        self.select_box_frame_size.setCurrentText(str(globals.frame_size))
        parameters_layout.addWidget(self.select_box_frame_size)

        parameters_layout.addWidget(QLabel("Select sampling frequncey:"))
        self.select_fs_size = QComboBox()
        self.select_fs_size.addItems(["8000Hz", "16000Hz", "32000Hz", "48000Hz"])
        self.select_fs_size.setCurrentText(str(globals.fs) + "Hz")
        parameters_layout.addWidget(self.select_fs_size)

        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btnBox.accepted.connect(self.ok_callback)
        btnBox.rejected.connect(self.cancel_callback)
        parameters_layout.addWidget(btnBox)

        parameters_widget = QWidget()
        parameters_widget.setLayout(parameters_layout)
        self.parameters_window.setCentralWidget(parameters_widget)

        self.setLayout(layout)

    def ok_callback(self):
        globals.locked_setting = True
        globals.frame_size_or_fs_change = True
        globals.frame_size = int(self.select_box_frame_size.currentText())
        globals.fs = int(self.select_fs_size.currentText().replace("Hz", ""))
        self.parameters_window.close()

    def cancel_callback(self):
        self.parameters_window.close()

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        if not globals.locked_setting:
            self.parameters_window.show()

    def changeIcon(self):
        if self.is_play_icon:
            button_icon = QIcon(self.pause_icon_path)
            self.is_play_icon = False
        else:
            button_icon = QIcon(self.play_icon_path)
            self.is_play_icon = True
        self.button1.setIcon(button_icon)




class Clock_Node1(NodeBase):
    title = 'clock_new'
    version = 'v0.1'
    init_inputs = [
        # NodeInputBP(dtype=dtypes.Float(default=0.16), label='delay'),
        # NodeInputBP(dtype=dtypes.Float(default=globals.frame_size/globals.fs), label='delay'),
        NodeInputBP(dtype=dtypes.Integer(default=-1, bounds=(-1, 1000)), label='iterations'),
    ]
    init_outputs = [
        NodeOutputBP(type_='exec')
    ]
    color = '#5d95de'
    main_widget_class = ClockNode_MainWidget
    main_widget_pos = 'below ports'

    def __init__(self, params):
        super().__init__(params)

        self.actions['start'] = {'method': self.start}
        self.actions['stop'] = {'method': self.stop}

        if self.session.gui:
            from qtpy.QtCore import QTimer
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.timeouted)
            self.iteration = 0


    def timeouted(self):
        # if globals.stop_timer:
        #     self.stop()
        if globals.stop_timer:
            return
        self.exec_output(0)
        self.iteration += 1
        if -1 < self.input(0) <= self.iteration:
            self.stop()

    def start(self):
        if self.session.gui:
            # self.timer.setInterval(self.input(0) * 1000)
            self.timer.setInterval(globals.frame_size/globals.fs * 1000 * 0.94)
            self.timer.start()
        else:
            import time
            for i in range(self.input(0)):
                self.exec_output(0)
                time.sleep(globals.frame_size/globals.fs)

    def stop(self):
        self.iteration = 0
        if self.session.gui:
            self.timer.stop()

    def toggle(self):
        # triggered from main widget
        globals.stop_timer = False
        self.main_widget().changeIcon()
        # globals.locked_setting = True
        if self.session.gui:
            if self.timer.isActive():
                self.stop()
                # globals.locked_setting = False
            else:
                self.start()


    def update_event(self, inp=-1):
        if self.session.gui:
            self.timer.setInterval(globals.frame_size/globals.fs * 1000 * 0.94)

    def remove_event(self):
        self.stop()


nodes = [
    Clock_Node1,
]
