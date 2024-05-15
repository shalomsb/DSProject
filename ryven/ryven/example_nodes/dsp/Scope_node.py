# import matplotlib.pyplot as plt
import numpy as np
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QLineEdit, QHBoxLayout, QLayout, QCheckBox
# import scipy
from qtpy.QtGui import QPixmap, QDoubleValidator, QFont
from qtpy.QtWidgets import QWidget, QPushButton, QLabel, QMainWindow, QVBoxLayout, QToolBar, QComboBox, QMenuBar, QMenu, \
    QActionGroup, QAction, QToolButton, QWidgetAction
from ryven.NENV import *
from ryven.NWENV import *
from scipy.signal import spectrogram

import pyqtgraph as pg
from qtpy.QtCore import Qt
from functools import partial
import globals



class NodeBase(Node):
    version = 'v0.1'
    color = '#FFCA00'


class NewPlotWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        # self.history_size = int(globals.fs + globals.frame_size - globals.fs % globals.frame_size)
        self.history_size = self.node.fs
        self.signal = np.zeros(self.history_size)
        self.signal1 = np.zeros(self.history_size)
        self.signal2 = np.zeros(self.history_size)

        self.counter = 1

        self.signal_zoh_flag = 0
        self.signal_zoh_flag1 = 0
        self.signal_zoh_flag2 = 0

        self.t = np.arange(self.history_size) / self.node.fs

        self.num_of_ports = self.node.num_of_ports
        self.x_range = self.node.x_range
        self.y_range = self.node.y_range

        # Create the GraphicsLayoutWidget without the background argument
        self.layout_widget = pg.GraphicsLayoutWidget()
        # Set the background color for the GraphicsLayoutWidget
        self.layout_widget.setBackground('k')
        self.plot_widget = self.layout_widget.addPlot()  # This is the PlotItem

        styles = {'color': '#FFF', 'font-size': '16px'}
        self.plot_widget.setLabel('left', 'Amplitude', **styles)  # Set label for y-axis
        self.plot_widget.setLabel('bottom', 'Time', **styles)  # Set label for x-axis
        axis_pen = pg.mkPen(color='#FFF', width=1)
        self.plot_widget.getAxis('bottom').setPen(axis_pen)
        self.plot_widget.getAxis('left').setPen(axis_pen)
        self.plot_widget.getAxis('bottom').setTextPen(axis_pen)
        self.plot_widget.getAxis('left').setTextPen(axis_pen)
        self.plot_widget.showGrid(x=True, y=True)  # Show grid on both axes

        self.plot_item2 = None
        self.plot_item = self.plot_widget.plot([], pen=pg.mkPen(color='#FF0', width=1), name="input1")
        # self.plot_item.getViewBox().disableAutoRange()

        # Create the InfiniteLine objects for cursors
        self.vLine1 = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('r', width=2))
        self.vLine2 = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('g', width=2))
        self.hLine1 = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('r', width=2))
        self.hLine2 = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('g', width=2))

        # Add the lines to the plot widget
        # self.plot_widget.addItem(self.vLine1)
        # self.plot_widget.addItem(self.vLine2)
        # self.plot_widget.addItem(self.hLine1)
        # self.plot_widget.addItem(self.hLine2)

        # Connect the lines to a method to handle their movement
        self.vLine1.sigPositionChanged.connect(self.updateLinePos)
        self.vLine2.sigPositionChanged.connect(self.updateLinePos)
        self.hLine1.sigPositionChanged.connect(self.updateLinePos)
        self.hLine2.sigPositionChanged.connect(self.updateLinePos)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        layout.setSizeConstraint(QLayout.SetFixedSize)  # Set the size constraint

        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "new_scope.png")
        image = QPixmap(icon_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        imageLabel.setMargin(0)  # Set the margins of the imageLabel to 0
        layout.addWidget(imageLabel)

        self.setLayout(layout)

        self.windowPlot = QWidget()
        self.windowPlot.setWindowTitle("Scope")
        self.windowPlot.setWindowIcon(image)
        self.windowPlot.setStyleSheet("""
            QWidget {
                background-color: #adbabd; /* Greyish-green background */
            }
            QPushButton, QLabel, QLineEdit, QCheckBox {
                color: black; /* Black font color */
                font-size: 20px; /* Font size set to 12 */
            }
        """)

        layout = QVBoxLayout()

        # Update layout to use the new GraphicsLayoutWidget
        layout.addWidget(self.layout_widget)

        self.button_layout = QHBoxLayout()

        self.x_zoom = QPushButton("x-zoom")
        self.y_zoom = QPushButton("y-zoom")
        self.xy_zoom = QPushButton("xy-zoom")

        # Set default color of xy-zoom to red
        self.xy_zoom.setStyleSheet("color: green")

        # Connect buttons to slots
        self.x_zoom.clicked.connect(self.buttonClicked)
        self.y_zoom.clicked.connect(self.buttonClicked)
        self.xy_zoom.clicked.connect(self.buttonClicked)

        self.button_layout.addWidget(self.x_zoom)
        self.button_layout.addWidget(self.y_zoom)
        self.button_layout.addWidget(self.xy_zoom)

        # Create horizontal layout for the difference display and x-axis range widgets
        info_layout = QHBoxLayout()
        self.vLineLabel = QLabel('Vertical Difference:')
        self.hLineLabel = QLabel('Horizontal Difference:')
        self.vLineLabel.hide()
        self.hLineLabel.hide()

        info_layout.addWidget(self.vLineLabel)
        info_layout.addWidget(self.hLineLabel)

        # Adding checkboxes for line visibility control
        self.vLines_checkbox = QCheckBox("Show Vertical Cursor")
        self.hLines_checkbox = QCheckBox("Show Horizontal Cursor")

        # # Set default states (Checked if you want them visible by default)
        # self.vLines_checkbox.setChecked(False)
        # self.hLines_checkbox.setChecked(False)

        # # Connect checkboxes to their respective slot methods
        self.vLines_checkbox.stateChanged.connect(self.toggle_vLines)
        self.hLines_checkbox.stateChanged.connect(self.toggle_hLines)

        # Set default states (Checked if you want them visible by default)
        self.vLines_checkbox.setChecked(False)
        self.hLines_checkbox.setChecked(False)

        # Add the layouts to the main layout
        layout.addLayout(self.button_layout)
        layout.addLayout(info_layout)

        # Adding checkboxes to the layout
        checkboxes_layout = QHBoxLayout()
        checkboxes_layout.addWidget(self.vLines_checkbox)
        checkboxes_layout.addWidget(self.hLines_checkbox)

        layout.addLayout(checkboxes_layout)

        self.windowPlot.setLayout(layout)

        self.main = QMainWindow()
        self.main.setWindowTitle("Scope")
        self.main.setWindowIcon(image)

        menu_bar = QMenuBar()
        file_menu = QMenu("File", menu_bar)
        menu_bar.addMenu(file_menu)

        stop_menu = QMenu("Pause/Unpause", menu_bar)
        menu_bar.addMenu(stop_menu)

        input_ports_submenu = QMenu("Number of Input Ports", file_menu)
        file_menu.addMenu(input_ports_submenu)
        input_ports_group = QActionGroup(self)

        # # Create actions
        for num_ports in range(1, 3):
            action = QAction(f"{num_ports}", self, checkable=True)
            action.triggered.connect(partial(self.on_input_ports_changed, num_ports))
            input_ports_submenu.addAction(action)
            input_ports_group.addAction(action)

        # Set the default checked action based on self.num_of_ports
        default_action = input_ports_group.actions()[self.num_of_ports - 1]
        default_action.setChecked(True)

        self.on_input_ports_changed(self.num_of_ports)


        stop_action = QAction("Pause/Unpause", self)
        stop_action.triggered.connect(self.on_stop_button_clicked)
        stop_menu.addAction(stop_action)

        self.main.setMenuBar(menu_bar)
        self.main.setCentralWidget(self.windowPlot)
        self.i = 0

        rangex_layout = QHBoxLayout()
        self.x_range_label = QLabel('Enter x-axis range (0 to 1):', self)  # Creates label
        rangex_layout.addWidget(self.x_range_label)  # Adds label to layout

        self.x_range_edit = QLineEdit(self)
        self.x_range_edit.setMinimumHeight(40)  # Adjust the width as needed to prevent text from being cut off

        self.x_range_edit.setValidator(QDoubleValidator(0.0, 1.0, 3))
        self.x_range_edit.setText(str(self.x_range))
        self.x_range_edit.setStyleSheet("background-color: white; color: black; border: 1px solid gray;")
        self.x_range_edit.returnPressed.connect(self.update_x_range)
        self.update_x_range()
        rangex_layout.addWidget(self.x_range_edit)  # Adds line edit to layout
        self.update_button = QPushButton('Update x-axis', self)  # Creates button
        self.update_button.clicked.connect(
            self.update_x_range)  # Connects button's clicked signal to update_x_range method
        rangex_layout.addWidget(self.update_button)  # Adds button to layout
        layout.addLayout(rangex_layout)


        rangey_layout = QHBoxLayout()
        self.y_range_label = QLabel('Enter y-axis range:', self)  # Creates label
        rangey_layout.addWidget(self.y_range_label)  # Adds label to layout

        self.y_range_edit = QLineEdit(self)
        self.y_range_edit.setMinimumHeight(40)  # Adjust the width as needed to prevent text from being cut off

        self.y_range_edit.setValidator(QDoubleValidator(0.0, 1000000, 3))
        self.y_range_edit.setStyleSheet("background-color: white; color: black; border: 1px solid gray;")
        self.y_range_edit.setText(str(self.y_range))
        self.y_range_edit.returnPressed.connect(self.update_y_range)
        self.update_y_range()
        rangey_layout.addWidget(self.y_range_edit)  # Adds line edit to layout
        self.updatey_button = QPushButton('Update y-axis', self)  # Creates button
        self.updatey_button.clicked.connect(
            self.update_y_range)  # Connects button's clicked signal to update_x_range method
        rangey_layout.addWidget(self.updatey_button)  # Adds button to layout
        layout.addLayout(rangey_layout)


        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.singleClickAction)

        self.click_count = 0

        # Initialize the cursor labels
        self.updateLinePos()

    def toggle_vLines(self, state):
        if state == Qt.Checked:
            self.plot_widget.addItem(self.vLine1)
            self.plot_widget.addItem(self.vLine2)
            self.vLineLabel.show()
        else:
            self.plot_widget.removeItem(self.vLine1)
            self.plot_widget.removeItem(self.vLine2)
            self.vLineLabel.hide()


    def toggle_hLines(self, state):
        if state == Qt.Checked:
            self.plot_widget.addItem(self.hLine1)
            self.plot_widget.addItem(self.hLine2)
            self.hLineLabel.show()
        else:
            self.plot_widget.removeItem(self.hLine1)
            self.plot_widget.removeItem(self.hLine2)
            self.hLineLabel.hide()

    def updateLinePos(self):
        # Retrieve the current positions of the vertical and horizontal lines
        vLinePos1 = self.vLine1.value()
        vLinePos2 = self.vLine2.value()
        hLinePos1 = self.hLine1.value()
        hLinePos2 = self.hLine2.value()

        # Calculate the differences in positions
        vertical_difference = abs(vLinePos1 - vLinePos2)
        horizontal_difference = abs(hLinePos1 - hLinePos2)

        # CSS style for the labels
        label_style = """
        QLabel {
            background-color: #444; /* Dark background for contrast */
            color: white; /* Bright text color for readability */
            border: 1px solid #FFF; /* White border */
            border-radius: 4px; /* Rounded corners */
            padding: 4px; /* Some padding around the text */
            font-weight: bold; /* Make the font bold */
            font-size: 20px; /* Increase the font size */
        }
        """

        # Update the labels with the differences, applying the CSS style
        self.vLineLabel.setStyleSheet(label_style)
        self.vLineLabel.setText(f'Vertical Difference: {vertical_difference:.4f}')

        self.hLineLabel.setStyleSheet(label_style)
        self.hLineLabel.setText(f'Horizontal Difference: {horizontal_difference:.4f}')

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
        self.main.show()
        if self.main.isMinimized():
            # If the window is minimized, restore it to its normal size
            self.main.setWindowState(self.main.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

            # Bring the window to the front and activate it
        self.main.raise_()
        self.main.activateWindow()

    def update_x_range(self):
        x_range = float(self.x_range_edit.text())  # Convert text to float
        self.plot_widget.setXRange(0, x_range)  # Set x range of the plot widget
        self.node.x_range = x_range

    def update_y_range(self):
        y_range = float(self.y_range_edit.text())  # Convert text to float
        print(y_range)
        self.plot_widget.setYRange(-y_range, y_range)  # Set x range of the plot widget
        self.node.y_range = y_range

    def on_stop_button_clicked(self):
        globals.stop_timer = not globals.stop_timer

    def on_input_ports_changed(self, num_ports):
        self.node.num_of_ports = num_ports
        self.node.update_ports()
        print(f"Number of input ports selected: {num_ports}")
        self.num_of_ports = num_ports
        if num_ports == 2:
            self.plot_item2 = self.plot_widget.plot([], pen=pg.mkPen(color='#0FF', width=1), name="input2")
        if num_ports == 1:
            self.plot_widget.removeItem(self.plot_item2)

    def add_frame(self, frame):
        if frame[-1] == 1:
            self.signal_zoh_flag = 1
        else:
            self.signal_zoh_flag = 0
        frame = frame[:-1]
        frame_length = len(frame)
        self.signal = np.roll(self.signal, -frame_length)
        # Insert the new frame at the end
        self.signal[-frame_length:] = frame
        length = len(self.signal)
        if self.signal_zoh_flag == 1:
            self.plot_item.setData(self.t[-length:], self.signal[-(self.history_size):], stepMode='left')
        else:
            self.plot_item.setData(self.t[-length:], self.signal[-(self.history_size):], stepMode=None)
        self.plot_item.getViewBox().disableAutoRange()

        # if self.i == 1:
        #     if self.signal_zoh_flag == 1:
        #         self.plot_item.setData(self.t[-length:], self.signal[-(self.history_size):], stepMode='left')
        #     else:
        #         self.plot_item.setData(self.t[-length:], self.signal[-(self.history_size):], stepMode=None)
        #     self.i = 0
        # else:
        #     self.i = self.i+1

    # def add_frame2(self, frame1, frame2):
    def add_frame2(self,frame1, frame2):

        if frame1[-1] == 1:
            self.signal_zoh_flag1 = 1
        else:
            self.signal_zoh_flag1 = 0
        if frame2[-1] == 1:
            self.signal_zoh_flag2 = 1
        else:
            self.signal_zoh_flag2 = 0
        frame1 = frame1[:-1]
        frame2 = frame2[:-1]
        frame_length1 = len(frame1)
        self.signal1 = np.roll(self.signal1, -frame_length1)
        self.signal1[-frame_length1:] = frame1
        frame_length2 = len(frame2)
        self.signal2 = np.roll(self.signal2, -frame_length2)
        self.signal2[-frame_length2:] = frame2

        length1 = len(self.signal1)
        length2 = len(self.signal2)

        if self.counter % 1 == 0:
            try:
                # Update plot_item (signal1)
                plot_item_data = (self.t[-length1:], self.signal1[-self.history_size:])
                step_mode_1 = 'left' if self.signal_zoh_flag1 == 1 else None
                self.plot_item.setData(*plot_item_data, stepMode=step_mode_1, pen={'color': "yellow", 'width': 3})

                # Update plot_item2 (signal2)
                plot_item2_data = (self.t[-length2:], self.signal2[-self.history_size:])
                step_mode_2 = 'left' if self.signal_zoh_flag2 == 1 else None
                self.plot_item2.setData(*plot_item2_data, stepMode=step_mode_2, pen={'color': "red", 'width': 3})
            except Exception as e:
                print(e)
        self.counter = self.counter + 1
        self.plot_item.getViewBox().disableAutoRange()
        self.plot_item2.getViewBox().disableAutoRange()

    def buttonClicked(self):
        # Reset all buttons to black text
        self.x_zoom.setStyleSheet("color: black")
        self.y_zoom.setStyleSheet("color: black")
        self.xy_zoom.setStyleSheet("color: black")

        # Set the text color of the clicked button to red
        sender = self.sender()
        if sender:
            sender.setStyleSheet("color: green")

        # Your existing zoom functions
        if sender == self.x_zoom:
            self.plot_widget.setMouseEnabled(x=True, y=False)
        elif sender == self.y_zoom:
            self.plot_widget.setMouseEnabled(x=False, y=True)
        elif sender == self.xy_zoom:
            self.plot_widget.setMouseEnabled(x=True, y=True)

class PlotNew(NodeBase):
    title = 'Scope'
    main_widget_class = NewPlotWidget
    main_widget_pos = 'between ports'
    style = 'large'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "new_scope.png")
    icon = icon_path
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params)

        self.fs = self.get_var_val("fs")
        if self.fs is None:
            print("fs from globals")
            self.fs = globals.fs
        self.frame_size = self.get_var_val("frame_size")
        if self.frame_size is None:
            print("frame size from globals")
            self.frame_size = globals.frame_size

        self.num_of_ports = 1
        self.x_range = 1
        self.y_range = 1

    def update_event(self, inp=-1):
        if inp == 0 and self.num_of_ports == 1:
            self.main_widget().add_frame(self.input(0))
            # self.main_widget().add_frame2(self.input(0), self.input(1))
        elif inp == 1 and self.num_of_ports == 2:
            # self.main_widget().add_frame(self.input(0))
            self.main_widget().add_frame2(self.input(0), self.input(1))
        else:
            pass


    def update_ports(self):
        current_ports = len(self.inputs)
        if current_ports == 1 and self.num_of_ports == 2:
            self.create_input()
        elif current_ports == 2 and self.num_of_ports == 1:
            self.delete_input(1)


    def get_state(self) -> dict:
        return {
            'num_of_ports': self.num_of_ports,
            'x_range': self.x_range,
            'y_range': self.y_range,
        }

    def set_state(self, data: dict, version):
        self.num_of_ports = data['num_of_ports']
        self.x_range = data['x_range']
        self.y_range = data['y_range']

nodes = [
    PlotNew,
]

