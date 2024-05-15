import tempfile
from matplotlib.patches import Circle
import numpy as np
from PySide2.QtWidgets import QDoubleSpinBox, QSplitter, QMainWindow, QGroupBox, QRadioButton, QDialog, QLineEdit, \
    QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ryven.NWENV import *
from ryven.NENV import *
from qtpy.QtWidgets import QHBoxLayout, QWidget, QPushButton, QComboBox, QSpinBox,  \
    QLabel, QVBoxLayout, QGridLayout, QCheckBox
from qtpy.QtGui import QPixmap
from PySide2.QtCore import Qt, QTimer
from scipy import signal
from scipy.signal import remez, freqz, tf2zpk, zpk2tf, lfilter, butter, firwin, group_delay
import mplcursors
import globals
import matplotlib as plt
import sk_dsp_comm.fir_design_helper as fdh


class FilterDesigner(QMainWindow):
    def __init__(self, response_type, filter_order, design_method, iir_design, fir_design, window_options, fs, fc,
                 fpass_lpf, fstop_lpf, wpass_lpf, wstop_lpf, fpass_hpf, fstop_hpf, wpass_hpf, wstop_hpf,
                 fstop1_bpf, fpass1_bpf, fpass2_bpf, fstop2_bpf, wstop1_bpf, wpass_bpf, wstop2_bpf,
                 fpass1_bsf, fstop1_bsf, fstop2_bsf, fpass2_bsf, wpass1_bsf, wstop_bsf, wpass2_bsf):
        super(FilterDesigner, self).__init__()

        # Store the parameters
        self.coeffs = None
        self.response_type = response_type
        self.filter_order = filter_order
        self.design_method = design_method
        self.iir_design = iir_design
        self.fir_design = fir_design
        self.window_options = window_options
        self.fs = fs
        self.fc = fc
        self.fpass_lpf = fpass_lpf
        self.fstop_lpf = fstop_lpf
        self.wpass_lpf = wpass_lpf
        self.wstop_lpf = wstop_lpf
        self.fpass_hpf = fpass_hpf
        self.fstop_hpf = fstop_hpf
        self.wpass_hpf = wpass_hpf
        self.wstop_hpf = wstop_hpf
        self.fstop1_bpf = fstop1_bpf
        self.fpass1_bpf = fpass1_bpf
        self.fpass2_bpf = fpass2_bpf
        self.fstop2_bpf = fstop2_bpf
        self.wstop1_bpf = wstop1_bpf
        self.wpass_bpf = wpass_bpf
        self.wstop2_bpf = wstop2_bpf
        self.fpass1_bsf = fpass1_bsf
        self.fstop1_bsf = fstop1_bsf
        self.fstop2_bsf = fstop2_bsf
        self.fpass2_bsf = fpass2_bsf
        self.wpass1_bsf = wpass1_bsf
        self.wstop_bsf = wstop_bsf
        self.wpass2_bsf = wpass2_bsf
        self.apass_lpf = 1
        self.astop_lpf = 80

        self.fc_lpf_butterworth = 6000
        self.fc_lpf_window = 6000

        self.current_filter_params = {}

        self.a = None
        self.b = None
        self.z = False

        self.setWindowTitle("Filter Designer")
        # self.setGeometry(100, 100, int(1024*1.5), int(768))
        # self.setGeometry(100, 100, 1500, 1200)
        # self.setGeometry(100, 100, 500, 500)
        self.initUI()
        self.set_font_size(10)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QGridLayout(central_widget)

        # Create a Matplotlib figure and add it to a FigureCanvas
        self.figure = Figure(facecolor='#D3D3D3')  # Set the background color here
        self.canvas = FigureCanvas(self.figure)

        # Create a QGroupBox for the magnitude response plot
        magnitude_group_box = QGroupBox("Magnitude Response (dB)")
        # Create a layout for the QGroupBox
        magnitude_layout = QVBoxLayout()

        # Add the canvas to the QGroupBox's layout
        magnitude_layout.addWidget(self.canvas)

        # Set the layout for the QGroupBox
        magnitude_group_box.setLayout(magnitude_layout)

        magnitude_group_box.setStyleSheet("""
            QGroupBox {
                background-color: #D3D3D3; /* Light grey background */
                color: black; /* Text color */
                border: none; /* No border around the QGroupBox */
                margin-top: 20px; /* Space for the title */
            }
            QGroupBox::title {
                subcontrol-origin: margin; /* Position the title within the margin area */
                subcontrol-position: top center; /* Center the title at the top */
                padding: 0 15px; /* Padding on the left and right */
                background-color: #D3D3D3; /* Same background color as QGroupBox */
                color: black; /* Text color for the title */
                border: 1px solid black; /* Red border around the title */
            }
        """)

        # Add the QGroupBox to the main layout
        # Adjust the row, column, rowspan, and colspan as needed
        self.main_layout.addWidget(magnitude_group_box, 3, 0, 1, 4)

        # Optionally, you can set a minimum size for the group box if needed
        # magnitude_group_box.setMinimumSize(600, 500)

        # For Phase Response Plot
        self.phase_figure = Figure(facecolor='#D3D3D3')  # You can customize the background color
        self.phase_canvas = FigureCanvas(self.phase_figure)

        phase_group_box = QGroupBox("Phase Response (radians)")
        phase_layout = QVBoxLayout()
        phase_layout.addWidget(self.phase_canvas)
        phase_group_box.setLayout(phase_layout)

        # Add style if needed
        phase_group_box.setStyleSheet("""
            QGroupBox {
                background-color: #D3D3D3; /* Light grey background */
                color: black; /* Text color */
                border: none; /* No border around the QGroupBox */
                margin-top: 20px; /* Space for the title */
            }
            QGroupBox::title {
                subcontrol-origin: margin; /* Position the title within the margin area */
                subcontrol-position: top center; /* Center the title at the top */
                padding: 0 15px; /* Padding on the left and right */
                background-color: #D3D3D3; /* Same background color as QGroupBox */
                color: black; /* Text color for the title */
                border: 1px solid black; /* Red border around the title */
            }
        """)

        # Add the new group box to the layout
        self.main_layout.addWidget(phase_group_box, 4, 0, 1, 4)  # Adjust grid position as needed
        # phase_group_box.setMinimumSize(600, 500)

        self.createOptionsGroup()
        self.createResponseTypeGroup()
        self.createFilterOrderGroup()
        self.createDesignMethodGroup()
        # self.createWindowOptionsGroup()
        self.frequency_specs_group = QGroupBox("Frequency Specifications")
        self.createFrequencySpecsGroup()
        self.magnitude_specs_group = QGroupBox("Magnitude Specifications")
        self.createMagnitudeSpecsGroup()
        # self.createOptionsGroup()
        self.plotFilterResponse()
        #
        # self.updateUI()  # Set the initial state of the UI

        # Connect all QDoubleSpinBox valueChanged signals to a single function
        self.connect_all_spinboxes_to(self.update_design_button_style)

    def connect_all_spinboxes_to(self, function):
        for spinbox in self.findChildren(QDoubleSpinBox):
            spinbox.valueChanged.connect(function)
        for spinbox in self.findChildren(QSpinBox):
            spinbox.valueChanged.connect(function)

    def update_design_button_style(self):
        self.design_button.setStyleSheet("color: black; background-color:grey;")

    def createResponseTypeGroup(self):
        self.response_group = QGroupBox("Response Type")
        response_layout = QVBoxLayout()

        self.lowpass = QRadioButton("Lowpass")
        self.highpass = QRadioButton("Highpass")
        self.bandpass = QRadioButton("Bandpass")
        self.bandstop = QRadioButton("Bandstop")
        self.differentiator = QRadioButton("Differentiator")

        if self.response_type == "Lowpass":
            self.lowpass.setChecked(True)
        elif self.response_type == "Highpass":
            self.highpass.setChecked(True)
        elif self.response_type == "Bandpass":
            self.bandpass.setChecked(True)
        elif self.response_type == "Bandstop":
            self.bandstop.setChecked(True)
        elif self.response_type == "Differentiator":
            self.Differentiator.setChecked(True)

        response_layout.addWidget(self.lowpass)
        response_layout.addWidget(self.highpass)
        response_layout.addWidget(self.bandpass)
        response_layout.addWidget(self.bandstop)
        response_layout.addWidget(self.differentiator)
        self.response_group.setLayout(response_layout)

        # Set background color to white and text color to black for the group box and all child widgets
        self.response_group.setStyleSheet("""
            QGroupBox {
                background-color: #D3D3D3; /* Light grey background */
                color: black; /* Text color */
                border: none; /* No border around the QGroupBox */
                margin-top: 20px; /* Space for the title */
            }
            QGroupBox::title {
                subcontrol-origin: margin; /* Position the title within the margin area */
                subcontrol-position: top center; /* Center the title at the top */
                padding: 0 15px; /* Padding on the left and right */
                background-color: #D3D3D3; /* Same background color as QGroupBox */
                color: black; /* Text color for the title */
                border: 1px solid black; /* Red border around the title */
            }
            QGroupBox * {
                background-color: #D3D3D3;
                color: black;
            }
            """)

        # In createResponseTypeGroup
        self.lowpass.toggled.connect(self.updateFrequencySpecs)
        self.highpass.toggled.connect(self.updateFrequencySpecs)
        self.bandpass.toggled.connect(self.updateFrequencySpecs)
        self.bandstop.toggled.connect(self.updateFrequencySpecs)
        self.differentiator.toggled.connect(self.updateFrequencySpecs)

        self.main_layout.addWidget(self.response_group, 0, 0, 2, 1)

    def createFilterOrderGroup(self):
        self.filter_order_group = QGroupBox("Filter Order")
        order_layout = QVBoxLayout()

        self.specify_order_radio = QRadioButton("Specify order:")
        self.specify_order_radio.setChecked(True)
        self.specify_order_spinbox = QSpinBox()
        self.specify_order_spinbox.setMaximum(999)
        self.specify_order_spinbox.setValue(self.filter_order)
        # self.min_order_radio = QRadioButton("Minimum order")

        order_layout.addWidget(self.specify_order_radio)
        order_layout.addWidget(self.specify_order_spinbox)
        # order_layout.addWidget(self.min_order_radio)
        self.filter_order_group.setLayout(order_layout)

        self.filter_order_group.setStyleSheet("""
                    QGroupBox {
                background-color: #D3D3D3; /* Light grey background */
                color: black; /* Text color */
                border: none; /* No border around the QGroupBox */
                margin-top: 20px; /* Space for the title */
            }
            
            QGroupBox::title {
                subcontrol-origin: margin; /* Position the title within the margin area */
                subcontrol-position: top center; /* Center the title at the top */
                padding: 0 15px; /* Padding on the left and right */
                background-color: #D3D3D3; /* Same background color as QGroupBox */
                color: black; /* Text color for the title */
                border: 1px solid black; /* Red border around the title */
            }
                    QGroupBox * {
                        background-color: #D3D3D3;
                        color: black;
                    }
                    """)

        self.main_layout.addWidget(self.filter_order_group, 0, 1)

    def createDesignMethodGroup(self):
        self.design_method_group = QGroupBox("Design Method")
        design_method_layout = QHBoxLayout()

        self.filter_type_combobox = QComboBox()
        self.filter_type_combobox.addItems(["FIR", "IIR"])
        self.filter_type_combobox.setCurrentText(self.design_method)
        self.filter_type_combobox.currentTextChanged.connect(self.onFilterTypeChanged)

        self.iir_design_combobox = QComboBox()
        self.iir_design_combobox.addItems(["Butterworth", "Chebyshev Type I", "Chebyshev Type II", "Elliptic"])
        self.iir_design_combobox.setCurrentText(self.iir_design)
        self.iir_design_combobox.currentTextChanged.connect(self.onDesignMethodChanged)

        self.fir_design_combobox = QComboBox()
        self.fir_design_combobox.addItems(["Equiripple", "Least-squares", "Window", "Constrained Least-squares"])
        self.fir_design_combobox.setCurrentText(self.fir_design)
        self.fir_design_combobox.currentTextChanged.connect(self.onDesignMethodChanged)

        self.window_options_combobox = QComboBox()
        self.window_options_combobox.addItems(["Bartlett", "Blackman", "Hamming", "Hann", "Rectangular"])
        self.window_options_combobox.setCurrentText(self.window_options)

        if self.filter_type_combobox.currentText() == "FIR":
            self.iir_design_combobox.setEnabled(False)
            self.fir_design_combobox.setEnabled(True)
            if self.fir_design_combobox.currentText() == "Window":
                self.window_options_combobox.setEnabled(True)
            else:
                self.window_options_combobox.setEnabled(False)
        else:
            self.fir_design_combobox.setEnabled(False)
            self.window_options_combobox.setEnabled(False)
            self.iir_design_combobox.setEnabled(True)

        design_method_layout.addWidget(self.filter_type_combobox)
        design_method_layout.addWidget(self.iir_design_combobox)
        design_method_layout.addWidget(self.fir_design_combobox)
        design_method_layout.addWidget(self.window_options_combobox)
        self.design_method_group.setLayout(design_method_layout)

        self.design_method_group.setStyleSheet("""
                QGroupBox {
                background-color: #D3D3D3; /* Light grey background */
                color: black; /* Text color */
                border: none; /* No border around the QGroupBox */
                margin-top: 20px; /* Space for the title */
            }
            QGroupBox::title {
                subcontrol-origin: margin; /* Position the title within the margin area */
                subcontrol-position: top center; /* Center the title at the top */
                padding: 0 15px; /* Padding on the left and right */
                background-color: #D3D3D3; /* Same background color as QGroupBox */
                color: black; /* Text color for the title */
                border: 1px solid black; /* Red border around the title */
            }
                QGroupBox * {
                    background-color: #D3D3D3;
                    color: black;
                }
                QComboBox:disabled {
                    color: grey;  /* Change this color to the lighter one you prefer */
                }
            """)

        self.main_layout.addWidget(self.design_method_group, 1, 1)


    def onFilterTypeChanged(self, text):
        self.design_button.setStyleSheet("color: black")
        if text == "IIR":
            self.iir_design_combobox.setEnabled(True)
            self.fir_design_combobox.setEnabled(False)
            self.window_options_combobox.setEnabled(False)
        elif text == "FIR":
            self.iir_design_combobox.setEnabled(False)
            self.fir_design_combobox.setEnabled(True)
            if self.fir_design_combobox.currentText() == "Window":
                self.window_options_combobox.setEnabled(True)
        self.updateFrequencySpecs()

    def onDesignMethodChanged(self, ):
        self.design_button.setStyleSheet("color: black")
        if self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Window":
            self.window_options_combobox.setEnabled(True)
        else:
            self.window_options_combobox.setEnabled(False)

        self.updateFrequencySpecs()

    def updateFrequencySpecs(self):
        self.design_button.setStyleSheet("color: black")
        self.createFrequencySpecsGroup()
        self.createMagnitudeSpecsGroup()

    # def createWindowOptionsGroup(self):
    #     self.window_options_group = QGroupBox("Window Options")
    #     window_options_layout = QHBoxLayout()
    #
    #     self.main_layout.addWidget(self.design_method_group, 2, 1)




    # In createFrequencySpecsGroup, first clear the existing layout
    def createFrequencySpecsGroup(self):
        self.design_button.setStyleSheet("color: black")
        # Initialize frequency_layout if it does not exist
        if not hasattr(self, 'frequency_layout'):
            self.frequency_layout = QGridLayout()

        # Clear existing widgets from the layout
        for i in reversed(range(self.frequency_layout.count())):
            widget = self.frequency_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        if self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
            fs_label = QLabel("Fs:")
            self.fs_spinbox = QDoubleSpinBox()
            self.fs_spinbox.setMaximum(1000000)
            self.fs_spinbox.setValue(self.fs)


            # Lowpass/Highpass labels and spinboxes
            self.fpass_lpf_label = QLabel("Fpass:")
            self.fpass_lpf_spinbox = QDoubleSpinBox()
            self.fpass_lpf_spinbox.setMaximum(1000000)
            self.fpass_lpf_spinbox.setValue(self.fpass_lpf)

            self.fstop_lpf_label = QLabel("Fstop:")
            self.fstop_lpf_spinbox = QDoubleSpinBox()
            self.fstop_lpf_spinbox.setMaximum(1000000)
            self.fstop_lpf_spinbox.setValue(self.fstop_lpf)

            self.frequency_layout.addWidget(fs_label, 0, 0)
            self.frequency_layout.addWidget(self.fs_spinbox, 0, 1)

            self.frequency_layout.addWidget(self.fpass_lpf_label, 1, 0)
            self.frequency_layout.addWidget(self.fpass_lpf_spinbox, 1, 1)

            self.frequency_layout.addWidget(self.fstop_lpf_label, 2, 0)
            self.frequency_layout.addWidget(self.fstop_lpf_spinbox, 2, 1)

        elif self.highpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
            fs_label = QLabel("Fs:")
            self.fs_spinbox = QDoubleSpinBox()
            self.fs_spinbox.setMaximum(1000000)
            self.fs_spinbox.setValue(self.fs)

            self.fstop_hpf_label = QLabel("Fstop:")
            self.fstop_hpf_spinbox = QDoubleSpinBox()
            self.fstop_hpf_spinbox.setMaximum(1000000)
            self.fstop_hpf_spinbox.setValue(self.fstop_hpf)

            # Lowpass/Highpass labels and spinboxes
            self.fpass_hpf_label = QLabel("Fpass:")
            self.fpass_hpf_spinbox = QDoubleSpinBox()
            self.fpass_hpf_spinbox.setMaximum(1000000)
            self.fpass_hpf_spinbox.setValue(self.fpass_hpf)


            self.frequency_layout.addWidget(fs_label, 0, 0)
            self.frequency_layout.addWidget(self.fs_spinbox, 0, 1)

            self.frequency_layout.addWidget(self.fstop_hpf_label, 1, 0)
            self.frequency_layout.addWidget(self.fstop_hpf_spinbox, 1, 1)

            self.frequency_layout.addWidget(self.fpass_hpf_label, 2, 0)
            self.frequency_layout.addWidget(self.fpass_hpf_spinbox, 2, 1)

        elif self.bandpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
            fs_label = QLabel("Fs:")
            self.fs_spinbox = QDoubleSpinBox()
            self.fs_spinbox.setMaximum(1000000)
            self.fs_spinbox.setValue(self.fs)

            self.fstop1_bpf_label = QLabel("Fstop1:")
            self.fstop1_bpf_spinbox = QDoubleSpinBox()
            self.fstop1_bpf_spinbox.setMaximum(1000000)
            self.fstop1_bpf_spinbox.setValue(self.fstop1_bpf)

            self.fpass1_bpf_label = QLabel("Fpass1:")
            self.fpass1_bpf_spinbox = QDoubleSpinBox()
            self.fpass1_bpf_spinbox.setMaximum(1000000)
            self.fpass1_bpf_spinbox.setValue(self.fpass1_bpf)

            self.fpass2_bpf_label = QLabel("Fpass2:")
            self.fpass2_bpf_spinbox = QDoubleSpinBox()
            self.fpass2_bpf_spinbox.setMaximum(1000000)
            self.fpass2_bpf_spinbox.setValue(self.fpass2_bpf)

            self.fstop2_bpf_label = QLabel("Fstop2:")
            self.fstop2_bpf_spinbox = QDoubleSpinBox()
            self.fstop2_bpf_spinbox.setMaximum(1000000)
            self.fstop2_bpf_spinbox.setValue(self.fstop2_bpf)

            self.frequency_layout.addWidget(fs_label, 0, 0)
            self.frequency_layout.addWidget(self.fs_spinbox, 0, 1)

            self.frequency_layout.addWidget(self.fstop1_bpf_label, 1, 0)
            self.frequency_layout.addWidget(self.fstop1_bpf_spinbox, 1, 1)

            self.frequency_layout.addWidget(self.fpass1_bpf_label, 2, 0)
            self.frequency_layout.addWidget(self.fpass1_bpf_spinbox, 2, 1)

            self.frequency_layout.addWidget(self.fpass2_bpf_label, 3, 0)
            self.frequency_layout.addWidget(self.fpass2_bpf_spinbox, 3, 1)

            self.frequency_layout.addWidget(self.fstop2_bpf_label, 4, 0)
            self.frequency_layout.addWidget(self.fstop2_bpf_spinbox, 4, 1)

        elif self.bandstop.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
            fs_label = QLabel("Fs:")
            self.fs_spinbox = QDoubleSpinBox()
            self.fs_spinbox.setMaximum(1000000)
            self.fs_spinbox.setValue(self.fs)

            self.fpass1_bsf_label = QLabel("Fpass1:")
            self.fpass1_bsf_spinbox = QDoubleSpinBox()
            self.fpass1_bsf_spinbox.setMaximum(1000000)
            self.fpass1_bsf_spinbox.setValue(self.fpass1_bsf)

            self.fstop1_bsf_label = QLabel("Fstop1:")
            self.fstop1_bsf_spinbox = QDoubleSpinBox()
            self.fstop1_bsf_spinbox.setMaximum(1000000)
            self.fstop1_bsf_spinbox.setValue(self.fstop1_bsf)

            self.fstop2_bsf_label = QLabel("Fstop2:")
            self.fstop2_bsf_spinbox = QDoubleSpinBox()
            self.fstop2_bsf_spinbox.setMaximum(1000000)
            self.fstop2_bsf_spinbox.setValue(self.fstop2_bsf)

            self.fpass2_bsf_label = QLabel("Fpass2:")
            self.fpass2_bsf_spinbox = QDoubleSpinBox()
            self.fpass2_bsf_spinbox.setMaximum(1000000)
            self.fpass2_bsf_spinbox.setValue(self.fpass2_bsf)

            self.frequency_layout.addWidget(fs_label, 0, 0)
            self.frequency_layout.addWidget(self.fs_spinbox, 0, 1)

            self.frequency_layout.addWidget(self.fstop1_bsf_label, 2, 0)
            self.frequency_layout.addWidget(self.fstop1_bsf_spinbox, 2, 1)

            self.frequency_layout.addWidget(self.fpass1_bsf_label, 1, 0)
            self.frequency_layout.addWidget(self.fpass1_bsf_spinbox, 1, 1)

            self.frequency_layout.addWidget(self.fpass2_bsf_label, 4, 0)
            self.frequency_layout.addWidget(self.fpass2_bsf_spinbox, 4, 1)

            self.frequency_layout.addWidget(self.fstop2_bsf_label, 3, 0)
            self.frequency_layout.addWidget(self.fstop2_bsf_spinbox, 3, 1)

        elif self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "IIR" and self.iir_design_combobox.currentText() == "Butterworth":
            fs_label = QLabel("Fs:")
            self.fs_spinbox = QDoubleSpinBox()
            self.fs_spinbox.setMaximum(1000000)
            self.fs_spinbox.setValue(self.fs)

            # Lowpass/Highpass labels and spinboxes
            self.fc_lpf_butterworth_label = QLabel("Fc:")
            self.fc_lpf_butterworth_spinbox = QDoubleSpinBox()
            self.fc_lpf_butterworth_spinbox.setMaximum(1000000)
            self.fc_lpf_butterworth_spinbox.setValue(self.fc_lpf_butterworth)

            self.frequency_layout.addWidget(fs_label, 0, 0)
            self.frequency_layout.addWidget(self.fs_spinbox, 0, 1)

            self.frequency_layout.addWidget(self.fc_lpf_butterworth_label, 1, 0)
            self.frequency_layout.addWidget(self.fc_lpf_butterworth_spinbox, 1, 1)

        elif self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Window":
            fs_label = QLabel("Fs:")
            self.fs_spinbox = QDoubleSpinBox()
            self.fs_spinbox.setMaximum(1000000)
            self.fs_spinbox.setValue(self.fs)

            # Lowpass/Highpass labels and spinboxes
            self.fc_lpf_window_label = QLabel("Fc:")
            self.fc_lpf_window_spinbox = QDoubleSpinBox()
            self.fc_lpf_window_spinbox.setMaximum(1000000)
            self.fc_lpf_window_spinbox.setValue(self.fc_lpf_window)

            self.frequency_layout.addWidget(fs_label, 0, 0)
            self.frequency_layout.addWidget(self.fs_spinbox, 0, 1)

            self.frequency_layout.addWidget(self.fc_lpf_window_label, 1, 0)
            self.frequency_layout.addWidget(self.fc_lpf_window_spinbox, 1, 1)

        elif self.differentiator.isChecked():
            self.filter_type_combobox.setCurrentText("FIR")
            self.fir_design_combobox.setCurrentText("Equiripple")

            # freq_units_label = QLabel("Frequency Units:")
            # self.freq_units_combobox = QComboBox()
            # self.freq_units_combobox.addItems(["Hz", "kHz", "MHz"])  # Add relevant units

            # Fs
            fs_label = QLabel("Fs:")
            self.fs_spinbox = QDoubleSpinBox()
            self.fs_spinbox.setMaximum(1000000)
            self.fs_spinbox.setValue(self.fs)

            # Frequency Vector
            freq_vector_label = QLabel("Freq. vector:")
            self.freq_vector_lineedit = QLineEdit("[0, 16000]")  # Default value as a string

            # Magnitude Vector
            mag_vector_label = QLabel("Mag. vector:")
            self.mag_vector_lineedit = QLineEdit("[0, 1]")  # Default value as a string

            # Weight Vector
            weight_vector_label = QLabel("Weight vector:")
            self.weight_vector_lineedit = QLineEdit("[1]")  # Default value as a string

            # Adding widgets to the layout
            # self.frequency_layout.addWidget(freq_units_label, 0, 0)
            # self.frequency_layout.addWidget(self.freq_units_combobox, 0, 1)
            self.frequency_layout.addWidget(fs_label, 0, 0)
            self.frequency_layout.addWidget(self.fs_spinbox, 0, 1)
            self.frequency_layout.addWidget(freq_vector_label, 1, 0)
            self.frequency_layout.addWidget(self.freq_vector_lineedit, 1, 1)
            self.frequency_layout.addWidget(mag_vector_label, 2, 0)
            self.frequency_layout.addWidget(self.mag_vector_lineedit, 2, 1)
            self.frequency_layout.addWidget(weight_vector_label, 3, 0)
            self.frequency_layout.addWidget(self.weight_vector_lineedit, 3, 1)

        self.frequency_specs_group.setStyleSheet("""
                        QGroupBox {
                background-color: #D3D3D3; /* Light grey background */
                color: black; /* Text color */
                border: none; /* No border around the QGroupBox */
                margin-top: 20px; /* Space for the title */
            }
            QGroupBox::title {
                subcontrol-origin: margin; /* Position the title within the margin area */
                subcontrol-position: top center; /* Center the title at the top */
                padding: 0 15px; /* Padding on the left and right */
                background-color: #D3D3D3; /* Same background color as QGroupBox */
                color: black; /* Text color for the title */
                border: 1px solid black; /* Red border around the title */
            }
                        QGroupBox * {
                            background-color: #D3D3D3;
                            color: black;
                        }
                    """)

        self.frequency_specs_group.setLayout(self.frequency_layout)
        self.main_layout.addWidget(self.frequency_specs_group, 0, 2, 2, 1)

        self.set_font_size(10)

    def createMagnitudeSpecsGroup(self):
        self.design_button.setStyleSheet("color: black")
        # Initialize frequency_layout if it does not exist
        if not hasattr(self, 'magnitude_layout'):
            self.magnitude_layout = QGridLayout()

        # Clear existing widgets from the layout
        for i in reversed(range(self.magnitude_layout.count())):
            widget = self.magnitude_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        if self.specify_order_radio.isChecked():
            if self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                wpass_lpf_label = QLabel("Wpass:")
                self.wpass_lpf_spinbox = QDoubleSpinBox()
                self.wpass_lpf_spinbox.setMaximum(1000000)
                self.wpass_lpf_spinbox.setValue(self.wpass_lpf)

                wstop_lpf_label = QLabel("Wstop:")
                self.wstop_lpf_spinbox = QDoubleSpinBox()
                self.wstop_lpf_spinbox.setMaximum(1000000)
                self.wstop_lpf_spinbox.setValue(self.wstop_lpf)

                self.magnitude_layout.addWidget(wpass_lpf_label, 0, 0)
                self.magnitude_layout.addWidget(self.wpass_lpf_spinbox, 0, 1)

                self.magnitude_layout.addWidget(wstop_lpf_label, 1, 0)
                self.magnitude_layout.addWidget(self.wstop_lpf_spinbox, 1, 1)

            elif self.highpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                wpass_hpf_label = QLabel("Wpass:")
                self.wpass_hpf_spinbox = QDoubleSpinBox()
                self.wpass_hpf_spinbox.setMaximum(1000000)
                self.wpass_hpf_spinbox.setValue(self.wpass_hpf)

                wstop_hpf_label = QLabel("Wstop:")
                self.wstop_hpf_spinbox = QDoubleSpinBox()
                self.wstop_hpf_spinbox.setMaximum(1000000)
                self.wstop_hpf_spinbox.setValue(self.wstop_hpf)

                self.magnitude_layout.addWidget(wpass_hpf_label, 1, 0)
                self.magnitude_layout.addWidget(self.wpass_hpf_spinbox, 1, 1)

                self.magnitude_layout.addWidget(wstop_hpf_label, 0, 0)
                self.magnitude_layout.addWidget(self.wstop_hpf_spinbox, 0, 1)

            elif self.bandpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                wstop1_bpf_label = QLabel("Wstop1:")
                self.wstop1_bpf_spinbox = QDoubleSpinBox()
                self.wstop1_bpf_spinbox.setMaximum(1000000)
                self.wstop1_bpf_spinbox.setValue(self.wstop1_bpf)

                wpass_bpf_label = QLabel("Wpass:")
                self.wpass_bpf_spinbox = QDoubleSpinBox()
                self.wpass_bpf_spinbox.setMaximum(1000000)
                self.wpass_bpf_spinbox.setValue(self.wpass_bpf)

                wstop2_bpf_label = QLabel("Wstop2:")
                self.wstop2_bpf_spinbox = QDoubleSpinBox()
                self.wstop2_bpf_spinbox.setMaximum(1000000)
                self.wstop2_bpf_spinbox.setValue(self.wstop2_bpf)

                self.magnitude_layout.addWidget(wstop1_bpf_label, 0, 0)
                self.magnitude_layout.addWidget(self.wstop1_bpf_spinbox, 0, 1)

                self.magnitude_layout.addWidget(wpass_bpf_label, 1, 0)
                self.magnitude_layout.addWidget(self.wpass_bpf_spinbox, 1, 1)

                self.magnitude_layout.addWidget(wstop2_bpf_label, 2, 0)
                self.magnitude_layout.addWidget(self.wstop2_bpf_spinbox, 2, 1)

            elif self.bandstop.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                wpass1_bsf_label = QLabel("Wpass1:")
                self.wpass1_bsf_spinbox = QDoubleSpinBox()
                self.wpass1_bsf_spinbox.setMaximum(1000000)
                self.wpass1_bsf_spinbox.setValue(self.wpass1_bsf)

                wstop_bsf_label = QLabel("Wstop:")
                self.wstop_bsf_spinbox = QDoubleSpinBox()
                self.wstop_bsf_spinbox.setMaximum(1000000)
                self.wstop_bsf_spinbox.setValue(self.wstop_bsf)

                wpass2_bsf_label = QLabel("Wpass2:")
                self.wpass2_bsf_spinbox = QDoubleSpinBox()
                self.wpass2_bsf_spinbox.setMaximum(1000000)
                self.wpass2_bsf_spinbox.setValue(self.wpass2_bsf)

                self.magnitude_layout.addWidget(wpass1_bsf_label, 0, 0)
                self.magnitude_layout.addWidget(self.wpass1_bsf_spinbox, 0, 1)

                self.magnitude_layout.addWidget(wstop_bsf_label, 1, 0)
                self.magnitude_layout.addWidget(self.wstop_bsf_spinbox, 1, 1)

                self.magnitude_layout.addWidget(wpass2_bsf_label, 2, 0)
                self.magnitude_layout.addWidget(self.wpass2_bsf_spinbox, 2, 1)

            elif self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "IIR" and self.iir_design_combobox.currentText() == "Butterworth":
                self.magnitude_layout.addWidget(QLabel("The attenuation at cutoff frequencies is fixed at 3 dB (half the passband power)"))

            elif self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Window":
                self.magnitude_layout.addWidget(QLabel(f"The attenuation at cutoff frequencies is\nfixed at 3 dB (half the passband power)"))
        elif self.min_order_radio.isChecked():
            print("shalom")
            if self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                apass_lpf_label = QLabel("Apass:")
                self.apass_lpf_spinbox = QDoubleSpinBox()
                self.apass_lpf_spinbox.setMaximum(1000000)
                self.apass_lpf_spinbox.setValue(self.apass_lpf)

                astop_lpf_label = QLabel("Astop:")
                self.astop_lpf_spinbox = QDoubleSpinBox()
                self.astop_lpf_spinbox.setMaximum(1000000)
                self.astop_lpf_spinbox.setValue(self.astop_lpf)

                self.magnitude_layout.addWidget(apass_lpf_label, 0, 0)
                self.magnitude_layout.addWidget(self.apass_lpf_spinbox, 0, 1)

                self.magnitude_layout.addWidget(astop_lpf_label, 1, 0)
                self.magnitude_layout.addWidget(self.astop_lpf_spinbox, 1, 1)

        self.magnitude_specs_group.setStyleSheet("""
                                QGroupBox {
                background-color: #D3D3D3; /* Light grey background */
                color: black; /* Text color */
                border: none; /* No border around the QGroupBox */
                margin-top: 20px; /* Space for the title */
            }
            QGroupBox::title {
                subcontrol-origin: margin; /* Position the title within the margin area */
                subcontrol-position: top center; /* Center the title at the top */
                padding: 0 15px; /* Padding on the left and right */
                background-color: #D3D3D3; /* Same background color as QGroupBox */
                color: black; /* Text color for the title */
                border: 1px solid black; /* Red border around the title */
            }
                                QGroupBox * {
                                    background-color: #D3D3D3;
                                    color: black;
                                }
                            """)

        self.magnitude_specs_group.setLayout(self.magnitude_layout)
        self.main_layout.addWidget(self.magnitude_specs_group, 0, 3)

        self.set_font_size(10)

    def createOptionsGroup(self):
        self.options_group = QGroupBox()
        options_layout = QVBoxLayout()

        # density_label = QLabel("Density:")
        # self.density_spinbox = QDoubleSpinBox()

        self.design_button = QPushButton("Design Filter")
        self.design_button.clicked.connect(self.plotFilterResponse)

        # options_layout.addWidget(density_label)
        # options_layout.addWidget(self.density_spinbox)
        options_layout.addWidget(self.design_button)

        self.group_deley_button = QPushButton("Group Delay")
        self.group_deley_button.clicked.connect(self.plotGroupDelay)
        options_layout.addWidget(self.group_deley_button)
        #
        self.zero_pole_button = QPushButton("Pole-Zero plot")
        self.zero_pole_button.clicked.connect(self.plotPoleZero)
        options_layout.addWidget(self.zero_pole_button)

        self.coeffs_button = QPushButton("Export coefficients")
        self.coeffs_button.clicked.connect(self.export_coefficients_to_matlab)
        options_layout.addWidget(self.coeffs_button)



        self.options_group.setLayout(options_layout)

        self.options_group.setStyleSheet("""
                                        QGroupBox {
                background-color: #D3D3D3; /* Light grey background */
                color: black; /* Text color */
                border: none; /* No border around the QGroupBox */
                margin-top: 20px; /* Space for the title */
            }
            QGroupBox::title {
                subcontrol-origin: margin; /* Position the title within the margin area */
                subcontrol-position: top center; /* Center the title at the top */
                padding: 0 15px; /* Padding on the left and right */
                background-color: #D3D3D3; /* Same background color as QGroupBox */
                color: black; /* Text color for the title */
                border: 1px solid black; /* Red border around the title */
            }
                                        QGroupBox * {
                                            background-color: #D3D3D3;
                                            color: black;
                                        }
                                    """)

        self.main_layout.addWidget(self.options_group, 1, 3)

    def plotFilterResponse(self):

        self.design_button.setStyleSheet("color: black; background-color: green")
        if self.specify_order_radio.isChecked():
            if self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                # Normalize frequencies to Nyquist Frequency (fs/2)
                self.fs = self.fs_spinbox.value()
                self.filter_order = self.specify_order_spinbox.value()
                self.fpass_lpf = self.fpass_lpf_spinbox.value()
                self.fstop_lpf = self.fstop_lpf_spinbox.value()
                self.wpass_lpf = self.wpass_lpf_spinbox.value()
                self.wstop_lpf = self.wstop_lpf_spinbox.value()

                nyq = 0.5 * self.fs
                bands = [0, self.fpass_lpf, self.fstop_lpf, self.fs/2]
                desired = [1, 0]  # Desired gain in each band
                weights = [self.wpass_lpf, self.wstop_lpf]  # Weights for each band

                # Design the filter
                taps = remez(self.filter_order + 1, bands, desired, weight=weights, Hz=self.fs)
                self.coeffs = taps

            elif self.highpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                # Normalize frequencies to Nyquist Frequency (fs/2)
                self.fs = self.fs_spinbox.value()
                # if self.specify_order_spinbox.value() % 2 == 0:
                #     self.specify_order_spinbox.setValue(self.specify_order_spinbox.value() + 1)
                self.filter_order = self.specify_order_spinbox.value()
                self.fpass_hpf = self.fpass_hpf_spinbox.value()
                self.fstop_hpf = self.fstop_hpf_spinbox.value()
                self.wpass_hpf = self.wpass_hpf_spinbox.value()
                self.wstop_hpf = self.wstop_hpf_spinbox.value()

                nyq = 0.5 * self.fs

                # Design the filter
                # Correct the band edges for highpass filter
                bands = [0, self.fstop_hpf, self.fpass_hpf, nyq]
                desired = [0, 1]  # 0 in stopband, 1 in passband
                # Design the filter
                taps = remez(self.filter_order + 1, bands, desired, weight=[self.wstop_hpf, self.wpass_hpf], Hz=self.fs)
                self.coeffs = taps

            elif self.bandpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                # Normalize frequencies to Nyquist Frequency (fs/2)
                self.fs = self.fs_spinbox.value()
                # if self.specify_order_spinbox.value() % 2 == 1:
                #     self.specify_order_spinbox.setValue(self.specify_order_spinbox.value() + 1)
                self.filter_order = self.specify_order_spinbox.value()
                self.fpass1_bpf = self.fpass1_bpf_spinbox.value()
                self.fpass2_bpf = self.fpass2_bpf_spinbox.value()
                self.fstop1_bpf = self.fstop1_bpf_spinbox.value()
                self.fstop2_bpf = self.fstop2_bpf_spinbox.value()
                self.wpass_bpf = self.wpass_bpf_spinbox.value()
                self.wstop1_bpf = self.wstop1_bpf_spinbox.value()
                self.wstop2_bpf = self.wstop2_bpf_spinbox.value()

                nyq = 0.5 * self.fs

                bands = [0, self.fstop1_bpf, self.fpass1_bpf, self.fpass2_bpf, self.fstop2_bpf, nyq]  # Since Nyquist frequency (Fs/2) is 24000 Hz
                desired = [0, 1, 0]  # Gain of 0 in stopbands, 1 in passband
                weight = [self.wstop1_bpf, self.wpass_bpf, self.wstop2_bpf]  # Equal weight for both stopbands and the passband

                taps = remez(numtaps=self.specify_order_spinbox.value() + 1, bands=bands, desired=desired, weight=weight, Hz=self.fs)
                self.coeffs = taps

            elif self.bandstop.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                # Normalize frequencies to Nyquist Frequency (fs/2)
                self.fs = self.fs_spinbox.value()
                if self.specify_order_spinbox.value() % 2 == 1:
                    self.specify_order_spinbox.setValue(self.specify_order_spinbox.value() + 1)
                self.filter_order = self.specify_order_spinbox.value()
                self.fpass1_bsf = self.fpass1_bsf_spinbox.value()
                self.fpass2_bsf = self.fpass2_bsf_spinbox.value()
                self.fstop1_bsf = self.fstop1_bsf_spinbox.value()
                self.fstop2_bsf = self.fstop2_bsf_spinbox.value()
                self.wpass1_bsf = self.wpass1_bsf_spinbox.value()
                self.wstop_bsf = self.wstop_bsf_spinbox.value()
                self.wpass2_bsf = self.wpass2_bsf_spinbox.value()

                nyq = 0.5 * self.fs

                # Design the filter
                # Define the bands for the bandstop filter
                bands = [0, self.fpass1_bsf, self.fstop1_bsf, self.fstop2_bsf, self.fpass2_bsf, nyq]
                desired = [1, 0, 1]  # Gain of 1 in passbands, 0 in stopband
                weight = [self.wpass1_bsf, self.wstop_bsf, self.wpass2_bsf]

                taps = remez(self.filter_order + 1, bands, desired, weight=weight, Hz=self.fs)
                self.coeffs = taps

            elif self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "IIR" and self.iir_design_combobox.currentText() == "Butterworth":
                self.fs = self.fs_spinbox.value()
                nyq = 0.5 * self.fs  # Define nyq here for Butterworth filter
                self.fc_lpf_butterworth = self.fc_lpf_butterworth_spinbox.value()
                self.filter_order = self.specify_order_spinbox.value()

                # Normalize the cutoff frequency with respect to Nyquist frequency
                Wn = self.fc_lpf_butterworth / (0.5 * self.fs)

                # Calculate the filter coefficients for a Butterworth filter
                b, a = butter(self.filter_order, Wn, btype='low')

                self.a = a
                self.b = b


            elif self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Window":

                self.fs = self.fs_spinbox.value()
                nyq = 0.5 * self.fs  # Define nyq here for FIR filter
                self.fc_lpf_window = self.fc_lpf_window_spinbox.value()
                self.filter_order = self.specify_order_spinbox.value()
                self.window_options = self.window_options_combobox.currentText()
                # Normalize the cutoff frequency with respect to Nyquist frequency
                cutoff = self.fc_lpf_window / nyq

                # Select the window type and create the filter
                if self.window_options == "Bartlett":
                    window_type = 'bartlett'
                elif self.window_options == "Blackman":
                    window_type = 'blackman'
                elif self.window_options == "Hamming":
                    window_type = 'hamming'
                elif self.window_options == "Hann":
                    window_type = 'hann'
                elif self.window_options == "Rectangular":
                    window_type = 'boxcar'

                # Design the filter using the specified window
                taps = firwin(self.filter_order + 1, cutoff, window=window_type)
                self.coeffs = taps



            elif self.differentiator.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                self.fs = self.fs_spinbox.value()
                self.filter_order = self.specify_order_spinbox.value()
                nyq = 0.5 * self.fs
                bands = self.freq_vector_lineedit.text()
                bands = eval(bands)
                desired = self.mag_vector_lineedit.text()
                desired = eval(desired)
                desired = [desired[-1] * int(self.fs/bands[-1])]
                # Weights for each band - can be equal since remez will automatically weight them according to frequency.
                weight = self.weight_vector_lineedit.text()
                weight = eval(weight)
                print("bands:", bands, "desired:", desired, "weight:", weight)
                # Design the filter using the remez algorithm with 'differentiator' type
                taps = remez(self.filter_order + 1, bands=bands, desired=desired, weight=weight, type='differentiator',
                            fs=self.fs)
                self.coeffs = taps
                print(self.coeffs)
        elif self.min_order_radio.isChecked:
            if self.lowpass.isChecked() and self.filter_type_combobox.currentText() == "FIR" and self.fir_design_combobox.currentText() == "Equiripple":
                # Normalize frequencies to Nyquist Frequency (fs/2)
                self.fs = self.fs_spinbox.value()
                self.fpass_lpf = self.fpass_lpf_spinbox.value()
                self.fstop_lpf = self.fstop_lpf_spinbox.value()
                self.apass_lpf = self.apass_lpf_spinbox.value()
                self.astop_lpf = self.astop_lpf_spinbox.value()

                taps = fdh.fir_remez_lpf(self.fpass_lpf, self.fstop_lpf, self.apass_lpf, self.astop_lpf, self.fs)
                self.coeffs = taps


        # # Calculate ZPK
        # z, p, k = tf2zpk(taps, [1])
        #
        # # Convert ZPK to Polynomial Coefficients
        # b, a = zpk2tf(z, p, k)
        #
        # # self.z = z
        # self.a = a
        # self.b = b
        #
        # self.coeffs = taps

        self.zi = False
        if self.filter_type_combobox.currentText() == "FIR":
        # Calculate frequency response of the filter
            w, h = freqz(taps, worN=8000)
        elif self.filter_type_combobox.currentText() == "IIR":
            w, h = freqz(self.b, self.a, worN=8000)


        # Convert response to decibels
        h_db = 20 * np.log10(np.abs(h))

        # Create a frequency array for plotting
        freq = w * self.fs / (2 * np.pi)

        # Use the existing figure and clear it
        self.figure.clear()

        # Calculate phase response
        angles = np.unwrap(np.angle(h))  # Unwrap phase angles

        # Add a subplot to the figure
        ax = self.figure.add_subplot(111)

        # Plot the frequency response
        ax.plot(freq / 1000, h_db)  # Convert frequency to kHz for plotting
        ax.set_title("Filter Frequency Response")
        ax.set_xlabel("Frequency (kHz)")
        ax.set_ylabel("Gain (dB)")
        ax.set_xlim(0,int(self.fs/2))
        ax.grid(True)

        # Optionally set the axes limits if needed
        ax.set_xlim([0, self.fs_spinbox.value() / 2000])  # Set x-axis limit to half the sampling rate
        # print(min(h_db))
        # print(max(h_db))
        # ax.set_ylim([min(h_db) - 10, max(h_db) + 10])  # Give some padding to y-axis limits
        mplcursors.cursor(ax, hover=True)

        # Refresh the canvas
        self.canvas.draw()

        # Plotting Phase Response on new phase_canvas
        self.phase_figure.clear()
        phase_ax = self.phase_figure.add_subplot(111)

        # Plot the phase response
        phase_ax.plot(freq / 1000, angles)  # Convert frequency to kHz for plotting
        phase_ax.set_title("Filter Phase Response")
        phase_ax.set_xlabel("Frequency (kHz)")
        phase_ax.set_ylabel("Phase (radians)")
        phase_ax.grid(True)
        phase_ax.set_xlim(([0, self.fs_spinbox.value() / 2000]))

        mplcursors.cursor(phase_ax, hover=True)
        # Refresh the phase canvas
        self.phase_canvas.draw()
        # self.plotGroupDelay()
        # self.plotPoleZero()

    def plotGroupDelay(self):
        # Verify the filter type and compute the group delay
        if self.filter_type_combobox.currentText() == "FIR":
            w, gd = group_delay((self.coeffs, 1), fs=self.fs)
        elif self.filter_type_combobox.currentText() == "IIR":
            w, gd = group_delay((self.b, self.a), fs=self.fs)

        # Consider unwrapping the phase before calculating the group delay for IIR filters
        # This is just a placeholder and might not be directly applicable
        # phase = np.angle(h)
        # unwrapped_phase = unwrap(phase)
        # gd = np.diff(unwrapped_phase) / np.diff(w)

        gd = [round(float(value), 2) for value in gd]

        # Create a dialog window
        gd_dialog = QDialog(self)
        gd_dialog.setWindowTitle("Group Delay Response")
        gd_layout = QVBoxLayout()
        gd_dialog.setLayout(gd_layout)

        # Create a figure and canvas for the plot
        gd_figure = Figure()
        gd_canvas = FigureCanvas(gd_figure)
        gd_layout.addWidget(gd_canvas)

        # Plot the group delay on the canvas
        gd_ax = gd_figure.add_subplot(111)
        gd_ax.plot(w[:-20], gd[:-20])
        # gd_ax.set_xlim(0, 0.9*self.fs/2)
        gd_ax.set_title("Group Delay Response")
        gd_ax.set_xlabel("Frequency (Hz)")
        gd_ax.set_ylabel("Group delay (samples)")
        gd_ax.grid(True)

        # Refresh the canvas and show the dialog
        mplcursors.cursor(gd_ax, hover=True)
        gd_canvas.draw()
        gd_dialog.exec_()



    def plotPoleZero(self):
        # Get the poles and zeros
        if self.filter_type_combobox.currentText() == "FIR":
            z, p, k = tf2zpk(self.coeffs, [1])
            # print("Poles:", p)
            # print("Zeros:", z)
        elif self.filter_type_combobox.currentText() == "IIR":
            z, p, k = tf2zpk(self.b, self.a)

        # Create a dialog window
        pz_dialog = QDialog(self)
        pz_dialog.setWindowTitle("Pole-Zero Plot")
        pz_layout = QVBoxLayout()
        pz_dialog.setLayout(pz_layout)

        # Create a figure and canvas for the plot
        pz_figure = Figure()
        pz_canvas = FigureCanvas(pz_figure)
        pz_layout.addWidget(pz_canvas)

        # Plot the zeros and poles on the canvas
        pz_ax = pz_figure.add_subplot(111)


        # Plot zeros and poles
        pz_ax.scatter(np.real(z), np.imag(z), marker='o', color='blue', label='Zeros')
        pz_ax.scatter(np.real(p), np.imag(p), marker='x', color='red', label='Poles')

        # Add unit circle for reference
        unit_circle = Circle((0, 0), radius=1, color='green', fill=False, linestyle='dotted', linewidth=1.5)
        pz_ax.add_artist(unit_circle)

        pz_ax.set_title("Pole-Zero Plot")
        pz_ax.set_xlabel("Real")
        pz_ax.set_ylabel("Imaginary")
        pz_ax.grid(True)
        pz_ax.axhline(y=0, color='k')
        pz_ax.axvline(x=0, color='k')
        pz_ax.legend()

        # Set the aspect ratio to be equal so that the circle is shown correctly
        pz_ax.set_aspect('equal')

        # Set the limits of the plot to slightly larger than the unit circle for visibility
        pz_ax.set_xlim([-1.5, 1.5])
        pz_ax.set_ylim([-1.5, 1.5])
        # max_x = np.max(abs(np.imag(z)))
        # max_y = np.max(abs(np.real(z)))
        # pz_ax.set_xlim([-(max_x+1), max_x+1])
        # pz_ax.set_ylim([-(max_y+1), max_y+1])

        # Refresh the canvas and show the dialog
        mplcursors.cursor(pz_ax, hover=True)
        pz_canvas.draw()
        pz_dialog.exec_()

    def export_coefficients_to_matlab(self):
        # Get the coefficients
        if self.filter_type_combobox.currentText() == "FIR":
            coefficients = self.coeffs
        elif self.filter_type_combobox.currentText() == "IIR":
            # In case of an IIR filter, you might want to export both 'b' (numerator) and 'a' (denominator) coefficients
            coefficients = {'b': self.b, 'a': self.a}
        else:
            raise ValueError("Unknown filter type.")

        # Choose a filename
        filename = QFileDialog.getSaveFileName(self, 'Save File', '', "MATLAB Files (*.m)")[0]
        if not filename:
            return  # The user cancelled the file saving

        # Write the coefficients to a MATLAB script file
        with open(filename, 'w') as file:
            if isinstance(coefficients, dict):
                # IIR filter coefficients
                file.write(f"% IIR filter coefficients\n")
                file.write(f"b = [{', '.join(map(str, coefficients['b']))}];\n")
                file.write(f"a = [{', '.join(map(str, coefficients['a']))}];\n")
            else:
                # FIR filter coefficients
                file.write(f"% FIR filter coefficients\n")
                file.write(f"coeffs = [{', '.join(map(str, coefficients))}];\n")

        print(f"Filter coefficients were successfully exported to {filename}")

    def set_font_size(self, size):
        for widget in self.findChildren(QWidget):
            font = widget.font()
            font.setPointSize(size)
            widget.setFont(font)

    def get_current_params(self):
        self.current_filter_params = {
            'response_type': self.response_type,
            'filter_order': self.specify_order_spinbox.value(),
            'design_method': self.filter_type_combobox.currentText(),
            'iir_design': self.iir_design_combobox.currentText(),
            'fir_design': self.fir_design_combobox.currentText(),
            'window_options': self.window_options,
            'fs': self.fs,
            'fc': self.fc,
            'fpass_lpf': self.fpass_lpf,
            'fstop_lpf': self.fstop_lpf,
            'wpass_lpf': self.wpass_lpf,
            'wstop_lpf': self.wstop_lpf,
            'fpass_hpf': self.fpass_hpf,
            'fstop_hpf': self.fstop_hpf,
            'wpass_hpf': self.wpass_hpf,
            'wstop_hpf': self.wstop_hpf,
            'fstop1_bpf': self.fstop1_bpf,
            'fpass1_bpf': self.fpass1_bpf,
            'fpass2_bpf': self.fpass2_bpf,
            'fstop2_bpf': self.fstop2_bpf,
            'wstop1_bpf': self.wstop1_bpf,
            'wpass_bpf': self.wpass_bpf,
            'wstop2_bpf': self.wstop2_bpf,
            'fpass1_bsf': self.fpass1_bsf,
            'fstop1_bsf': self.fstop1_bsf,
            'fstop2_bsf': self.fstop2_bsf,
            'fpass2_bsf': self.fpass2_bsf,
            'wpass1_bsf': self.wpass1_bsf,
            'wstop_bsf': self.wstop_bsf,
            'wpass2_bsf': self.wpass2_bsf,
        }
        return self.current_filter_params


class DigitalFilterDesignWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.zi = None
        self.coeffs = None
        layout = QVBoxLayout()
        self.imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "LPF.png")
        image = QPixmap(icon_path)
        self.imageLabel.setPixmap(image)
        layout.addWidget(self.imageLabel)
        self.setLayout(layout)

        self.a = None
        self.b = None
        self.z = None

        self.response_type = self.node.response_type
        self.filter_order = self.node.filter_order
        self.design_method = self.node.design_method

        self.iir_design = self.node.iir_design
        self.fir_design = self.node.fir_design
        self.window_options = self.node.window_options
        self.fs = self.node.fs
        self.fc = self.node.fc

        self.fpass_lpf = self.node.fpass_lpf
        self.fstop_lpf = self.node.fstop_lpf
        self.wpass_lpf = self.node.wpass_lpf
        self.wstop_lpf = self.node.wstop_lpf

        self.fpass_hpf = self.node.fpass_hpf
        self.fstop_hpf = self.node.fstop_hpf
        self.wpass_hpf = self.node.wpass_hpf
        self.wstop_hpf = self.node.wstop_hpf

        self.fstop1_bpf = self.node.fstop1_bpf
        self.fpass1_bpf = self.node.fpass1_bpf
        self.fpass2_bpf = self.node.fpass2_bpf
        self.fstop2_bpf = self.node.fstop2_bpf
        self.wstop1_bpf = self.node.wstop1_bpf
        self.wpass_bpf = self.node.wpass_bpf
        self.wstop2_bpf = self.node.wstop2_bpf

        self.fpass1_bsf = self.node.fpass1_bsf
        self.fstop1_bsf = self.node.fstop1_bsf
        self.fstop2_bsf = self.node.fstop2_bsf
        self.fpass2_bsf = self.node.fpass2_bsf
        self.wpass1_bsf = self.node.wpass1_bsf
        self.wstop_bsf = self.node.wstop_bsf
        self.wpass2_bsf = self.node.wpass2_bsf

        try:
            self.window = FilterDesigner(
                response_type=self.response_type,
                filter_order=self.filter_order,
                design_method=self.design_method,
                iir_design=self.iir_design,
                fir_design=self.fir_design,
                window_options=self.window_options,
                fs=self.fs,
                fc=self.fc,
                fpass_lpf=self.fpass_lpf,
                fstop_lpf=self.fstop_lpf,
                wpass_lpf=self.wpass_lpf,
                wstop_lpf=self.wstop_lpf,
                fpass_hpf=self.fpass_hpf,
                fstop_hpf=self.fstop_hpf,
                wpass_hpf=self.wpass_hpf,
                wstop_hpf=self.wstop_hpf,
                fstop1_bpf=self.fstop1_bpf,
                fpass1_bpf=self.fpass1_bpf,
                fpass2_bpf=self.fpass2_bpf,
                fstop2_bpf=self.fstop2_bpf,
                wstop1_bpf=self.wstop1_bpf,
                wpass_bpf=self.wpass_bpf,
                wstop2_bpf=self.wstop2_bpf,
                fpass1_bsf=self.fpass1_bsf,
                fstop1_bsf=self.fstop1_bsf,
                fstop2_bsf=self.fstop2_bsf,
                fpass2_bsf=self.fpass2_bsf,
                wpass1_bsf=self.wpass1_bsf,
                wstop_bsf=self.wstop_bsf,
                wpass2_bsf=self.wpass2_bsf
            )
            # self.window.plot()
        except Exception as e:
            print(e)

        # if self.coeffs is not None:
        #     self.update_magnitude_response_label()

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
    #
    #
    #
    # def mousePressEvent(self, event):
    #     pass
    #
    # def mouseDoubleClickEvent(self, event):
    #     self.window.show()

    def filter_frame(self, frame):
        self.a = self.window.a
        self.b = self.window.b
        self.zi = self.window.zi
        self.coeffs = self.window.coeffs

        # Initialize self.z with zeros if not already set
        if self.zi is False:
            if self.window.filter_type_combobox.currentText() == "FIR":
                self.z = np.zeros(len(self.coeffs) - 1)  # Initialize self.z for FIR filter
            elif self.window.filter_type_combobox.currentText() == "IIR":
                self.z = np.zeros(max(len(self.a), len(self.b)) - 1)  # Initialize self.z for IIR filter
            self.window.zi = True

        # Apply the filter based on the filter type
        if self.window.filter_type_combobox.currentText() == "FIR":
            # For FIR filters, the 'a' coefficient is always 1
            frame_filtered, self.z = signal.lfilter(self.coeffs, 1, frame, zi=self.z)
        elif self.window.filter_type_combobox.currentText() == "IIR":
            # For IIR filters, use both 'b' and 'a' coefficients
            frame_filtered, self.z = signal.lfilter(self.b, self.a, frame, zi=self.z)
        else:
            # Default case: return the frame as is
            frame_filtered = frame

        return frame_filtered

    def gets_parameters(self):
        return self.window.get_current_params()

    # def generate_magnitude_response_image(self):
    #     # Assume self.coeffs holds the filter coefficients
    #     w, h = signal.freqz(self.coeffs, worN=8000, fs=self.fs)
    #
    #     # Generate magnitude in decibels
    #     h_db = 20 * np.log10(np.abs(h))
    #
    #     # Create a figure and plot the magnitude response
    #     fig, ax = plt.subplots()
    #     ax.plot(w, h_db)
    #     ax.set_title('Magnitude Response')
    #     ax.set_xlabel('Frequency [Hz]')
    #     ax.set_ylabel('Magnitude [dB]')
    #     ax.grid()
    #
    #     # Save the figure to a temporary file
    #     temp_image_path = os.path.join(tempfile.gettempdir(), 'temp_magnitude_response.png')
    #     fig.savefig(temp_image_path)
    #     plt.close(fig)  # Close the figure to free up memory
    #
    #     return temp_image_path
    #
    # def update_magnitude_response_label(self):
    #     temp_image_path = self.generate_magnitude_response_image()
    #     image = QPixmap(temp_image_path).scaled(240, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #     self.imageLabel.setPixmap(image)


