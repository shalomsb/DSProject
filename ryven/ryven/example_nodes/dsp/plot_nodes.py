# import matplotlib.pyplot as plt
import numpy as np
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QLineEdit
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
        self.frame_counter = 0  # Add this line to your __init__ method
        # self.frame_in_plot = int(1024/globals.frame_size)
        self.signal = np.zeros(globals.fs)
        self.signal_zoh_flag = 0
        self.signal_zoh_flag1 = 0
        self.signal_zoh_flag2 = 0

        self.signal1 = np.zeros(globals.fs)
        self.signal2 = np.zeros(globals.fs)

        self.t = np.arange(globals.fs) / (globals.fs)

        self.num_of_ports = self.node.num_of_ports

        # self.plot_widget = pg.PlotWidget(background="k")
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
        self.plot_item = self.plot_widget.plot([], pen=pg.mkPen(color='#FF0', width=3), name="input1")

        # # in your NewPlotWidget's __init__ method, after the self.plot_widget creation:
        # # Create and add Infinite Lines
        # self.vLine1 = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('r', width=2))  # Vertical line 1
        # self.vLine2 = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('g', width=2))  # Vertical line 2
        # self.hLine1 = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('r', width=2))  # Horizontal line 1
        # self.hLine2 = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('g', width=2))  # Horizontal line 2
        # self.plot_widget.addItem(self.vLine1, ignoreBounds=True)
        # self.plot_widget.addItem(self.vLine2, ignoreBounds=True)
        # self.plot_widget.addItem(self.hLine1, ignoreBounds=True)
        # self.plot_widget.addItem(self.hLine2, ignoreBounds=True)

        layout = QVBoxLayout()
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "scope.png")
        image = QPixmap(icon_path).scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)

        label = QLabel("   Scope")
        font = QFont()
        font.setPointSize(16)  # Set font size to 20 or another desired value
        label.setFont(font)
        layout.addWidget(label)

        self.setLayout(layout)

        self.windowPlot = QWidget()
        self.windowPlot.setWindowTitle("Scope")
        self.windowPlot.setWindowIcon(image)
        layout = QVBoxLayout()

        # layout.addWidget(self.plot_widget)  # add the PlotWidget, not the PlotDataItem
        # Update layout to use the new GraphicsLayoutWidget
        layout.addWidget(self.layout_widget)

        x_zoom = QPushButton("x-zoom")
        y_zoom = QPushButton("y-zoom")
        xy_zoom = QPushButton("xy-zoom")
        x_zoom.clicked.connect(self.xZoom)
        y_zoom.clicked.connect(self.yZoom)
        xy_zoom.clicked.connect(self.xyZoom)
        # Create and add Labels
        # self.vLineLabel = QLabel()  # Vertical line position label
        # self.hLineLabel = QLabel()  # Horizontal line position label
        # self.vLineDiffLabel = QLabel()  # Vertical line difference label
        # self.hLineDiffLabel = QLabel()  # Horizontal line difference label
        # layout.addWidget(self.vLineLabel)
        # layout.addWidget(self.hLineLabel)
        # layout.addWidget(self.vLineDiffLabel)
        # layout.addWidget(self.hLineDiffLabel)
        layout.addWidget(x_zoom)
        layout.addWidget(y_zoom)
        layout.addWidget(xy_zoom)
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
        # for num_ports in range(1, 3):  # Adjust the range as needed
        #     action = QAction(f"{num_ports}", self, checkable=True)
        #     action.triggered.connect(partial(self.on_input_ports_changed, num_ports))
        #     input_ports_submenu.addAction(action)
        #     input_ports_group.addAction(action)
        #
        #     # Check the action if num_ports matches self.num_of_ports
        #     if num_ports == self.num_of_ports:
        #         action.setChecked(True)
        #         self.on_input_ports_changed(num_ports)

        # # Create actions
        for num_ports in range(1, 3):
            action = QAction(f"{num_ports}", self, checkable=True)
            action.triggered.connect(partial(self.on_input_ports_changed, num_ports))
            input_ports_submenu.addAction(action)
            input_ports_group.addAction(action)

        # Set the default checked action based on self.num_of_ports
        default_action = input_ports_group.actions()[self.num_of_ports - 1]
        default_action.setChecked(True)

        stop_action = QAction("Pause/Unpause", self)
        stop_action.triggered.connect(self.on_stop_button_clicked)
        stop_menu.addAction(stop_action)

        self.main.setMenuBar(menu_bar)
        self.main.setCentralWidget(self.windowPlot)
        self.i = 0
        # Connect signal for mouse movement
        # self.proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.x_range_label = QLabel('Enter x-axis range (0 to 1):', self)  # Creates label
        layout.addWidget(self.x_range_label)  # Adds label to layout

        self.x_range_edit = QLineEdit(self)
        self.x_range_edit.setValidator(QDoubleValidator(0.0, 1.0, 3))
        self.x_range_edit.setText("0.01")
        self.x_range_edit.returnPressed.connect(self.update_x_range)
        self.x_range_edit.setStyleSheet("background-color: white; color: black; border: 1px solid gray;")
        self.update_x_range()
        layout.addWidget(self.x_range_edit)  # Adds line edit to layout
        self.update_button = QPushButton('Update x-axis', self)  # Creates button
        self.update_button.clicked.connect(
            self.update_x_range)  # Connects button's clicked signal to update_x_range method
        layout.addWidget(self.update_button)  # Adds button to layout

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
        self.window1()

    def update_x_range(self):
        x_range = float(self.x_range_edit.text())  # Convert text to float
        self.plot_widget.setXRange(0, x_range)  # Set x range of the plot widget

    # def mouseMoved(self, evt):
    #     pos = evt[0]
    #     if self.plot_widget.sceneBoundingRect().contains(pos):
    #         # mousePoint = self.plot_widget.plotItem.vb.mapSceneToView(pos)
    #         mousePoint = self.plot_widget.vb.mapSceneToView(pos)
    #         index = int(mousePoint.x())
    #         if 0 < index < len(self.signal):
    #             self.vLine1.setPos(mousePoint.x())
    #             self.hLine1.setPos(mousePoint.y())
    #
    #         # Formatting the text with styling
    #         self.vLineLabel.setText(
    #             f'<strong>Vertical Lines:</strong> '
    #             f'Line 1: <span style="color: yellow;">{self.vLine1.getPos()[0]:.2f}</span> units, '
    #             f'Line 2: <span style="color: red;">{self.vLine2.getPos()[0]:.2f}</span> units'
    #         )
    #
    #         self.hLineLabel.setText(
    #             f'<strong>Horizontal Lines:</strong> '
    #             f'Line 1: <span style="color: yellow;">{self.hLine1.getPos()[1]:.2f}</span> units, '
    #             f'Line 2: <span style="color: red;">{self.hLine2.getPos()[1]:.2f}</span> units'
    #         )
    #
    #         self.vLineDiffLabel.setText(
    #             f'<strong>Vertical Difference:</strong> '
    #             f'<span style="color: green;">{abs(self.vLine1.getPos()[0] - self.vLine2.getPos()[0]):.2f}</span> units'
    #         )
    #
    #         self.hLineDiffLabel.setText(
    #             f'<strong>Horizontal Difference:</strong> '
    #             f'<span style="color: green;">{abs(self.hLine1.getPos()[1] - self.hLine2.getPos()[1]):.2f}</span> units'
    #         )

    def on_stop_button_clicked(self):
        globals.stop_timer = not globals.stop_timer
        print(globals.stop_timer)

    def on_input_ports_changed(self, num_ports):
        print("blabla")
        self.node.num_of_ports = num_ports
        self.node.update_ports()
        print(f"Number of input ports selected: {num_ports}")
        self.num_of_ports = num_ports
        if num_ports == 2:
            self.plot_item2 = self.plot_widget.plot([], pen=pg.mkPen(color='#0FF', width=3), name="input2")
            # self.plot_item2.setData(np.array([1, 4, 9, 16]), np.array([1, 4, 9, 16]))
        if num_ports == 1:
            self.plot_widget.removeItem(self.plot_item2)
        # # self.update_node()

    def getNumOfPorts(self):
        return self.num_of_ports


    def window1(self):
        self.main.show()

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
        if self.i == 1:
            if self.signal_zoh_flag == 1:
                self.plot_item.setData(self.t[-length:], self.signal[-(globals.fs):], stepMode='left')
            else:
                self.plot_item.setData(self.t[-length:], self.signal[-(globals.fs):], stepMode=None)
            # self.t = np.arange(globals.fs*256) / (globals.fs*256)
            # self.plot_item.setData(self.t, np.repeat(self.signal[-(globals.fs):],256))
            self.i = 0
        else:
            self.i = self.i+1

    def add_frame2(self, frame1, frame2):
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

        # Determine data and stepMode for self.plot_item
        try:
            if self.signal_zoh_flag1 == 1 and self.signal_zoh_flag2 == 1:
                plot_item_data = (self.t[-length1:], self.signal1[-globals.fs:])
                plot_item2_data = (self.t[-length2:], self.signal2[-globals.fs:])
                self.plot_item.setData(*plot_item_data, stepMode='left', name="input1",
                                       pen={'color': "yellow", 'width': 1})
                self.plot_item2.setData(*plot_item2_data, stepMode='left', name="input2",
                                        pen={'color': (51, 153, 255), 'width': 1})

            elif self.signal_zoh_flag1 == 1 and self.signal_zoh_flag2 == 0:
                plot_item_data = (self.t[-length1:], self.signal1[-globals.fs:])
                plot_item2_data = (self.t[-length2:], self.signal2[-globals.fs:])
                self.plot_item.setData(*plot_item_data, stepMode='left',
                                       pen={'color': "yellow", 'width': 3})
                self.plot_item2.setData(*plot_item2_data,
                                        pen={'color': "red", 'width': 3})
            elif self.signal_zoh_flag1 == 0 and self.signal_zoh_flag2 == 1:
                plot_item_data = (self.t[-length1:], self.signal1[-globals.fs:])
                plot_item2_data = (self.t[-length2:], self.signal2[-globals.fs:])
                self.plot_item.setData(*plot_item_data,
                                       pen={'color': "yellow", 'width': 3})
                self.plot_item2.setData(*plot_item2_data, stepMode='left',
                                        pen={'color': "red", 'width': 3})
            elif self.signal_zoh_flag1 == 0 and self.signal_zoh_flag2 == 0:
                plot_item_data = (self.t[-length1:], self.signal1[-globals.fs:])
                plot_item2_data = (self.t[-length2:], self.signal2[-globals.fs:])
                self.plot_item.setData(*plot_item_data,
                                       pen={'color': "yellow", 'width': 3})
                self.plot_item2.setData(*plot_item2_data,
                                        pen={'color': "red", 'width': 3})
        except Exception as e:
            print(e)


    def xZoom(self):
        self.plot_widget.setMouseEnabled(x=True, y=False)

    def yZoom(self):
        self.plot_widget.setMouseEnabled(x=False, y=True)

    def xyZoom(self):
        self.plot_widget.setMouseEnabled(x=True, y=True)


