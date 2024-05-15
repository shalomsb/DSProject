# import matplotlib.pyplot as plt
import librosa
import numpy as np
# import scipy
# from qtpy.QtGui import QPixmap, QDoubleValidator
from qtpy.QtWidgets import QWidget, QPushButton, QLabel, QMainWindow, QVBoxLayout, QToolBar, QComboBox, QMenuBar, QMenu, \
    QActionGroup, QAction, QToolButton, QWidgetAction
from ryven.NENV import *
from ryven.NWENV import *
from scipy.signal import spectrogram, stft, windows
from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

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

        self.main = QMainWindow()
        self.main.setWindowTitle("Spectrogram")

        # Create a Matplotlib figure and add it to the widget
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

        # Use the canvas as the central widget in the main window
        self.main.setCentralWidget(self.canvas)

        layout = QVBoxLayout()
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "spectrogram.png")
        image = QPixmap(icon_path).scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        self.setLayout(layout)

        # Initial drawing of the plot
        signal_init = np.zeros(1024*62)+1e-7

        f, t, Zxx = stft(signal_init, fs=16000, window='hamming', nperseg=1024, padded=False,
                                        boundary=None, noverlap=768)
        self.ax.set_yscale('log')
        self.spec = self.ax.pcolormesh(t, f, 20 * np.log10(np.abs(Zxx) ** 2), cmap='viridis')  # example shape, adjust as needed
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)



    def update_spectrogram(self, spec, f, t):

        try:
            # Offset to avoid log(0)
            spec = np.abs(spec) + 1e-7
            spec = 20 * np.log10(spec)
            spec = np.nan_to_num(spec, nan=np.nanmin(spec), posinf=np.nanmax(spec), neginf=np.nanmin(spec))

            # Convert frequency values to logarithmic scale, avoid log(0)
            f_log = np.log10(f + 1e-7)

            # Update the spectrogram plot
            self.spec.set_array(spec.ravel())

            # Set the y-axis to logarithmic scale
            self.ax.set_yscale('log')

            # Adjust the y-axis limits to the log-scaled frequencies
            self.ax.set_ylim(f[1], f[-1])  # exclude 0 Hz if it's in the array

            # Update color limits if needed
            self.spec.set_clim(vmin=spec.min(), vmax=spec.max())

            # Blit drawing
            self.canvas.restore_region(self.background)
            self.ax.draw_artist(self.spec)
            self.canvas.blit(self.ax.bbox)

        except Exception as e:
            print(str(e))
        # try:
        #     # Clear the current axes
        #     self.ax.clear()
        #
        #     # Plot the spectrogram
        #     # Assuming spec shape is (513, N), transpose may be required
        #     # spec = spec.T if spec.shape[0] != len(f) else spec
        #     self.ax.pcolormesh(t, f, 20 * np.log10(np.abs(spec) ** 2), shading='gouraud',
        #                    cmap='viridis')
        #
        #     # Set labels and titles as needed
        #     self.ax.set_xlabel('Time [sec]')
        #     self.ax.set_ylabel('Frequency [Hz]')
        #     self.ax.set_title('Spectrogram')
        #
        #     # Draw the canvas again
        #     self.canvas.draw()
        # except Exception as e:
        #     print(str(e))
        #     print("blabla")

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        self.window1()

    def window1(self):
        self.main.show()

    def add_frame(self, spec, f, t):
        try:
            # f = librosa.fft_frequencies(sr=16000, n_fft=1024)
            # t = librosa.frames_to_time(np.arange(spec.shape[1]), sr=16000, hop_length=1024 - 768,
            #                                      n_fft=1024)
            self.update_spectrogram(spec, f, t)
        except Exception as e:
            print(e)
            print("here")

class SpectrogramNode1(Node):
    title = 'Shalom'
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
        self.signal = np.zeros(1024*62)
        self.f, self.t, self.Zxx = stft(self.signal, fs=16000, window='hamming', nperseg=1024, padded=False,
                         boundary=None, noverlap=768)

    def update_event(self, inp=-1):
        if inp == 0:
            new_samples = self.input(0)[:-1]
            if new_samples is not None:
                self.signal = np.roll(self.signal, -len(new_samples))
                self.signal[-len(new_samples):] = new_samples
                f, t, Zxx = stft(self.signal[-1792:], fs=16000, window='hamming', nperseg=1024, padded=False,
                                      boundary=None, noverlap=768)
                self.Zxx = np.concatenate((self.Zxx[:, :], Zxx), axis=1)
                self.Zxx = self.Zxx[:, -245:]
                self.main_widget().add_frame(self.Zxx, self.f, self.t)


nodes = [
    SpectrogramNode1,
]