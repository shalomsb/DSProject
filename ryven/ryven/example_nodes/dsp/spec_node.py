# import matplotlib.pyplot as plt
import numpy as np
# import scipy
# from qtpy.QtGui import QPixmap, QDoubleValidator
from qtpy.QtWidgets import QWidget, QPushButton, QLabel, QMainWindow, QVBoxLayout, QToolBar, QComboBox, QMenuBar, QMenu, \
    QActionGroup, QAction, QToolButton, QWidgetAction
from ryven.NENV import *
from ryven.NWENV import *
from scipy.signal import spectrogram, stft, windows

import pyqtgraph as pg
# from qtpy.QtCore import Qt, QTimer
# from functools import partial
# import globals
from PySide2.QtCore import QRectF
from qtpy.QtGui import QPixmap
from qtpy.QtCore import Qt


class SpectrogramPlotWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.frame_counter = 0

        # Create custom axis items for time and frequency
        time_axis = pg.AxisItem(orientation='bottom')
        time_axis.setLabel('Time', units='s')
        freq_axis = pg.AxisItem(orientation='left')
        freq_axis.setLabel('Frequency', units='Hz')

        # Create a PlotItem with custom axes
        self.plot_item = pg.PlotItem(axisItems={'bottom': time_axis, 'left': freq_axis})
        self.spec_item = pg.ImageItem()
        # Apply the 'viridis' colormap
        self.spec_item.setColorMap(pg.colormap.get('viridis'))
        self.plot_item.addItem(self.spec_item)

        # Set up color map
        self.spec_widget = pg.GraphicsLayoutWidget()
        self.spec_widget.addItem(self.plot_item)

        self.main = QMainWindow()
        self.main.setWindowTitle("Spec")
        self.main.setCentralWidget(self.spec_widget)

        layout = QVBoxLayout()
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "spectrogram.png")
        image = QPixmap(icon_path).scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        # self.setLayout(layout)

        # layout = QVBoxLayout()
        # showSpecButton = QPushButton("Show Spec")
        #
        # layout.addWidget(showSpecButton)
        self.setLayout(layout)

        self.spec_signal = np.array([])
        self.spec_window = 16000 * 4
        self.spec_noverlap = np.round(1024 * 0.75)
        self.spec_nfft = 1024
        self.window_hann = windows.hann(self.spec_nfft)

        self.spec = np.empty((513, 0))

    # Update the update_spectrogram function to use spec_item
    def update_spectrogram(self, spec, f, t):
        try:
            spec_dB = 20 * np.log10(spec)

            # Set image data
            self.spec_item.setImage(spec_dB.T)
            #
            # # Compute frequency and time step size
            # freq_step = f[1] - f[0]
            # time_step = t[1] - t[0]

            # Reset the transform and set the correct image rectangle
            self.spec_item.resetTransform()
            self.spec_item.setRect(QRectF(0, f[0], t[-1], f[-1] - f[0]))

            # Set axis range
            self.plot_item.setLimits(xMin=0, xMax=t[-1], yMin=f[0], yMax=f[-1])

        except Exception as e:
            print(f"Error in update_spectrogram(): {str(e)}")

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        self.window1()

    def window1(self):
        self.main.show()

    def add_frame(self, frame):
        self.spec_signal = np.concatenate((self.spec_signal, frame))

        # Compute the spectrogram
        # f, t, spec = spectrogram(self.spec_signal[-1792:], fs=16000, window='hann', nperseg=self.spec_nfft,
        #                          noverlap=self.spec_noverlap)
        f, t, spec = stft(self.spec_signal[-1792:], fs=16000, nperseg=self.spec_nfft, noverlap=self.spec_noverlap,
                          window=self.window_hann, padded=False,
                          boundary=None)
        spec = np.abs(spec) ** 2
        # Update the combined spectrogram
        self.spec = np.concatenate((self.spec[:, :], spec), axis=1)
        # self.spec = np.concatenate((self.spec[:, :-1], spec), axis=1)
        self.spec = self.spec[:, -265:]

        # Compute the frequency and time arrays
        f = np.fft.fftfreq(self.spec_nfft, 1 / 16000)[:self.spec_nfft // 2]
        t = np.arange(self.spec.shape[1]) * (self.spec_nfft - self.spec_noverlap) / 16000
        self.update_spectrogram(self.spec, f, t)


class SpectrogramNode(Node):
    title = 'TRAINSPEC'
    main_widget_class = SpectrogramPlotWidget
    main_widget_pos = 'below ports'
    init_inputs = [
        NodeInputBP(label='samples:'),
    ]
    init_outputs = [
        NodeOutputBP(label='spectrogram'),
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params)

    def update_event(self, inp=-1):
        if inp == 0:
            new_samples = self.input(0)
            if new_samples is not None:
                self.main_widget().add_frame(new_samples)


nodes = [
    SpectrogramNode,
]
