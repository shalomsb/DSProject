import matplotlib
import numpy as np
import scipy
import matplotlib.pyplot as plt
# import scipy
# from qtpy.QtGui import QPixmap, QDoubleValidator
from qtpy.QtWidgets import QWidget, QPushButton, QLabel, QMainWindow, QVBoxLayout, QToolBar, QComboBox, QMenuBar, QMenu, \
    QActionGroup, QAction, QToolButton, QWidgetAction, QSpinBox, QHBoxLayout, QSizePolicy, QGroupBox, QFormLayout, QLineEdit
from ryven.NENV import *
from ryven.NWENV import *
from scipy.interpolate import interp2d, interp1d
from scipy.io import wavfile
from scipy.signal import spectrogram, stft, windows, welch
import globals
import pyqtgraph as pg
from PySide2.QtCore import QRectF, QTimer
from PySide2.QtCore import QTimer  # Import QTimer
from scipy.signal.windows import hann, hamming

from qtpy.QtGui import QPixmap, QFont
from qtpy.QtCore import Qt
from scipy.signal.windows import hann, hamming
from scipy.signal.windows import get_window
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import LogFormatter



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.counter = 1

        # Central Widget and Layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QHBoxLayout()  # Main layout of the window

        # Layout for the plots
        plotLayout = QVBoxLayout()  # This layout will contain the spectrum and spectrogram group boxes

        # Group Box for Spectrum Plot
        self.spectrumGroupBox = QGroupBox("Spectrum")
        spectrumLayout = QVBoxLayout()

        # Matplotlib Spectrum Plot
        self.spectrumFigure = Figure()
        self.spectrumCanvas = FigureCanvas(self.spectrumFigure)
        self.spectrumCanvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.spectrumCanvas.updateGeometry()
        self.spectrumAxes = self.spectrumFigure.add_subplot(111)
        self.spectrumAxes.set_ylabel('dBm')
        self.spectrumAxes.set_xlabel('Frequency [Hz]')
        self.spectrumAxes.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5)


        # Set the background color of the figure and axes
        self.spectrumFigure.patch.set_facecolor('black')  # Set figure background to black
        self.spectrumAxes.set_facecolor('black')          # Set axes background to black

        # Ensure that labels and titles are visible on a black background
        self.spectrumAxes.xaxis.label.set_color('white')
        self.spectrumAxes.yaxis.label.set_color('white')
        self.spectrumAxes.title.set_color('white')
        self.spectrumAxes.tick_params(axis='x', colors='white')
        self.spectrumAxes.tick_params(axis='y', colors='white')

        # self.spectrumAxes.set_xscale('log')
        spectrumLayout.addWidget(self.spectrumCanvas)
        self.spectrumGroupBox.setLayout(spectrumLayout)
        plotLayout.addWidget(self.spectrumGroupBox)

        # Info labels
        info_layout = QHBoxLayout()
        self.vLineLabel = QLabel('Vertical Difference:')
        self.hLineLabel = QLabel('Horizontal Difference:')
        info_layout.addWidget(self.vLineLabel)
        info_layout.addWidget(self.hLineLabel)
        spectrumLayout.addLayout(info_layout)

        # Group Box for Spectrogram Plot
        self.spectrogramGroupBox = QGroupBox("Spectrogram")
        spectrogramLayout = QVBoxLayout()

        # Matplotlib Spectrogram Plot
        self.spectrogramFigure = Figure()
        self.spectrogramCanvas = FigureCanvas(self.spectrogramFigure)
        self.spectrogramCanvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.spectrogramCanvas.updateGeometry()
        self.spectrogramAxes = self.spectrogramFigure.add_subplot(111)
        self.spectrogramAxes.set_ylabel('Time [sec]')
        self.spectrogramAxes.set_xlabel('Frequency [Hz]')
        self.spectrogramAxes.grid(True, which='both', color='gray', linestyle='-', linewidth=1)

        # Set the background color of the figure and axes
        self.spectrogramFigure.patch.set_facecolor('black')  # Set figure background to black
        self.spectrogramAxes.set_facecolor('black')          # Set axes background to black

        # Ensure that labels and titles are visible on a black background
        self.spectrogramAxes.xaxis.label.set_color('white')
        self.spectrogramAxes.yaxis.label.set_color('white')
        self.spectrogramAxes.title.set_color('white')
        self.spectrogramAxes.tick_params(axis='x', colors='white')
        self.spectrogramAxes.tick_params(axis='y', colors='white')

        # self.spectrogramAxes.set_xscale('log')
        spectrogramLayout.addWidget(self.spectrogramCanvas)
        self.spectrogramGroupBox.setLayout(spectrogramLayout)

        plotLayout.addWidget(self.spectrogramGroupBox)

        # Group Box for Parameters
        self.parametersGroupBox = QGroupBox("Parameters")
        parametersLayout = QFormLayout()


        # Example: Adding a spin box for 'Sample rate'
        self.sampleRateSpinBox = QSpinBox()
        self.sampleRateSpinBox.setRange(1, 100000)  # Set appropriate range
        self.sampleRateSpinBox.setValue(globals.fs)  # Set default value
        parametersLayout.addRow("Sample rate (Hz):", self.sampleRateSpinBox)

        self.windowLengthSpinBox = QSpinBox()
        self.windowLengthSpinBox.setRange(1, 100000)  # Set appropriate range
        self.windowLengthSpinBox.setValue(globals.frame_size)  # Set default value
        parametersLayout.addRow("Window length:", self.windowLengthSpinBox)

        self.NFFTSpinBox = QSpinBox()
        self.NFFTSpinBox.setRange(1, 100000)  # Set appropriate range
        self.NFFTSpinBox.setValue(globals.frame_size)  # Set default value
        parametersLayout.addRow("NFFT:", self.NFFTSpinBox)

        self.overlapSpinBox = QSpinBox()
        self.overlapSpinBox.setRange(1, 100)  # Set appropriate range
        self.overlapSpinBox.setValue(75)  # Set default value
        parametersLayout.addRow("Overlap(%):", self.overlapSpinBox)

        self.windowSelect = QComboBox()
        self.windowSelect.addItems(['Rectangular', 'Hamming', 'Hann'])  # Add options here as seen in your image
        self.windowSelect.setCurrentText('Hamming')
        parametersLayout.addRow("Window:", self.windowSelect)

        self.spectrum_scale = QComboBox()
        self.spectrum_scale.addItems(['Linear', 'Log'])
        self.spectrum_scale.setCurrentText('Linear')
        parametersLayout.addRow("Spectrum scale:", self.spectrum_scale)
        self.parametersGroupBox.setLayout(parametersLayout)

        # Adding group boxes to the main layout
        mainLayout.addLayout(plotLayout)  # Add the plot layout
        mainLayout.addWidget(self.parametersGroupBox)  # Add the parameters group box

        centralWidget.setLayout(mainLayout)

        fs = self.sampleRateSpinBox.value()
        window_length = self.windowLengthSpinBox.value()
        overlap = self.overlapSpinBox.value()
        noverlap = int(overlap / 100 * window_length)
        nfft = self.NFFTSpinBox.value()
        
        signal_init = np.zeros(int(fs*1)) + 1e-7

        f, t, Sxx = spectrogram(signal_init, fs, window="hamming", nperseg=window_length, noverlap=noverlap, nfft=nfft)
        Sxx_dB = 10 * np.log10(Sxx)

        # Filter out frequencies below 20 Hz
        valid_indices = f >= 20
        f_filtered = f[valid_indices]
        Sxx_dB_filtered = Sxx_dB[valid_indices, :]

        # Initial plot with imshow
        extent = [f_filtered.min(), f_filtered.max(), t.min(), t.max()]
        # Use the jet colormap
        cmap = plt.get_cmap("jet")

        self.spec = self.spectrogramAxes.imshow(Sxx_dB_filtered.T, aspect='auto', extent=extent, origin='lower',
                                                cmap=cmap)
        # self.spec = self.spectrogramAxes.imshow(Sxx_dB_filtered.T, aspect='auto', extent=extent, origin='lower', cmap="jet")

        # Colorbar setup
        self.colorbar = self.spectrogramFigure.colorbar(self.spec, ax=self.spectrogramAxes, orientation='horizontal')
        self.colorbar.ax.tick_params(colors='white')

        self.current_scale = "linear"

        self.spectrumLine, = self.spectrumAxes.plot([], [], 'r')  # Initialize an empty line

    def plot_spectrum(self, signal):
        fs = self.sampleRateSpinBox.value()
        window_length = self.windowLengthSpinBox.value()
        window = self.windowSelect.currentText().lower()
        # if window == "hamming":
        #     window = hamming(window_length)
        # elif window == "hann":
        #     window = hann(window_length)
        # else:
        #     window = windows.boxcar(window_length)
        overlap = self.overlapSpinBox.value()
        noverlap = int(overlap / 100 * window_length)
        nfft = self.NFFTSpinBox.value()
        f, Pxx = welch(signal, fs, window=window, nperseg=window_length, nfft=nfft, noverlap=noverlap,
                       scaling='spectrum')
        Pxx_dB = 10 * np.log10(Pxx * 1000)

        # Filter out frequencies below 20 Hz
        valid_indices = f >= 20
        f = f[valid_indices]
        Pxx_dB = Pxx_dB[valid_indices]

        if self.spectrumLine is None or not hasattr(self, 'spectrumLine'):
            # Initialize the line if it does not exist with yellow color
            self.spectrumLine, = self.spectrumAxes.plot(f, Pxx_dB, color='yellow')
        else:
            # Update data of the existing line and ensure it's yellow
            self.spectrumLine.set_data(f, Pxx_dB)
            self.spectrumLine.set_color('yellow')  # Set line color to yellow

        if self.spectrum_scale.currentText() == "Linear":
            self.spectrumAxes.set_xscale('linear')
        else:
            self.spectrumAxes.set_xscale('log')

        self.spectrumAxes.relim()  # Recompute the ax.dataLim
        self.spectrumAxes.autoscale_view()  # Update ax.viewLim using the new dataLim
        self.spectrumCanvas.draw_idle()

    # def plot_spectrogram(self, signal):
    #     fs = self.sampleRateSpinBox.value()
    #     window_length = self.windowLengthSpinBox.value()
    #     window = self.windowSelect.currentText().lower()
    #     overlap = self.overlapSpinBox.value()
    #     noverlap = int(overlap / 100 * window_length)
    #     nfft = self.NFFTSpinBox.value()

    #     # Calculate the spectrogram
    #     f, t, Sxx = spectrogram(signal, fs, window=window, nperseg=window_length, noverlap=noverlap, nfft=nfft)
    #     Sxx_dB = 10 * np.log10(Sxx)

    #     # Filter out frequencies below 20 Hz
    #     valid_indices = f >= 20
    #     f_filtered = f[valid_indices]
    #     Sxx_dB_filtered = Sxx_dB[valid_indices, :]

    #     # Clear the previous spectrogram
    #     self.spectrogramAxes.clear()

    #     # Plot the filtered spectrogram data
    #     extent = [f_filtered.min(), f_filtered.max(), t.min(), t.max()]
    #     # extent = [20, 8000, 0, 5]
    #     self.spec = self.spectrogramAxes.imshow(Sxx_dB_filtered.T, aspect='auto', extent=extent, origin='lower', cmap="jet")
    #     # self.spec = self.spectrogramAxes.pcolormesh(f_filtered, t, Sxx_dB_filtered.T, shading='auto')

    #     # Setting labels and scales
    #     self.spectrogramAxes.set_xlabel('Frequency [Hz]')
    #     self.spectrogramAxes.set_ylabel('Time [sec]')
    #     self.spectrogramAxes.xaxis.label.set_color('white')
    #     self.spectrogramAxes.yaxis.label.set_color('white')
    #     self.spectrogramAxes.grid(True, which='both', color='gray', linestyle='-', linewidth=1)

    #     if self.spectrum_scale.currentText() == "Linear":
    #         self.spectrogramAxes.set_xscale('linear')
    #     else:
    #         self.spectrogramAxes.set_xscale('log')

    #     # Update or create the colorbar
    #     if hasattr(self, 'colorbar') and self.colorbar:
    #         self.colorbar.update_normal(self.spec)
    #     else:
    #         self.colorbar = self.spectrogramFigure.colorbar(self.spec, ax=self.spectrogramAxes)

    #     # Redraw the canvas
    #     self.spectrogramCanvas.draw_idle()
    
    def plot_spectrogram(self, signal):
        fs = self.sampleRateSpinBox.value()
        window_length = self.windowLengthSpinBox.value()
        window = self.windowSelect.currentText().lower()
        if window == "hamming":
            window = hamming(window_length)
        elif window == "hann":
            window = hann(window_length)
        else:
            window = windows.boxcar(window_length)
        overlap = self.overlapSpinBox.value()
        noverlap = int(overlap / 100 * window_length)
        nfft = self.NFFTSpinBox.value()

        # Calculate the spectrogram
        f, t, Sxx = spectrogram(signal, fs, window=window, nperseg=window_length, noverlap=noverlap, nfft=nfft)
        Sxx_dB = 10 * np.log10(Sxx)

        # Filter out frequencies below 20 Hz
        valid_indices = f >= 20
        f_filtered = f[valid_indices]
        Sxx_dB_filtered = Sxx_dB[valid_indices, :]

        if not hasattr(self, 'spec'):
            # If this is the first run, initialize the spectrogram plot
            extent = [f_filtered.min(), f_filtered.max(), t.min(), t.max()]
            cmap = plt.get_cmap("jet")
            self.spec = self.spectrogramAxes.imshow(Sxx_dB_filtered.T, aspect='auto', extent=extent, origin='lower', cmap=cmap)
            self.colorbar = self.spectrogramFigure.colorbar(self.spec, ax=self.spectrogramAxes)
        else:
            # Update the data of the existing spectrogram
            self.spec.set_data(Sxx_dB_filtered.T)
            self.spec.set_clim(vmin=Sxx_dB_filtered.min(), vmax=Sxx_dB_filtered.max())
        
        # Set log scale for frequency axis if required
        if self.spectrum_scale.currentText() == "Log":
            self.spectrogramAxes.set_xscale('log')
        else:
            self.spectrogramAxes.set_xscale('linear')

        # Redraw only the parts that have changed
        self.spectrogramCanvas.draw_idle()

        # Adjust extent if necessary
        extent = [f_filtered.min(), f_filtered.max(), t.min(), t.max()]
        self.spec.set_extent(extent)

        # Update colorbar
        self.colorbar.update_normal(self.spec)



    
    def get_current_params(self):
        self.current_filter_params = {
            'window_type': self.windowSelect.currentText(),
            'window_length': self.windowLengthSpinBox.value(),
            'spec_nfft': self.NFFTSpinBox.value(),
        }
        return self.current_filter_params