class PlotNew(NodeBase):
    title = 'Scope'
    main_widget_class = NewPlotWidget
    main_widget_pos = 'between ports'
    style = 'large'
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params)
        self.num_of_ports = 1
        print("bingo")

    def update_event(self, inp=-1):
        pass
        if self.num_of_ports == 1:
            self.main_widget().add_frame(self.input(0))
        elif self.num_of_ports == 2:
            self.main_widget().add_frame2(self.input(0), self.input(1))
        # if inp == -1:
        #     num_of_ports = self.main_widget().getNumOfPorts()
        #     if self.num_of_ports > 1:
        #         for i in reversed(range(1, self.num_of_ports)):
        #             print(i)
        #             print(self.num_of_ports)
        #             self.delete_input(i)
        #
        #     if num_of_ports > 1:
        #         for i in range(1, num_of_ports):
        #             # self.create_input(label=f"samples{i}:")
        #             self.create_input()
        #
        #     self.num_of_ports = num_of_ports
        # print(inp)
        # if inp == 1:
        #     print(self.input(1))
        #     self.main_widget().add_frame2(self.input(0), self.input(1))
        # elif inp == 0:
        #     self.main_widget().add_frame(self.input(0))

    # def view_place_event(self):
    #     # importlib.reload(globals)
    #     num_of_ports = self.num_of_ports
    #     if self.num_of_ports == 2:
    #         self.create_input()
    def update_ports(self):
        current_ports = len(self.inputs)
        if current_ports == 1 and self.num_of_ports == 2:
            self.create_input()
        elif current_ports == 2 and self.num_of_ports == 1:
            self.delete_input(1)


    def get_state(self) -> dict:
        return {
            'num_of_ports': self.num_of_ports,
        }

    def set_state(self, data: dict, version):
        self.num_of_ports = data['num_of_ports']



class SpectrogramPlotWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.signal = np.array([])
        self.t = np.arange(80000) / 16000

        self.spec_plot = pg.PlotItem()
        self.spec_plot.setLabel('left', 'Frequency (Hz)')
        self.spec_plot.setLabel('bottom', 'Time (s)')

        self.spec_image = pg.ImageItem()
        self.spec_plot.addItem(self.spec_image)


        # Apply the 'viridis' colormap
        self.color_map = pg.colormap.get('viridis')
        self.spec_image.setLookupTable(self.color_map.getLookupTable())

        self.spec_view = pg.PlotWidget()
        self.spec_view.setCentralItem(self.spec_plot)

        layout = QVBoxLayout()
        layout.addWidget(self.spec_view)
        self.setLayout(layout)

        self.spec_signal = np.array([])
        self.spec_window = 80000
        self.spec_noverlap = 256  # Change from 8000 to 64
        self.spec_nfft = 1024

    def update_spectrogram(self, signal):
        _, times, spec = spectrogram(signal, fs=16000, nperseg=self.spec_nfft, noverlap=self.spec_noverlap)
        spec_dB = 20 * np.log10(spec)
        self.spec_image.setImage(spec_dB.T)
        print(spec_dB.T.shape)


    def add_frame(self, frame):
        self.signal = np.concatenate((self.signal, frame))
        if len(self.signal) >= self.spec_window:
            self.update_spectrogram(self.signal[-self.spec_window:])
            self.signal = self.signal[-self.spec_window:]


class PlotSpectrogram(Node):
    title = 'Spectrogram'
    main_widget_class = SpectrogramPlotWidget
    main_widget_pos = 'below ports'
    init_inputs = [
        NodeInputBP(label='samples:'),
    ]
    init_outputs = [
        NodeOutputBP(label='spectrum:'),
    ]

    def __init__(self, params):
        super().__init__(params)

    def update_event(self, inp=-1):
        if inp == 0:
            new_samples = self.input(0)
            if new_samples is not None:
                self.main_widget().add_frame(new_samples)


nodes = [
    PlotNew,
    # PlotSpectrogram,
]

