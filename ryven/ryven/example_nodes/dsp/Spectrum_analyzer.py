import matplotlib
import numpy as np
from pyqtgraph import GraphicsLayoutWidget, ImageItem, ColorBarItem, ColorMap, mkQApp, QtGui, mkPen
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


class MainWindow(QMainWindow):
    def __init__(self, parent_widget):
        super(MainWindow, self).__init__()
        self.parent_widget = parent_widget
        self.frame_size = self.parent_widget.node.frame_size
        self.fs = self.parent_widget.node.fs

        # Central Widget and Layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QHBoxLayout()  # Main layout of the window

        # Layout for the plots
        plotLayout = QVBoxLayout()  # This layout will contain the spectrum and spectrogram group boxes

        # Group Box for Spectrum Plot
        self.spectrumGroupBox = QGroupBox("Spectrum")
        spectrumLayout = QVBoxLayout()
        self.spectrumPlotWidget = pg.PlotWidget()
        self.spectrumPlotWidget.setLabel('left', 'dBm')
        self.spectrumPlotWidget.setLabel('bottom', 'Frequency')
        spectrumLayout.addWidget(self.spectrumPlotWidget)
        self.spectrumGroupBox.setLayout(spectrumLayout)
        plotLayout.addWidget(self.spectrumGroupBox)

        # # Add InfiniteLines to the spectrum plot
        # self.vLine1 = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('r', width=2))
        # self.vLine2 = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('g', width=2))
        # self.hLine1 = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('r', width=2))
        # self.hLine2 = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('g', width=2))

        # self.vLine1.sigDragged.connect(self.onLineMoved)
        # self.vLine2.sigDragged.connect(self.onLineMoved)
        # self.hLine1.sigDragged.connect(self.onLineMoved)
        # self.hLine2.sigDragged.connect(self.onLineMoved)

        # # Set initial position for the lines to make sure they are visible
        # # self.vLine1.setValue(1000)  # Example frequency value
        # # self.vLine2.setValue(2000)  # Example frequency value
        # # self.hLine1.setValue(-100)  # Example dB value
        # # self.hLine2.setValue(-50)  # Example dB value

        # self.spectrumPlotWidget.addItem(self.vLine1)
        # self.spectrumPlotWidget.addItem(self.vLine2)
        # self.spectrumPlotWidget.addItem(self.hLine1)
        # self.spectrumPlotWidget.addItem(self.hLine2)

        # # Create horizontal layout for the difference display and x-axis range widgets
        # info_layout = QHBoxLayout()
        # self.vLineLabel = QLabel('Vertical Difference:')
        # self.hLineLabel = QLabel('Horizontal Difference:')

        # info_layout.addWidget(self.vLineLabel)
        # info_layout.addWidget(self.hLineLabel)

        # spectrumLayout.addLayout(info_layout)

        self.spectrogramGroupBox = QGroupBox("Spectrogram")
        spectrogramLayout = QHBoxLayout()  # Create a layout for the group box

        layoutWidget = GraphicsLayoutWidget()  # Create the GraphicsLayoutWidget

        self.spectrogramPlotWidget = layoutWidget.addPlot(row=0, col=0)
        self.spectrogramPlotWidget.setLabel('left', 'Time')
        self.spectrogramPlotWidget.setLabel('bottom', 'Frequency')
   

        # Spectrogram ImageItem
        self.spectrogram_plot_item = ImageItem()
        # pos = np.linspace(0.0, 1.0, 256)  # 256 is an example, adjust the number of colors as needed
        # color = pg.colormap.get('viridis').getLookupTable(0.0, 1.0, 256)
        color = pg.colormap.get('viridis')

        color_map = pg.colormap.get('viridis')
        lut = color_map.getLookupTable(0.0, 1.0, 256)
        self.spectrogram_plot_item.setLookupTable(lut)
        # self.spectrogram_plot_item.setColorMap(color_map)
        self.spectrogramPlotWidget.addItem(self.spectrogram_plot_item)

        self.bar = pg.ColorBarItem(colorMap=color_map)
        self.bar.setImageItem(self.spectrogram_plot_item)

        layoutWidget.addItem(self.bar, row = 0, col = 1)



        # # Create the ColorBarItem and configure it
        # self.colorbar = ColorBarItem(values=(0, 1), cmap='viridis')  # Adjust the range as per your data
        # self.colorbar.setImageItem(self.spectrogram_plot_item)
        # layoutWidget.addItem(self.colorbar, row=0, col=1)  # Add the color bar next to the spectrogram

        # Add the GraphicsLayoutWidget to the layout of the group box
        spectrogramLayout.addWidget(layoutWidget)
        self.spectrogramGroupBox.setLayout(spectrogramLayout)
        plotLayout.addWidget(self.spectrogramGroupBox)

        # Group Box for Parameters
        self.parametersGroupBox = QGroupBox("Parameters")
        parametersLayout = QFormLayout()

        # # View selection combo box
        # self.view_select = QComboBox()
        # self.view_select.addItem('Spectrum')
        # self.view_select.addItem('Spectrogram')
        # self.view_select.addItem('Spectrum and Spectrogram')
        # parametersLayout.addRow(QLabel("View:"), self.view_select)
        #
        # # Additional parameter widgets
        # # Example: Adding a combo box for 'Input domain'
        # self.inputDomainSelect = QComboBox()
        # self.inputDomainSelect.addItems(['Time', 'Frequency'])  # Add options here as seen in your image
        # parametersLayout.addRow("Input domain:", self.inputDomainSelect)

        # Example: Adding a spin box for 'Sample rate'
        self.sampleRateSpinBox = QSpinBox()
        self.sampleRateSpinBox.setRange(1, 100000)  # Set appropriate range
        self.sampleRateSpinBox.setValue(self.fs)  # Set default value
        parametersLayout.addRow("Sample rate (Hz):", self.sampleRateSpinBox)

        self.windowLengthSpinBox = QSpinBox()
        self.windowLengthSpinBox.setRange(1, 100000)  # Set appropriate range
        self.windowLengthSpinBox.setValue(self.frame_size)  # Set default value
        parametersLayout.addRow("Window length:", self.windowLengthSpinBox)

        self.NFFTSpinBox = QSpinBox()
        self.NFFTSpinBox.setRange(1, 100000)  # Set appropriate range
        self.NFFTSpinBox.setValue(self.frame_size)  # Set default value
        parametersLayout.addRow("NFFT:", self.NFFTSpinBox)

        self.overlapSpinBox = QSpinBox()
        self.overlapSpinBox.setRange(1, 100)  # Set appropriate range
        self.overlapSpinBox.setValue(75)  # Set default value
        parametersLayout.addRow("Overlap(%):", self.overlapSpinBox)

        self.windowSelect = QComboBox()
        self.windowSelect.addItems(['Rectangular', 'Hamming', 'Hann'])  # Add options here as seen in your image
        self.windowSelect.setCurrentText('Hamming')
        parametersLayout.addRow("Input domain:", self.windowSelect)

        self.spectrum_scale = QComboBox()
        self.spectrum_scale.addItems(['Linear', 'Log'])
        self.spectrum_scale.setCurrentText('Linear')
        parametersLayout.addRow("Spectrum scale:", self.spectrum_scale)
        self.parametersGroupBox.setLayout(parametersLayout)

        # Adding group boxes to the main layout
        mainLayout.addLayout(plotLayout)  # Add the plot layout
        mainLayout.addWidget(self.parametersGroupBox)  # Add the parameters group box

        centralWidget.setLayout(mainLayout)


        # Connect the widgets to the update function
        self.sampleRateSpinBox.editingFinished.connect(self.update_plots)
        self.windowLengthSpinBox.editingFinished.connect(self.update_plots)
        self.NFFTSpinBox.editingFinished.connect(self.update_plots)
        self.overlapSpinBox.editingFinished.connect(self.update_plots)
        self.windowSelect.currentIndexChanged.connect(self.update_plots)

        # self.t = None
        self.signal = None

        # self.t = np.linspace(0, 1, self.sampleRateSpinBox.value())
        # self.signal = np.zeros(globals.fs * 1)

        # self.update_plots()  # Initial plot update

        # Initialize the cursor labels
        # self.onLineMoved()
    #
    def update_plots(self):
        fs = self.sampleRateSpinBox.value()
        window_length = self.windowLengthSpinBox.value()
        nfft = self.NFFTSpinBox.value()  # Not used in welch
        overlap = self.overlapSpinBox.value()
        window_type = self.windowSelect.currentText()

        # # Create the signal
        # t = np.linspace(0, 1, fs)
        # sin_wave = 1500 * np.sin(2 * np.pi * 1000 * t) + 3000 * np.sin(2 * np.pi * 1500 * t)
        if self.signal is not None:
            # Compute the spectrum
            self.plot_spectrum(self.signal[-self.frame_size:], fs, window_length, nfft,  overlap, window_type)

            # Compute the spectrogram
            self.plot_spectrogram(self.signal, fs, window_length, nfft,  overlap, window_type)

    # def onLineMoved(self):
    #     # Retrieve the current positions of the vertical and horizontal lines
    #     vLinePos1 = self.vLine1.value()
    #     vLinePos2 = self.vLine2.value()
    #     hLinePos1 = self.hLine1.value()
    #     hLinePos2 = self.hLine2.value()

    #     # Calculate the differences in positions
    #     vertical_difference = abs(vLinePos1 - vLinePos2)
    #     horizontal_difference = abs(hLinePos1 - hLinePos2)

    #     # CSS style for the labels
    #     label_style = """
    #             QLabel {
    #                 background-color: #444; /* Dark background for contrast */
    #                 color: white; /* Bright text color for readability */
    #                 border: 1px solid #FFF; /* White border */
    #                 border-radius: 4px; /* Rounded corners */
    #                 padding: 4px; /* Some padding around the text */
    #                 font-weight: bold; /* Make the font bold */
    #                 font-size: 20px; /* Increase the font size */
    #             }
    #             """

    #     # Update the labels with the differences, applying the CSS style
    #     self.vLineLabel.setStyleSheet(label_style)
    #     self.vLineLabel.setText(f'Vertical Difference: {vertical_difference:.4f}')

    #     self.hLineLabel.setStyleSheet(label_style)
    #     self.hLineLabel.setText(f'Horizontal Difference: {horizontal_difference:.4f}')

    def plot_spectrum(self, signal, fs, window_length, nfft, overlap, window_type):
        # Compute the Power Spectral Density using Welch's method
        if self.spectrum_scale.currentText() == "Log":
            self.spectrumPlotWidget.getPlotItem().setLogMode(x=True, y=False)  # Set x-axis to logarithmic scale
        else:
            self.spectrumPlotWidget.getPlotItem().setLogMode(x=False, y=False)  # Set x-axis to logarithmic scale

        try:
            if window_type == "Hamming":
                # window = hamming(window_length)  # Hamming window
                window = 'hamming'
                try:
                    frequencies, spectrum = welch(signal, fs=fs, window=window, nfft=nfft, nperseg=window_length, noverlap=int(window_length*overlap / 100), scaling="spectrum")
                    # frequencies, spectrum = welch(signal, fs=fs, window=window, nfft=nfft, noverlap=int(window_length*overlap / 100))

                except Exception as e:
                    print(f"Error in computing spectrogram: {e}")
                self.spectrumPlotWidget.clear()
                spectrum_dB = 20 * np.log10(np.abs(spectrum))
                yellow_pen = mkPen(color='y')
                self.spectrumPlotWidget.plot(frequencies, spectrum_dB, pen=yellow_pen)
                self.spectrogramPlotWidget.setXRange(20, fs/2)
                
                # if self.spectrum_scale.currentText() == "Linear":
                #     self.spectrumPlotWidget.addItem(self.vLine1)
                #     self.spectrumPlotWidget.addItem(self.vLine2)
                #     self.spectrumPlotWidget.addItem(self.hLine1)
                #     self.spectrumPlotWidget.addItem(self.hLine2)
            elif window_type == "Hann":
                # window = hann(window_length)  # Hamming window
                window = 'hann'
                frequencies, spectrum = welch(signal, fs=fs, window=window, nfft=nfft, nperseg=window_length, noverlap=int(window_length*overlap / 100), scaling="spectrum")
                self.spectrumPlotWidget.clear()
                spectrum_dB = 20 * np.log10(np.abs(spectrum))
                yellow_pen = mkPen(color='y')
                self.spectrumPlotWidget.plot(frequencies, spectrum_dB, pen=yellow_pen)
                self.spectrogramPlotWidget.setXRange(20, fs/2)

                # if self.spectrum_scale.currentText() == "Linear":
                #     self.spectrumPlotWidget.addItem(self.vLine1)
                #     self.spectrumPlotWidget.addItem(self.vLine2)
                #     self.spectrumPlotWidget.addItem(self.hLine1)
                #     self.spectrumPlotWidget.addItem(self.hLine2)

            elif window_type == "Rectangular":
                window = np.ones(window_length)  # Hamming window
                frequencies, spectrum = welch(signal, fs=fs, window=window, nfft=nfft, nperseg=window_length, noverlap=int(window_length*overlap / 100), scaling="spectrum")
                self.spectrumPlotWidget.clear()
                spectrum_dB = 20 * np.log10(np.abs(spectrum))
                yellow_pen = mkPen(color='y')
                self.spectrumPlotWidget.plot(frequencies, spectrum_dB, pen=yellow_pen)
                self.spectrogramPlotWidget.setXRange(20, fs/2)

                # if self.spectrum_scale.currentText() == "Linear":
                #     self.spectrumPlotWidget.addItem(self.vLine1)
                #     self.spectrumPlotWidget.addItem(self.vLine2)
                #     self.spectrumPlotWidget.addItem(self.hLine1)
                #     self.spectrumPlotWidget.addItem(self.hLine2)
            else:
                self.spectrumPlotWidget.clear()

        except Exception as e:
            print(f"Error in computing spectrum: {e}")

    #
    import numpy as np
    from scipy.signal import stft

    def plot_spectrogram(self, signal, fs, window_length, nfft, overlap, window_type):
        try:
            if window_type == "Hamming":
                window = 'hamming'
            elif window_type == "Hann":
                window = 'hann'  # Hamming windoww
            elif window_type == "Rectangular":
                window = np.ones(window_length)  # Hamming window


            # Calculating noverlap as the number of samples
            noverlap_samples = int(window_length * overlap / 100)

            # Compute the STFT
            frequencies, times, Zxx = stft(signal, fs, window=window, nperseg=window_length, noverlap=noverlap_samples, nfft=nfft)

            # Compute the magnitude (spectrogram)
            Sxx = np.abs(Zxx)

            # Convert to dB scale for visualization
            spec_dB = 10 * np.log10(Sxx + np.finfo(float).eps)

            # Update the ImageView widget with the spectrogram data
            self.spectrogram_plot_item.setImage(spec_dB)

            # Reset the transform and set the correct image rectangle
            self.spectrogram_plot_item.resetTransform()
            # self.spectrogram_plot_item.setRect(
            #     QRectF(times[0], frequencies[0], times[-1] - times[0], frequencies[-1] - frequencies[0]))
            self.spectrogram_plot_item.setRect(
                QRectF(20, times[0], frequencies[-1] - 20, times[-1] - times[0]))

            # Create the ColorBarItem and configure it

            # Update the ColorBarItem with the new range
            self.bar.setLevels((np.min(spec_dB), np.max(spec_dB)))

            # Since the spectrogram might have a different scale now, we need to update the color bar as well
            colorMap = pg.colormap.get('viridis')
            lut = colorMap.getLookupTable(0.0, 1.0, 256)
            self.spectrogram_plot_item.setLookupTable(lut)



        except Exception as e:
            print(f"Error in computing spectrogram: {e}")

    def get_current_params(self):
        self.current_filter_params = {
            'window_type': self.windowSelect.currentText(),
            'window_length': self.windowLengthSpinBox.value(),
            'spec_nfft': self.NFFTSpinBox.value(),
        }
        return self.current_filter_params


class SpectrumWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.fs = self.node.fs
        self.window_type = self.node.window_type
        self.window_length = self.node.window_length
        self.spec_nfft = self.node.spec_nfft

        print(self.fs)
        print(self.window_type)
        print(self.window_length)
        print(self.spec_nfft)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "new_spectrum_icon.png")
        image = QPixmap(icon_path)
        imageLabel.setPixmap(image)
        imageLabel.setStyleSheet("background-color: white;")
        layout.addWidget(imageLabel)
        self.setLayout(layout)

        self.mainWindow = MainWindow(self)

        self.mainWindow.sampleRateSpinBox.setValue(self.fs)
        self.mainWindow.windowLengthSpinBox.setValue(self.window_length)
        self.mainWindow.NFFTSpinBox.setValue(self.spec_nfft)
        self.mainWindow.windowSelect.setCurrentText(self.window_type)

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
        try:
            self.mainWindow.show()
            if self.mainWindow.isMinimized():
                # If the window is minimized, restore it to its normal size
                self.mainWindow.setWindowState(self.mainWindow.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

                # Bring the window to the front and activate it
            self.mainWindow.raise_()
            self.mainWindow.activateWindow()
        except Exception as e:
            print(e)

    def add_frame(self, frame):
        self.mainWindow.signal = frame
        self.mainWindow.update_plots()

    def gets_parameters(self):
        return self.mainWindow.get_current_params()


class SpectrumAnalyzer(Node):
    title = 'Spectrum Analyzer'
    style = 'large'
    main_widget_class = SpectrumWidget
    main_widget_pos = 'between ports'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "new_spectrum_icon.png")
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
        self.window_type = "Hamming"
        self.window_length = self.frame_size
        self.spec_nfft = self.frame_size
        self.overlap = 75
        self.last_5_seconds_buffer = np.zeros(self.fs * 5)
        self.counter = 1

    def update_event(self, inp=-1):
        if inp == 0:
            new_samples = self.input(0)
            if new_samples is not None:
                new_samples = new_samples[:-1]  # Remove the last element
                self.last_5_seconds_buffer = np.roll(self.last_5_seconds_buffer, -len(new_samples))
                self.last_5_seconds_buffer[-len(new_samples):] = new_samples
                if self.counter % 2 == 0:
                    self.main_widget().add_frame(self.last_5_seconds_buffer)
                self.counter = self.counter + 1
        # if inp == 0:
        #     new_samples = self.input(0)
        #     if new_samples is not None:
        #         new_samples = new_samples[:-1]  # Remove the last element
        #         self.main_widget().add_frame(new_samples)
        # pass

    def get_state(self) -> dict:
        data_parameters = self.main_widget().gets_parameters()
        return {
            'window_type': data_parameters['window_type'],
            'window_length': data_parameters['window_length'],
            'spec_nfft': data_parameters['spec_nfft'],
        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.window_type = data['window_type']
        self.window_length = data['window_length']
        self.spec_nfft = data['spec_nfft']

        print(data['amp'])
        print(data['freq'])
        print(data['type'])


nodes = [
    SpectrumAnalyzer,
]