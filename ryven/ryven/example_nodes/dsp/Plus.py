from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
from ryven.NENV import *
from ryven.NWENV import *
from qtpy.QtCore import Qt
import numpy as np

# import math

class TryWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        layout = QVBoxLayout()
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # icon_path = os.path.join(script_dir, "icons", "signal generator.png")
        icon_path = os.path.join(script_dir, "icons", "plus.png")
        # image = QPixmap(icon_path).scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        self.setLayout(layout)
class OperatorNodeBase(Node):

    version = 'v0.0'
    main_widget_class = TryWidget
    main_widget_pos = 'between ports'
    init_inputs = [
        # NodeInputBP(dtype=dtypes.Data(size='s')),
        # NodeInputBP(dtype=dtypes.Data(size='s')),
        NodeInputBP(),
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    style = 'large'

    def __init__(self, params):
        super().__init__(params)

        self.num_inputs = 0
        self.actions['add input'] = {'method': self.add_operand_input}

    def place_event(self):
        for i in range(len(self.inputs)):
            self.register_new_operand_input(i)

    def add_operand_input(self):
        self.create_input_dt(dtype=dtypes.Data(size='s'))
        self.register_new_operand_input(self.num_inputs)
        self.update()

    def remove_operand_input(self, index):
        self.delete_input(index)
        self.num_inputs -= 1
        # del self.actions[f'remove input {index}']
        self.rebuild_remove_actions()
        self.update()

    def register_new_operand_input(self, index):
        self.actions[f'remove input {index}'] = {
            'method': self.remove_operand_input,
            'data': index
        }
        self.num_inputs += 1

    def rebuild_remove_actions(self):

        remove_keys = []
        for k, v in self.actions.items():
            if k.startswith('remove input'):
                remove_keys.append(k)

        for k in remove_keys:
            del self.actions[k]

        for i in range(self.num_inputs):
            self.actions[f'remove input {i}'] = {'method': self.remove_operand_input, 'data': i}

    def update_event(self, inp=-1):
        self.set_output_val(0, self.apply_op([self.input(i) for i in range(len(self.inputs))]))

    def apply_op(self, elements: list):
        return None

class ArithmeticNodeBase(OperatorNodeBase):
    color = '#58db53'


class Plus_Node(ArithmeticNodeBase):
    title = 'plus'

    def apply_op(self, elements: list):
        # v = elements[0]
        # for e in elements[1:]:
        #     v = v + e
        # return v
        # # return sum(elements)

        e1 = elements[0]
        e2 = elements[1]
        e1 = e1[:-1]
        e2 = e2[:-1]

        result = e1 + e2
        result = np.append(result, 0)
        print(len(result))
        print(result.dtype)
        return result

nodes = [
    Plus_Node,
]