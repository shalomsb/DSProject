from PySide2.QtCore import QTimer, Qt
from PySide2.QtWidgets import QLayout, QSizePolicy
import numpy as np
from ryven.NWENV import *
from ryven.NENV import *
from PySide2.QtWidgets import QWidget, QFormLayout, QComboBox, QLineEdit, \
    QDialogButtonBox, QLabel, QVBoxLayout, QBoxLayout, QSlider
from PySide2.QtGui import QPixmap, QIntValidator, QFont
import os
import globals

# Dictionary to map numbers and minus sign to their superscript equivalents
superscript_map = {
    "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
    "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "0": "⁰",
    "-": "⁻"
}

# Function to convert a number into its superscript form
def to_superscript(n):
    return ''.join(superscript_map.get(digit, '') for digit in str(-n))



class NodeBase(Node):
    version = 'v0.1'
    color = '#FF0000'


class DelayWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.window = None
        self.delay = self.node.delay

        self.widget_layout = QVBoxLayout()
        self.widget_layout.setContentsMargins(5, 5, 5,5)  # Set the layout margins to 0
        self.widget_layout.setSizeConstraint(QLayout.SetFixedSize)  # Set the size constraint

        # self.label = QLabel(f"Delay×{self.delay}")
        #
        # font = QFont()
        # font.setPointSize(20)  # Set font size to 24 or any other value you'd like
        # self.label.setFont(font)
        #
        # self.widget_layout.addWidget(self.label)

        self.delay_slider = QSlider(Qt.Horizontal)
        self.delay_slider.setMinimum(0)
        self.delay_slider.setMaximum(1000)
        self.delay_slider.setValue(int(self.delay))  # Set initial value to match self.freq
        self.delay_slider.setTickPosition(QSlider.TicksBelow)  # Add tick marks below the slider
        self.delay_slider.setTickInterval(10)  # Set tick interval to 1 or any other value you prefer
        self.delay_slider.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # self.delay_slider.setStyleSheet("color: black;background-color: white;font-size: 14pt;")
        self.delay_slider.valueChanged.connect(self.update_delay_field)

        self.current_delay = QLabel(str(self.delay))
        self.current_delay.setAlignment(Qt.AlignCenter)
        # delay_label = QLabel("delay Slider:")
        formatted_string = f"Z{to_superscript(self.delay)}"
        print(formatted_string)
        self.delay_label = QLabel(str(formatted_string))
        self.delay_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(12)  # Set font size to 24 or any other value you'd like
        self.delay_label.setFont(font)
        self.current_delay.setFont(font)
        self.widget_layout.addWidget(self.delay_label)
        self.widget_layout.addWidget(self.delay_slider)
        self.widget_layout.addWidget(self.current_delay)
        self.setStyleSheet("background-color: white; color: black;")

        self.setLayout(self.widget_layout)
        
        self.window = QWidget()
        self.window.setWindowTitle("delay")
    
        layout = QFormLayout()
        delay_label = QLabel("delay:")
        self.delay_field = QLineEdit(str(self.delay))
        self.delay_field.setValidator(QIntValidator(1, 1000))
        layout.addWidget(delay_label)
        layout.addWidget(self.delay_field)
    
        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btnBox.accepted.connect(self.ok_callback)
        btnBox.rejected.connect(self.cancel_callback)
        layout.addWidget(btnBox)
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
        if self.window.isMinimized():
            # If the window is minimized, restore it to its normal size
            self.window.setWindowState(
                self.window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

            # Bring the window to the front and activate it
        self.window.raise_()
        self.window.activateWindow()
    
    def ok_callback(self):
        value = self.delay_field.text()
        self.delay = int(value)  # Convert to integer
        self.node.delay = self.delay
        self.current_delay.setText(str(value))  # Updating the label text
        formatted_string = f"Z{to_superscript(self.delay)}"  # Pass integer to to_superscript
        self.delay_label.setText(formatted_string)
        self.window.close()
    
    def cancel_callback(self):
        self.window.close()
    
    def update_delay_field(self, value):
        self.delay = value
        self.node.delay = value
        self.current_delay.setText(str(value))  # Updating the label text
        formatted_string = f"Z{to_superscript(self.delay)}"  # Pass integer to to_superscript
        self.delay_label.setText(formatted_string)
        self.delay_field.setText(str(value))


import numpy as np

class Delay(NodeBase):
    title = 'Delay'
    main_widget_class = DelayWidget
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
        self.delay = 12  # Number of samples to delay
        self.buffer = np.zeros(self.delay, dtype=float)  # Buffer to store delayed samples

    def update_event(self, inp=-1):
        if inp > -1:
            frame = self.input(0)
            zoh_flag = frame[-1]
            frame = frame[:-1]

            # self.buffer = np.zeros(self.delay, dtype=float)
            # Prepare the output frame with delayed samples
            output_frame = np.concatenate((self.buffer, frame))

            # Update the buffer with the new samples
            if len(frame) >= self.delay:
                self.buffer = frame[-self.delay:]
            else:
                self.buffer = np.roll(self.buffer, -len(frame))
                self.buffer[-len(frame):] = frame

            # Append the zoh_flag back to the output frame
            output_frame = np.append(output_frame[:len(frame)], zoh_flag)

            self.set_output_val(0, output_frame)


    def get_state(self) -> dict:
        print("get_state called")
        print(self.delay)
        return {
            'delay': self.delay,
        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.delay = data['delay']
        print(data['delay'])



nodes = [
    Delay,
]
