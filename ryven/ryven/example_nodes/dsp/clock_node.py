from ryven.NENV import *
from ryven.NWENV import *
from qtpy.QtWidgets import QPushButton
import globals


class NodeBase(Node):
    version = 'v0.1'
    color = '#FFCA00'


class ClockNode_MainWidget(MWB, QPushButton):

    def __init__(self, params):
        MWB.__init__(self, params)
        QPushButton.__init__(self)

        self.clicked.connect(self.node.toggle)


class Clock_Node(NodeBase):
    title = 'clock'
    version = 'v0.1'
    init_inputs = [
        NodeInputBP(dtype=dtypes.Float(default=0.016), label='delay'),
        NodeInputBP(dtype=dtypes.Integer(default=-1, bounds=(-1, 1000)), label='iterations'),
    ]
    init_outputs = [
        NodeOutputBP(type_='exec')
    ]
    color = '#5d95de'
    style = 'large'
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
        if -1 < self.input(1) <= self.iteration:
            self.stop()

    def start(self):
        if self.session.gui:
            # self.timer.setInterval(self.input(0) * 1000)
            self.timer.setInterval(1)
            self.timer.start()
        else:
            import time
            for i in range(self.input(1)):
                self.exec_output(0)
                time.sleep(self.input(0))

    def stop(self):
        self.iteration = 0
        if self.session.gui:
            self.timer.stop()

    def toggle(self):
        # triggered from main widget
        globals.stop_timer = False
        if self.session.gui:
            if self.timer.isActive():
                self.stop()
            else:
                self.start()

    def update_event(self, inp=-1):
        if self.session.gui:
            # self.timer.setInterval(self.input(0) * 1000)
            self.timer.setInterval(1)


    def remove_event(self):
        self.stop()

nodes = [
    Clock_Node,
]


