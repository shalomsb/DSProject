# import matplotlib.pyplot as plt
import numpy as np
# import scipy
# from qtpy.QtGui import QPixmap, QDoubleValidator
from qtpy.QtWidgets import QWidget, QPushButton, QLabel, QMainWindow, QVBoxLayout, QToolBar, QComboBox, QMenuBar, QMenu, \
    QActionGroup, QAction, QToolButton, QWidgetAction, QSpinBox, QHBoxLayout, QSizePolicy, QGroupBox, QFormLayout, QLineEdit
from ryven.NENV import *
from ryven.NWENV import *
from scipy.io import wavfile
from scipy.signal import spectrogram, stft, windows, welch
import globals
import pyqtgraph as pg
from PySide2.QtCore import QRectF, QTimer
from qtpy.QtGui import QPixmap, QFont
from qtpy.QtCore import Qt
from scipy.signal.windows import hann, hamming


class SpectrumWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        layout = QVBoxLayout()
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "spectrum analyzer.png")
        image = QPixmap(icon_path).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        imageLabel.setStyleSheet("background-color: white;")
        layout.addWidget(imageLabel)

        label = QLabel("Spectrum Analyzer")
        font = QFont()
        font.setPointSize(14)  # Set font size to 20 or another desired value
        label.setFont(font)
        layout.addWidget(label)

        self.setLayout(layout)
        self.fs = self.node.fs
        self.window_length = self.node.window_length
        self.window_type = self.node.window_type
        self.overlap = self.node.overlap
        self.spec_nfft = self.node.spec_nfft
        self.spec_noverlap = np.round(self.spec_nfft*self.overlap/100)

        self.last_5_seconds_buffer = np.zeros(globals.fs * 5)
        # self.last_5_seconds_buffer = np.zeros(68820)
        spec_size = int(self.spec_nfft // 2 + 1)
        self.spec = np.empty((spec_size, 0))
        self.spec_signal = np.array([])
        # self.spec_window = 16000*5
        # self.window = MainWindow(self, self.fs, self.window_type, self.window_length, self.spec_nfft, self.overlap)  # pass self to MainWindow
        self.window = MainWindow(self)  # pass self to MainWindow

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


    # def mousePressEvent(self, event):
    #     super().mousePressEvent(event)
    #
    #
    # def mouseDoubleClickEvent(self, event):
    #     self.window.show()


    def add_frame(self, frame):
        self.last_5_seconds_buffer = np.roll(self.last_5_seconds_buffer, -len(frame))
        self.last_5_seconds_buffer[-len(frame):] = frame
        self.build_spectrum(frame)
        self.build_spectrogram(self.last_5_seconds_buffer)


    def build_spectrum(self, data):
        self.spec_noverlap = int(self.window_length * self.overlap/100)  # with 75% overlap
        if self.window_type == "Hann":
            window = hann(self.window_length)  # Hann window
        elif self.window_type == "Hamming":
            window = hamming(self.window_length)  # Hamming window
        else:
            window = np.ones(self.window_length)  # Rectangular window

        frequencies, Pxx = welch(data, self.fs, window=window,nperseg=self.window_length, noverlap=int(self.spec_noverlap), nfft=self.spec_nfft,
                                 return_onesided=True,
                                 scaling='density')
        # frequencies, Pxx = welch(data, fs=globals.fs, window=window, nperseg=256,
        #                          noverlap=int(256*0.75), nfft=256*2,
        #                          return_onesided=True,
        #                          scaling='density')

        # Convert to dBm assuming Pxx is in Watts (which is not physically correct, but for illustration purposes)
        Pxx_dbm = 10 * np.log10(Pxx) + 30

        self.window.update_spectrum(frequencies, Pxx_dbm)

    def build_spectrogram(self, data):
        self.spec_noverlap = int(self.window_length * self.overlap / 100)  # with 75% overlap
        print(self.spec_noverlap)
        if self.window_type == "Hann":
            window = hann(self.window_length)  # Hann window
        elif self.window_type == "Hamming":
            window = np.hamming(self.window_length)  # Hamming window
        else:
            window = np.ones(self.window_length)  # Rectangular window

        # f, t, spec = stft(data[-(self.window_length+self.spec_noverlap):], fs=self.fs, nperseg=self.spec_nfft, noverlap=self.spec_noverlap,
        #                   window=window, padded=False,
        #                   boundary=None)
        # fs, data = wavfile.read("C:\\Users\\shalo\\PycharmProjects\\DSProject\\record1.wav")
        f, t, spec = stft(data, fs=self.fs, nfft=self.spec_nfft,
                          noverlap=self.spec_noverlap,
                          window=window, nperseg=self.window_length,  padded=False,
                          boundary=None)

        print(spec.shape)
        spec = np.abs(spec)
        # Update the combined spectrogram
        # self.spec = np.concatenate((self.spec[:, :], spec), axis=1)
        self.spec = spec
        # limit = np.ceil((self.spec_window-self.window_length)/(self.window_length*(1-self.overlap/100)))
        # # print(limit)
        # self.spec = self.spec[:, -int(limit):]

        # Compute the frequency and time arrays
        # f = np.fft.fftfreq(self.spec_nfft, 1 / self.fs)[:self.spec_nfft // 2]
        # t = np.arange(self.spec.shape[1]) * (self.spec_nfft - self.spec_noverlap) / self.fs
        self.window.update_spectrogram(self.spec, f, t)


class MainWindow(QMainWindow):
    def __init__(self, spectrum_widget, parent=None):
        super(MainWindow, self).__init__(parent)
        self.spectrum_widget = spectrum_widget  # store the SpectrumWidget instance
        # self.curr_window_length = 1024

        # Create the main widget that will contain the plots and the control panel
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Create the layout for the main widget
        layout = QHBoxLayout(main_widget)

        # Create the layout for the plots
        self.plots_layout = QVBoxLayout()
        layout.addLayout(self.plots_layout)

        # Create the layout for the control panel
        control_layout = QVBoxLayout()
        layout.addLayout(control_layout)

        # Create the plots
        self.plot_spectrum = pg.PlotWidget()
        self.plot_spectrum.setLabel('left', 'PSD')
        self.plot_spectrum.setLabel('bottom', 'Frequency')
        # self.plot_spectrum.getAxis('bottom').setLogMode(True)
        self.plot_spectrum.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding))
        self.plot_spectrum.setLogMode(True, False)
        self.spectrum_plot_item = self.plot_spectrum.plot([], pen=pg.mkPen(color='#FF0', width=3))
        # self.plot_item.setLogMode(True, False)
        # self.hist.vb.setLimits(yMin=0, yMax=16000)

        # """
        self.plot_spectrogram = pg.PlotWidget()
        # self.plot_spectrogram.setLabel('left', 'Spectrogram')
        self.plot_spectrogram.setLabel('left', 'Time')
        # self.plot_spectrogram.setLabel('bottom', 'Time')
        self.plot_spectrogram.setLabel('bottom', 'Frequency')
        self.plot_spectrogram.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding))
        self.spectrogram_plot_item = pg.ImageItem()  # use ImageItem instead of plot()
        self.spectrogram_plot_item.setColorMap(pg.colormap.get('viridis'))  # Set the color map for ImageItem
        self.plot_spectrogram.addItem(self.spectrogram_plot_item)  # add the ImageItem to the plot

        # First, add the Spectrum plot
        self.plots_layout.addWidget(self.plot_spectrum)
        # Second, add the Spectrogram plot
        self.plots_layout.addWidget(self.plot_spectrogram)
        # self.plots_layout.addWidget(self.spec_widget)

        groupBox = QGroupBox("Spectrum Setting")
        vbox = QFormLayout()

        vbox.addWidget(QLabel("Main options"))

        vbox.addWidget(QLabel("View:"))
        self.view_select = QComboBox()
        self.view_select.addItem('Spectrum')
        self.view_select.addItem('Spectrogram')
        self.view_select.addItem('Spectrum and Spectrogram')
        self.view_select.currentIndexChanged.connect(self.update_view)
        vbox.addWidget(self.view_select)

        vbox.addWidget(QLabel("Window length:"))
        self.window_length_select = QSpinBox()
        self.window_length_select.setMinimum(1)  # Setting minimum value to 1
        self.window_length_select.setMaximum(99999)  # Setting maximum value to 99999
        self.window_length_select.setValue(self.spectrum_widget.window_length)
        self.window_length_select.valueChanged.connect(self.update_window_length)
        vbox.addWidget(self.window_length_select)

        vbox.addWidget(QLabel("NFFT:"))
        self.NFFT_select = QSpinBox()
        self.NFFT_select.setMinimum(1)  # Setting minimum value to 1
        self.NFFT_select.setMaximum(99999)  # Setting maximum value to 99999
        self.NFFT_select.setValue(self.spectrum_widget.spec_nfft)
        self.NFFT_select.valueChanged.connect(self.update_NFFT)
        vbox.addWidget(self.NFFT_select)

        vbox.addWidget(QLabel("Window options:"))

        vbox.addWidget(QLabel("Overlap (%):"))
        self.Overlap_select = QSpinBox()
        self.Overlap_select.setValue(self.spectrum_widget.overlap)
        self.Overlap_select.valueChanged.connect(self.update_overlap)
        vbox.addWidget(self.Overlap_select)

        vbox.addWidget(QLabel("Window:"))
        self.window_type_select = QComboBox()
        self.window_type_select.addItem('Rectangular')
        self.window_type_select.addItem('Hamming')
        self.window_type_select.addItem('Hann')
        self.window_type_select.setCurrentText(self.spectrum_widget.window_type)
        self.window_type_select.currentIndexChanged.connect(self.update_window_type)
        vbox.addWidget(self.window_type_select)

        groupBox.setLayout(vbox)
        control_layout.addWidget(groupBox)

        self.update_view(self.view_select.currentIndex())

    def update_spectrum(self, val1, val2):
        self.spectrum_plot_item.setData(val1, val2)

    def update_spectrogram(self, spec, f, t):
        try:

            spec_dB = 20 * np.log10(np.maximum(spec, 1e-8))

            # Transpose the data
            # spec_dB = np.transpose(spec_dB)

            # Set image data
            self.spectrogram_plot_item.setImage(spec_dB)

            # Reset the transform and set the correct image rectangle
            # Note the order of parameters in QRectF changed to match the new orientation
            self.spectrogram_plot_item.resetTransform()
            self.spectrogram_plot_item.setRect(QRectF(f[0], 0, f[-1] - f[0], t[-1]))

            # Set axis range
            # self.spectrogram_plot_item.setLimits(yMin=0, yMax=t[-1], xMin=f[0], xMax=f[-1])

        except Exception as e:
            print(f"Error in update_spectrogram(): {str(e)}")

    # def update_spectrogram(self, spec, f, t):
    #     try:
    #         # Convert the amplitude spectrogram to dB scale
    #         spec_dB = 20 * np.log10(np.maximum(spec, 1e-8))
    #
    #         # Create a logarithmic frequency axis
    #         f_log = np.log10(f + 1e-8)  # Add a small value to avoid taking the logarithm of zero
    #
    #         # Compute the difference between logarithmic frequencies for spacing
    #         df_log = f_log[1] - f_log[0]
    #
    #         # Set image data
    #         self.spectrogram_plot_item.setImage(spec_dB, axisOrder='row-major')  # Make sure the data is row-major
    #
    #         # Reset the transform and set the correct image rectangle for the logarithmic y-axis
    #         self.spectrogram_plot_item.resetTransform()
    #         self.spectrogram_plot_item.setRect(QRectF(0, f_log[0], t[-1], df_log * len(f_log)))
    #
    #         # Optional: Set axis range to adjust the view (you can adjust the values as needed)
    #         # self.spectrogram_plot_item.setLimits(yMin=f_log[0], yMax=f_log[-1], xMin=0, xMax=t[-1])
    #
    #     except Exception as e:
    #         print(f"Error in update_spectrogram(): {str(e)}")

    def update_view(self, index):
        self.plot_spectrogram.setVisible(index == 1 or index == 2)
        self.plot_spectrum.setVisible(index == 0 or index == 2)

    def update_window_length(self, value):
        # TODO: Update the window length in your spectrum analysis
        self.spectrum_widget.window_length = value
        self.spectrum_widget.spec_size = int(self.spectrum_widget.spec_nfft // 2 + 1)
        self.spectrum_widget.spec = np.empty((self.spectrum_widget.spec_size, 0))
        # self.NFFT_select.setValue(value)
        # self.spectrum_widget.spec_size = int(self.spectrum_widget.spec_nfft // 2 + 1)
        # self.spectrum_widget.spec = np.empty((self.spectrum_widget.spec_size, 0))

    def update_NFFT(self, value):
        # TODO: Update the window length in your spectrum analysis
        self.spectrum_widget.spec_nfft = value

        # self.window_length_select.setValue(value)
        self.spectrum_widget.spec_size = int(self.spectrum_widget.spec_nfft // 2 + 1)
        self.spectrum_widget.spec = np.empty((self.spectrum_widget.spec_size, 0))

    def update_window_type(self, index):
        if index == 0:
            self.spectrum_widget.window_type = 'Rectangular'
        elif index == 1:
            self.spectrum_widget.window_type = 'Hamming'
        elif index == 2:
            self.spectrum_widget.window_type = 'Hann'

    def update_overlap(self, value):
        # TODO: Update the window type in your spectrum analysis
        self.spectrum_widget.overlap = value
        self.spectrum_widget.spec_size = int(self.spectrum_widget.spec_nfft // 2 + 1)
        self.spectrum_widget.spec = np.empty((self.spectrum_widget.spec_size, 0))



class SpectrumAnalyzerNode(Node):
    title = 'Spectrum Analyzer'
    style = 'large'
    main_widget_class = SpectrumWidget
    main_widget_pos = 'below ports'
    init_inputs = [
        NodeInputBP(),
    ]
    init_outputs = [
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params)
        self.fs = globals.fs
        self.window_type = "Hann"
        self.window_length = globals.frame_size
        self.spec_nfft = globals.frame_size
        self.overlap = 75

    def update_event(self, inp=-1):
        if inp == 0:
            new_samples = self.input(0)
            if new_samples is not None:
                new_samples = new_samples[:-1]  # Remove the last element
                self.main_widget().add_frame(new_samples)


nodes = [
    SpectrumAnalyzerNode,
]