class DigitalFilterDesign(Node):
    title = 'Digital Filter Design'
    style = 'large'
    main_widget_class = DigitalFilterDesignWidget
    main_widget_pos = 'between ports'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "LPF.png")
    icon = icon_path
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
        self.filter_order = 100
        self.design_method = "FIR"
        self.iir_design = "Butterworth"
        self.fir_design = "Equiripple"
        self.window_options = "Bartlett"

        self.fs = self.get_var_val("fs")
        if self.fs is None:
            print("fs from globals")
            self.fs = globals.fs
        # self.fs = globals.fs
        self.fc = 1

        self.fpass_lpf = 4000
        self.fstop_lpf = 5000
        self.wpass_lpf = 1
        self.wstop_lpf = 1

        self.fpass_hpf = 12000
        self.fstop_hpf = 9600
        self.wpass_hpf = 1
        self.wstop_hpf = 1

        self.fstop1_bpf = 7200
        self.fpass1_bpf = 9600
        self.fpass2_bpf = 12000
        self.fstop2_bpf = 14400
        self.wstop1_bpf = 1
        self.wpass_bpf = 1
        self.wstop2_bpf = 1

        self.fpass1_bsf = 7200
        self.fstop1_bsf = 9600
        self.fstop2_bsf = 12000
        self.fpass2_bsf = 14400
        self.wpass1_bsf = 1
        self.wstop_bsf = 1
        self.wpass2_bsf = 1



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
            'filter_order': data_parameters['filter_order'],
            'design_method': data_parameters['design_method'],
            'iir_design': data_parameters['iir_design'],
            'fir_design': data_parameters['fir_design'],
            'window_options': data_parameters['window_options'],
            'fs': data_parameters['fs'],
            'fc': data_parameters['fc'],
            'fpass_lpf': data_parameters['fpass_lpf'],
            'fstop_lpf': data_parameters['fstop_lpf'],
            'wpass_lpf': data_parameters['wpass_lpf'],
            'wstop_lpf': data_parameters['wstop_lpf'],
            'fpass_hpf': data_parameters['fpass_hpf'],
            'fstop_hpf': data_parameters['fstop_hpf'],
            'wpass_hpf': data_parameters['wpass_hpf'],
            'wstop_hpf': data_parameters['wstop_hpf'],
            'fstop1_bpf': data_parameters['fstop1_bpf'],
            'fpass1_bpf': data_parameters['fpass1_bpf'],
            'fpass2_bpf': data_parameters['fpass2_bpf'],
            'fstop2_bpf': data_parameters['fstop2_bpf'],
            'wstop1_bpf': data_parameters['wstop1_bpf'],
            'wpass_bpf': data_parameters['wpass_bpf'],
            'wstop2_bpf': data_parameters['wstop2_bpf'],
            'fpass1_bsf': data_parameters['fpass1_bsf'],
            'fstop1_bsf': data_parameters['fstop1_bsf'],
            'fstop2_bsf': data_parameters['fstop2_bsf'],
            'fpass2_bsf': data_parameters['fpass2_bsf'],
            'wpass1_bsf': data_parameters['wpass1_bsf'],
            'wstop_bsf': data_parameters['wstop_bsf'],
            'wpass2_bsf': data_parameters['wpass2_bsf'],
        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.response_type = data['response_type']
        self.filter_order = data['filter_order']
        self.design_method = data['design_method']
        self.iir_design = data['iir_design']
        self.fir_design = data['fir_design']
        self.window_options = data['window_options']
        # self.fs = data['fs']
        self.fc = data['fc']
        self.fpass_lpf = data['fpass_lpf']
        self.fstop_lpf = data['fstop_lpf']
        self.wpass_lpf = data['wpass_lpf']
        self.wstop_lpf = data['wstop_lpf']
        self.fpass_hpf = data['fpass_hpf']
        self.fstop_hpf = data['fstop_hpf']
        self.wpass_hpf = data['wpass_hpf']
        self.wstop_hpf = data['wstop_hpf']
        self.fstop1_bpf = data['fstop1_bpf']
        self.fpass1_bpf = data['fpass1_bpf']
        self.fpass2_bpf = data['fpass2_bpf']
        self.fstop2_bpf = data['fstop2_bpf']
        self.wstop1_bpf = data['wstop1_bpf']
        self.wpass_bpf = data['wpass_bpf']
        self.wstop2_bpf = data['wstop2_bpf']
        self.fpass1_bsf = data['fpass1_bsf']
        self.fstop1_bsf = data['fstop1_bsf']
        self.fstop2_bsf = data['fstop2_bsf']
        self.fpass2_bsf = data['fpass2_bsf']
        self.wpass1_bsf = data['wpass1_bsf']
        self.wstop_bsf = data['wstop_bsf']
        self.wpass2_bsf = data['wpass2_bsf']


nodes = [
    DigitalFilterDesign,
]