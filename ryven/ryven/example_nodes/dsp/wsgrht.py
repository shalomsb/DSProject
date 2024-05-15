from ryven.NWENV import *
from ryven.NENV import *
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout


class TempNodeWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        label = QLabel()
        label.setText("Temp Node")
        layout.addWidget(label)
        self.setLayout(layout)


class TempNode(Node):
    main_widget_class = TempNodeWidget
    main_widget_pos = 'between ports'
    style = "large"
    title = 'Temp'

    init_inputs = [
        NodeInputBP(),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]

    def __init__(self, params):
        super().__init__(params)

    def update_event(self, inp=-1):
        if inp == 0:
            frame = self.input(0)
            self.set_output_val(0, frame)


nodes = [
    TempNode,
]