class SpectrumWidget(MWB, QWidget):
    def __init__(self, params):
        try:
            MWB.__init__(self, params)
            QWidget.__init__(self)
            self.fs = self.node.fs
            self.window_type = self.node.window_type
            self.window_length = self.node.window_length
            self.spec_nfft = self.node.spec_nfft

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
            imageLabel = QLabel()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "icons", "new_spectrum_icon.png")
            image = QPixmap(icon_path).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            imageLabel.setPixmap(image)
            imageLabel.setStyleSheet("background-color: white;")
            layout.addWidget(imageLabel)
            self.setLayout(layout)

            self.mainWindow = MainWindow()

            self.mainWindow.sampleRateSpinBox.setValue(self.fs)
            self.mainWindow.windowLengthSpinBox.setValue(self.window_length)
            self.mainWindow.NFFTSpinBox.setValue(self.spec_nfft)
            self.mainWindow.windowSelect.setCurrentText(self.window_type)

            self.click_timer = QTimer(self)
            self.click_timer.setSingleShot(True)
            self.click_timer.timeout.connect(self.singleClickAction)

            self.click_count = 0

            self.counter = 0
        except Exception as e:
            print(e)

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
        try:
            self.mainWindow.show()
        except Exception as e:
            print(e)

    def update_signal(self, signal):
        if self.counter % 4 == 0:
            self.mainWindow.plot_spectrogram(signal)
        self.mainWindow.plot_spectrum(signal[-self.window_length:])
        self.counter+=1

    def gets_parameters(self):
        return self.mainWindow.get_current_params()


