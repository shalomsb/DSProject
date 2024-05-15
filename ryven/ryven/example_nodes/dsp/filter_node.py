import numpy as np
from PySide2.QtWidgets import QDoubleSpinBox, QSplitter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ryven.NWENV import *
from ryven.NENV import *
from qtpy.QtWidgets import QHBoxLayout, QWidget, QPushButton, QComboBox, QSpinBox,  \
    QLabel, QVBoxLayout, QGridLayout, QCheckBox
from qtpy.QtGui import QPixmap
from PySide2.QtCore import Qt
from scipy import signal
import globals
import mplcursors


class MyApp(QWidget):
    def __init__(self, response_type, design_method, method_options, window_options, filter_order, fs, fc, fpass, fstop, wpass, wstop):
        super().__init__()

        self.initUI(response_type, design_method, method_options, window_options, filter_order, fs, fc, fpass, fstop, wpass, wstop)
        self.current_filter_params = {}
        self.set_font_size(10)

    def initUI(self, response_type, design_method, method_options, window_options, filter_order, fs, fc, fpass, fstop, wpass, wstop):
        self.setWindowTitle('Digital Filter Designer')

        # The parent layout
        parent_layout = QHBoxLayout()

        # Create the splitter
        splitter = QSplitter(Qt.Horizontal)

        # Create the left and right widgets and layouts
        left_widget = QWidget()
        left_layout = QGridLayout()

        right_widget = QWidget()
        right_layout = QVBoxLayout()


        # User Inputs
        self.response_type = QComboBox()
        self.response_type.addItems(["Lowpass", "Highpass"])
        self.response_type.setCurrentText(response_type)

        self.design_method = QComboBox()
        self.design_method.addItems(["IIR", "FIR"])
        self.design_method.setCurrentText(design_method)
        self.design_method.currentIndexChanged.connect(self.update_method_options)

        self.method_options = QComboBox()
        self.method_options.addItems(["Butterworth", "Chebyshev Type I"])
        self.method_options.setCurrentText(method_options)

        self.window_options = QComboBox()
        self.window_options.addItems(["Bartlett", "Hamming", "Hann"])
        self.window_options.setCurrentText(window_options)
        self.window_options.setDisabled(True)
        self.method_options.currentIndexChanged.connect(self.update_window_options)

        self.filter_order = QSpinBox()
        self.filter_order.setRange(1, 500)
        self.filter_order.setValue(filter_order)

        self.fs = QDoubleSpinBox()
        self.fs.setRange(1, 100000)
        self.fs.setDecimals(2)
        self.fs.setValue(fs)

        self.fc = QDoubleSpinBox()
        self.fc.setRange(1, 100000)
        self.fc.setDecimals(2)
        self.fc.setValue(fc)

        self.fpass = QDoubleSpinBox()
        self.fpass.setRange(1, 100000)
        self.fpass.setDecimals(2)
        self.fpass.setValue(fpass)

        self.fstop = QDoubleSpinBox()
        self.fstop.setRange(1, 100000)
        self.fstop.setDecimals(2)
        self.fstop.setValue(fstop)

        self.wpass = QDoubleSpinBox()
        self.wpass.setRange(1, 10000)
        self.wpass.setDecimals(2)
        self.wpass.setValue(wpass)

        self.wstop = QDoubleSpinBox()
        self.wstop.setRange(1, 10000)
        self.wstop.setDecimals(2)
        self.wstop.setValue(wstop)

        self.fpass.setDisabled(True)
        self.fstop.setDisabled(True)
        self.wpass.setDisabled(True)
        self.wstop.setDisabled(True)

        # Error Label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red")  # Set red font color for error messages

        # Layouts
        left_layout.addWidget(QLabel("Response Type"), 0, 0)
        left_layout.addWidget(self.response_type, 0, 1)

        left_layout.addWidget(QLabel("Design Method"), 1, 0)
        left_layout.addWidget(self.design_method, 1, 1)
        left_layout.addWidget(self.method_options, 1, 2)
        left_layout.addWidget(self.window_options, 1, 3)

        left_layout.addWidget(QLabel("Filter Order"), 2, 0)
        left_layout.addWidget(self.filter_order, 2, 1)

        left_layout.addWidget(QLabel("Fs"), 3, 0)
        left_layout.addWidget(self.fs, 3, 1)

        self.use_sim_fs = QCheckBox("Use Simulation Fs")
        self.use_sim_fs.setStyleSheet(
            "QCheckBox::indicator { border: 1px solid white; width: 20px; height: 20px; background: grey; } QCheckBox "
            "{ color: white }")

        left_layout.addWidget(self.use_sim_fs, 3, 2)
        self.use_sim_fs.stateChanged.connect(self.update_fs)
        self.use_sim_fs.setChecked(True)  # Set the checkbox as checked by default

        left_layout.addWidget(QLabel("Fc"), 4, 0)
        left_layout.addWidget(self.fc, 4, 1)

        self.Fpass_label = QLabel("Fpass")
        self.Fstop_label = QLabel("Fstop")
        left_layout.addWidget(self.Fpass_label, 5, 0)
        left_layout.addWidget(self.fpass, 5, 1)

        left_layout.addWidget(self.Fstop_label, 6, 0)
        left_layout.addWidget(self.fstop, 6, 1)

        self.response_type.currentIndexChanged.connect(self.update_response_type)

        left_layout.addWidget(QLabel("Wpass"), 7, 0)
        left_layout.addWidget(self.wpass, 7, 1)

        left_layout.addWidget(QLabel("Wstop"), 8, 0)
        left_layout.addWidget(self.wstop, 8, 1)

        left_layout.addWidget(self.error_label, 9, 0, 1, 2)  # Add error label to the layout

        # Button
        btn = QPushButton('Design Filter', self)
        btn.clicked.connect(self.plot)
        left_layout.addWidget(btn, 10, 0, 1, 2)

        # Plot
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        right_layout.addWidget(self.canvas)  # Place the plot on the right side

        # Apply layouts to widgets
        left_widget.setLayout(left_layout)
        right_widget.setLayout(right_layout)

        # Add widgets to the splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Add the splitter to the parent layout
        parent_layout.addWidget(splitter)

        self.setLayout(parent_layout)
        self.update_method_options()

    def store_current_params(self):
        self.current_filter_params = {
            'response_type': self.response_type.currentText(),
            'design_method': self.design_method.currentText(),
            'method_options': self.method_options.currentText(),
            'window_options': self.window_options.currentText(),
            'filter_order': self.filter_order.value(),
            'fs': self.fs.value(),
            'fc': self.fc.value(),
            'fpass': self.fpass.value(),
            'fstop': self.fstop.value(),
            'wpass': self.wpass.value(),
            'wstop': self.wstop.value()
        }

    def get_current_params(self):
        self.current_filter_params = {
            'response_type': self.response_type.currentText(),
            'design_method': self.design_method.currentText(),
            'method_options': self.method_options.currentText(),
            'window_options': self.window_options.currentText(),
            'filter_order': self.filter_order.value(),
            'fs': self.fs.value(),
            'fc': self.fc.value(),
            'fpass': self.fpass.value(),
            'fstop': self.fstop.value(),
            'wpass': self.wpass.value(),
            'wstop': self.wstop.value()
        }
        return self.current_filter_params

    def update_method_options(self):
        method = self.design_method.currentText()
        if method == "IIR":
            self.method_options.clear()
            self.method_options.addItems(["Butterworth", "Chebyshev Type I"])
            self.window_options.setDisabled(True)
            self.fpass.setDisabled(True)
            self.fstop.setDisabled(True)
            self.wpass.setDisabled(True)
            self.wstop.setDisabled(True)
            self.fc.setDisabled(False)
        else:  # FIR
            self.method_options.clear()
            self.method_options.addItems(["Equiripple", "Window"])
            self.window_options.setDisabled(self.method_options.currentText() != "Window")
            self.fc.setDisabled(self.method_options.currentText() == "Equiripple")
            if self.method_options.currentText() == "Equiripple":
                self.fpass.setDisabled(False)
                self.fstop.setDisabled(False)
                self.wpass.setDisabled(False)
                self.wstop.setDisabled(False)

    def update_window_options(self):
        method = self.design_method.currentText()
        method_option = self.method_options.currentText()

        if method == "FIR" and method_option == "Window":
            self.window_options.setDisabled(False)
            self.fpass.setDisabled(True)  # Disable Fpass
            self.fstop.setDisabled(True)  # Disable Fstop
            self.wpass.setDisabled(True)  # Disable Wpass
            self.wstop.setDisabled(True)  # Disable Wstop
            self.fc.setDisabled(False)  # Enable Fc for Window method
        elif method == "FIR" and method_option == "Equiripple":
            self.fc.setDisabled(True)  # disable fc when method_option is Equiripple
            self.fpass.setDisabled(False)  # disable fpass when method_option is Equiripple
            self.fstop.setDisabled(False)  # disable fstop when method_option is Equiripple
            self.wpass.setDisabled(False)  # disable wpass when method_option is Equiripple
            self.wstop.setDisabled(False)  # disable wstop when method_option is Equiripple
        else:
            self.window_options.setDisabled(True)
            self.fpass.setDisabled(False)  # Enable Fpass
            self.fstop.setDisabled(False)  # Enable Fstop
            self.wpass.setDisabled(False)  # Enable Wpass
            self.wstop.setDisabled(False)  # Enable Wstop

    def update_response_type(self):
        response_type = self.response_type.currentText()
        if response_type == "Highpass":
            self.Fpass_label.setText("Fstop")
            self.Fstop_label.setText("Fpass")
        else:
            self.Fpass_label.setText("Fpass")
            self.Fstop_label.setText("Fstop")

    def calculate_coefficients(self):
        # N = self.filter_order.value()
        N = self.current_filter_params.get('filter_order')
        # fs = self.fs.value()
        fs = self.current_filter_params.get('fs')
        # fc = self.fc.value()
        fc = self.current_filter_params.get('fc')
        # response_type = self.response_type.currentText()
        response_type = self.current_filter_params.get('response_type')
        # method = self.design_method.currentText()
        method = self.current_filter_params.get('design_method')
        # method_option = self.method_options.currentText()
        method_option = self.current_filter_params.get('method_options')
        # window_option = self.window_options.currentText()
        window_option = self.current_filter_params.get('window_options')

        b, a = None, None

        if not any([response_type, method, method_option, window_option]):
            return b, a, fs

        if response_type == "Lowpass":
            btype = 'low'
        else:
            btype = 'high'

        if method == "IIR":
            if method_option == "Butterworth":
                b, a = signal.butter(N, fc, btype=btype, fs=fs)
            elif method_option == "Chebyshev Type I":
                b, a = signal.cheby1(N, 1, fc, btype=btype, fs=fs)
        else:  # FIR
            if method_option == "Equiripple":
                bands = [0, self.fpass.value(), self.fstop.value(), 0.5 * fs]
                desired = [1, 0] if btype == 'low' else [0, 1]
                weights = [self.wpass.value(), self.wstop.value()]
                b = signal.remez(N + 1, bands, desired, weight=weights, fs=fs)
                a = [1]
            else:  # Window
                if window_option == "Bartlett":
                    win = 'bartlett'
                elif window_option == "Hamming":
                    win = 'hamming'
                else:  # Hann
                    win = 'hann'
                b = signal.firwin(N, fc, window=win, pass_zero=btype == 'low', fs=fs)
                a = [1]

        return b, a, fs

    def get_filter_coefficients(self):
        try:
            b, a, fs = self.calculate_coefficients()
            return b, a
        except ValueError as e:
            print(f"An error occurred: {str(e)}")  # You can handle the error as per your requirement

    def plot(self):
        try:
            self.store_current_params()
            self.fig.clear()

            # Create a 2-row subplot: top for magnitude and bottom for phase
            ax1 = self.fig.add_subplot(2, 1, 1)  # Magnitude plot
            ax2 = self.fig.add_subplot(2, 1, 2)  # Phase plot

            b, a, fs = self.calculate_coefficients()
            w, h = signal.freqz(b, a, worN=8000)
            f = w * fs / (2 * np.pi)

            # Magnitude plot
            ax1.plot(f, 20 * np.log10(abs(h)))
            ax1.set_ylabel('Magnitude [dB]')
            ax1.grid(True)

            # Phase plot with unwrapping
            ax2.plot(f, np.unwrap(np.angle(h)))  # Unwrapped phase in radians
            ax2.set_xlabel('Frequency [Hz]')
            ax2.set_ylabel('Phase [degrees]')
            ax2.grid(True)

            mplcursors.cursor(ax1, hover=True)
            mplcursors.cursor(ax2, hover=True)
            self.canvas.draw()



            self.error_label.setText("")  # Clear any previous error message
        except ValueError as e:
            self.error_label.setText(f"An error occurred: {str(e)}")  # Display the error message in the layout

    def update_fs(self):
        if self.use_sim_fs.isChecked():
            self.fs.setValue(globals.fs)

    def set_font_size(self, size):
        for widget in self.findChildren(QWidget):
            font = widget.font()
            font.setPointSize(size)
            widget.setFont(font)

class TryWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        layout = QVBoxLayout()
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "LPF.png")
        image = QPixmap(icon_path).scaled(240, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        self.setLayout(layout)
        self.a = None
        self.b = None
        self.zi = None  # initial conditions for the filter
        self.response_type = self.node.response_type
        self.design_method = self.node.design_method
        self.method_options = self.node.method_options
        self.window_options = self.node.window_options
        self.filter_order = self.node.filter_order
        self.fs = self.node.fs
        self.fc = self.node.fc
        self.fpass = self.node.fpass
        self.fstop = self.node.fstop
        self.wpass = self.node.wpass
        self.wstop = self.node.wstop

        try:
            self.window = MyApp(self.response_type, self.design_method, self.method_options, self.window_options, self.filter_order, self.fs, self.fc, self.fpass, self.fstop, self.wpass, self.wstop)
            self.window.plot()
        except Exception as e:
            print(e)



    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        self.window.show()

    import numpy as np

    def filter_frame(self, frame):
        try:
            b, a = self.window.get_filter_coefficients()

            # If the user didn't select any filter parameters
            if b is None or a is None:
                return frame
            else:
                # If the user set parameters for the first time or changed them
                if self.b is None or self.a is None or not np.array_equal(b, self.b) or not np.array_equal(a, self.a):
                    self.b, self.a = b, a
                    # if the coefficients have changed, reset zi
                    self.zi = signal.lfilter_zi(self.b, self.a) * frame[0]

                # apply the filter
                frame_filtered, self.zi = signal.lfilter(self.b, self.a, frame, zi=self.zi)

                return frame_filtered

        except Exception as e:
            print(f"An exception occurred: {e}")
            raise

    def gets_parameters(self):
        return self.window.get_current_params()


class LPF(Node):
    title = 'Filter'
    style = 'large'
    main_widget_class = TryWidget
    main_widget_pos = 'between ports'
    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def __init__(self, params):
        super().__init__(params)
        self.a = None
        self.b = None
        self.zi = None
        self.change = False
        self.response_type = "Lowpass"
        self.design_method = "FIR"
        self.method_options = "Butterworth"
        self.window_options = "Bartlett"
        self.filter_order = 1
        self.fs = 1
        self.fc = 1
        self.fpass = 1
        self.fstop = 1
        self.wpass = 1
        self.wstop = 1



    def update_event(self, inp=-1):

        if inp == 0:
            frame = self.input(0)
            zoh_flag = frame[-1]
            frame = frame[:-1]
            filter_frame = self.main_widget().filter_frame(frame)
            filter_frame = np.append(filter_frame, zoh_flag)
            self.set_output_val(0, filter_frame)


    def get_state(self) -> dict:
        print("get_state called")
        data_parameters = self.main_widget().gets_parameters()

        return {
            'response_type': data_parameters['response_type'],
            'design_method': data_parameters['design_method'],
            'method_options': data_parameters['method_options'],
            'window_options': data_parameters['window_options'],
            'filter_order': data_parameters['filter_order'],
            'fs': data_parameters['fs'],
            'fc': data_parameters['fc'],
            'fpass': data_parameters['fpass'],
            'fstop': data_parameters['fstop'],
            'wpass': data_parameters['wpass'],
            'wstop': data_parameters['wstop']

        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.response_type = data['response_type']
        self.design_method = data['design_method']
        self.method_options = data['method_options']
        self.window_options = data['window_options']
        self.filter_order = data['filter_order']
        self.fs = data['fs']
        self.fc = data['fc']
        self.fpass = data['fpass']
        self.fstop = data['fstop']
        self.wpass = data['wpass']
        self.wstop = data['wstop']




nodes = [
    LPF,
]