class SpectrumAndSpectrogramAnalyzer(Node):
    title = 'Spectrum Analyzer'
    style = 'large'
    main_widget_class = SpectrumWidget
    main_widget_pos = 'between ports'
    init_inputs = [
        NodeInputBP(),
    ]
    init_outputs = [
    ]
    color = '#5d95de'

    def __init__(self, params):
        try:
            super().__init__(params)
            self.fs = self.get_var_val("fs")
            if self.fs is None:
                print("fs from globals")
                self.fs = globals.fs
            self.frame_size = self.get_var_val("frame_size")
            if self.frame_size is None:
                print("frame size from globals")
                self.frame_size = globals.frame_size
            self.window_type = "Hamming"
            self.window_length = self.frame_size
            self.spec_nfft = self.frame_size
            self.overlap = 75
            self.signal = np.zeros(int(self.fs*1))
        except Exception as e:
            print(e)
            print("1")

    def update_event(self, inp=-1):
        if inp == 0:
            new_samples = self.input(0)
            if new_samples is not None:
                try:
                    new_samples = new_samples[:-1]  # Remove the last element
                    self.signal = np.roll(self.signal, -len(new_samples))
                    self.signal[-len(new_samples):] = new_samples
                    self.main_widget().update_signal(self.signal)
                except Exception as e:
                    print(e)
                    print("2")


    # def get_state(self) -> dict:
    #     data_parameters = self.main_widget().gets_parameters()
    #     return {
    #         'window_type': data_parameters['window_type'],
    #         'window_length': data_parameters['window_length'],
    #         'spec_nfft': data_parameters['spec_nfft'],
    #     }

    # def set_state(self, data: dict, version):
    #     print("set_state called with data:", data)
    #     self.window_type = data['window_type']
    #     self.window_length = data['window_length']
    #     self.spec_nfft = data['spec_nfft']

    #     print(data['amp'])
    #     print(data['freq'])
    #     print(data['type'])


nodes = [
    SpectrumAndSpectrogramAnalyzer,
]