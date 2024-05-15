from PySide2.QtWidgets import QLayout, QLineEdit, QComboBox
from ryven.NENV import *
from ryven.NWENV import *
from qtpy.QtWidgets import QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget, QTextEdit, QGroupBox, QHBoxLayout
from qtpy.QtGui import QPixmap, QFont
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal, QSize, QTimer
import os
from scipy.io import wavfile
import numpy as np
import sounddevice as sd
import pyaudio
import wave
import librosa
import globals


class ChooseFileInputWidget(MWB, QWidget):


    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.path_chosen = self.node.audio_filepath
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # Set the layout margins to 0
        # layout.setSizeConstraint(QLayout.SetFixedSize)  # Set the size constraint
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "read from wav.png")
        image = QPixmap(icon_path)
        imageLabel.setPixmap(image)
        imageLabel.setMargin(0)
        imageLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(imageLabel)
        label = self.node.label
        if label != None:
            self.WavDetails = QLabel(label)
            self.WavDetails
        else:
            self.WavDetails = QLabel("Not Selected WAV\n")
        self.WavDetails.setMinimumWidth(150)
        self.WavDetails.setMaximumWidth(150)
        layout.addWidget(self.WavDetails)
        #


        # label = QLineEdit("Read Wav")
        # label.setMaximumWidth(120)
        # label.setMinimumHeight(34)  # You may need to increase this if the text is still cut off
        # label.setAlignment(Qt.AlignCenter)  # Center the text vertically and horizontally
        #
        # layout.addWidget(label)

        self.setLayout(layout)
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.singleClickAction)
        self.click_count = 0

        self.setStyleSheet("""
                    QWidget {
                        background-color: white;
                    }
                    QLabel {
                        background-color: white;
                        color: black;
                        font-size: 8pt;
                    }
                """)
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
        file_path = QFileDialog.getOpenFileName(self, 'Select image')[0]
        print(file_path)
        try:
            file_path = os.path.relpath(file_path)
        except ValueError:
            return

        self.path_chosen = file_path
        self.node.path_chosen(self.path_chosen)

    def updateWavDetail(self, label):
        print(label)
        self.WavDetails.setText(label)


class ReadWavAudio(Node):
    style = "large"
    title = 'Read Wav'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "read from wav.png")
    icon = icon_path
    main_widget_class = ChooseFileInputWidget
    main_widget_pos = 'between ports'

    init_inputs = [
        NodeInputBP(type_='exec'),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]
    color = '#e60026'

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
        self.audio_filepath = "C:\\Users\\shalo\\PycharmProjects\\DSProject\\record1.wav"
        self.data_audio = None
        self.num_of_samples = None
        self.i = 0
        self.label = None

    # def view_place_event(self):
    #     self.data_audio = self.path_chosen(self.audio_filepath)

    def update_event(self, inp=-1):

        if inp > -1:
            if self.i + self.frame_size >= len(self.data_audio):
                remaining = len(self.data_audio) - self.i
                # output_data = self.data[self.i:] + self.data[:256 - remaining]
                output_data = np.concatenate((self.data_audio[self.i:], self.data_audio[:self.frame_size - remaining]))
                self.i = self.frame_size - remaining
            else:
                output_data = self.data_audio[self.i:self.i + self.frame_size]
                self.i += self.frame_size
            flag = 0
            output_data = np.int16(output_data)
            output_data = np.append(output_data, np.int16(flag))
            self.set_output_val(0, output_data)

    def get_state(self) -> dict:
        print("get_state called")
        print(self.audio_filepath)

        return {
            'path': self.audio_filepath
        }

    def set_state(self, data: dict, version):
        print("set_state called with data:", data)
        self.audio_filepath = data['path']
        self.path_chosen(self.audio_filepath)
        print(data['path'])
        # self.self.main_widget().updateWavDetail(self.label)



    # def get_state(self):
    #     data = {'audio file path': self.audio_filepath}
    #     print("baba")
    #     return data
    #
    # def set_state(self, data, version):
    #     self.path_chosen(data['audio file path'])
    #     # self.image_filepath = data['image file path']

    # def path_chosen(self, file_path):
    #     self.audio_filepath = file_path
    #     # self.update()
    #     if self.audio_filepath == '':
    #         return
    #     try:
    #         samplerate, self.data_audio = wavfile.read(self.audio_filepath)
    #         print("Sample rate:", samplerate)
    #
    #         # Determine bit depth from data type
    #         if self.data_audio.dtype == np.int16:
    #             bit_depth = 16
    #         elif self.data_audio.dtype == np.int32:
    #             bit_depth = 32
    #         elif self.data_audio.dtype == np.int8:
    #             bit_depth = 8
    #         elif self.data_audio.dtype == np.float32:  # Sometimes used for normalized WAV files
    #             bit_depth = '32 (float)'
    #         else:
    #             bit_depth = 'Unknown'
    #         print("Bit depth:", bit_depth)
    #
    #         # Determine mono or stereo from data shape
    #         if len(self.data_audio.shape) == 1:
    #             print("Channels: Mono")
    #         elif self.data_audio.shape[1] == 2:
    #             print("Channels: Stereo")
    #         else:
    #             print("Channels:", self.data_audio.shape[1])  # More than stereo, e.g., 5.1 surround sound
    #         # self.set_output_val(0, data)
    #     except Exception as e:
    #         print(e)
    #     self.num_of_samples = len(self.data_audio)

    def path_chosen(self, file_path):
        self.audio_filepath = file_path
        # self.update()
        if self.audio_filepath == '':
            return
        try:
            y, sr = librosa.load(self.audio_filepath, sr=None, mono=False)

            # Convert to mono by averaging channels
            if len(y.shape) > 1 and y.shape[0] == 2:
                y = (y[0, :] + y[1, :]) / 2

            # Resample to 16kHz
            y_resample = librosa.core.resample(y, orig_sr=sr, target_sr=self.fs)
            self.data_audio = np.int16(y_resample * 32767)
            samplerate = self.fs

            # samplerate, self.data_audio = wavfile.read(self.audio_filepath)
            print("Sample rate:", samplerate)

            # Determine bit depth from data type
            if self.data_audio.dtype == np.int16:
                bit_depth = 16
            elif self.data_audio.dtype == np.int32:
                bit_depth = 32
            elif self.data_audio.dtype == np.int8:
                bit_depth = 8
            elif self.data_audio.dtype == np.float32:  # Sometimes used for normalized WAV files
                bit_depth = '32 (float)'
            else:
                bit_depth = 'Unknown'
            print("Bit depth:", bit_depth)

            # Determine mono or stereo from data shape
            if len(self.data_audio.shape) == 1:
                channel = "mono"
                print("Channels: Mono")
            elif self.data_audio.shape[1] == 2:
                channel = "stereo"
                print("Channels: Stereo")
            else:
                print("Channels:", self.data_audio.shape[1])  # More than stereo, e.g., 5.1 surround sound
            # self.set_output_val(0, data)
        except Exception as e:
            print(e)
        self.num_of_samples = len(self.data_audio)
        label = f"{os.path.basename(file_path)}\n{samplerate} Hz, {bit_depth} bit, {channel}"
        self.label = label
        self.main_widget().updateWavDetail(label)


# class ReadWavAudio(Node):
#     style = "large"
#     title = 'Read From Wav'
#     input_widget_classes = {
#         'choose file IW': ChooseFileInputWidget
#     }
#     main_widget_pos = 'between ports'
#     # init_inputs = [
#     #     NodeInputBP('f_path', add_data={'widget name': 'choose file IW', 'widget pos': 'besides'})
#     # ]
#
#     init_inputs = [
#         NodeInputBP('f_path', add_data={'widget name': 'choose file IW', 'widget pos': 'besides'}),
#         NodeInputBP(type_='exec'),
#     ]
#
#     init_outputs = [
#         NodeOutputBP(),
#     ]
#     color = '#e60026'
#
#     def __init__(self, params):
#         super().__init__(params)
#
#         self.audio_filepath = ''
#         self.data = None
#         self.num_of_samples = None
#         self.i = 0
#
#     def view_place_event(self):
#         self.input_widget(0).path_chosen.connect(self.path_chosen)
#         # self.main_widget_message.connect(self.main_widget().show_path)
#
#     def update_event(self, inp=-1):
#
#         if inp > -1:
#             if self.i + 1024 >= len(self.data):
#                 remaining = len(self.data) - self.i
#                 # output_data = self.data[self.i:] + self.data[:256 - remaining]
#                 output_data = np.concatenate((self.data[self.i:], self.data[:1024 - remaining]))
#                 self.i = 1024 - remaining
#             else:
#                 output_data = self.data[self.i:self.i + 1024]
#                 self.i += 1024
#             self.set_output_val(0, output_data)
#
#             # self.set_output_val(0, self.num_of_samples)
#
#     def get_state(self):
#         data = {'audio file path': self.audio_filepath}
#         return data
#
#     def set_state(self, data, version):
#         self.path_chosen(data['audio file path'])
#         # self.image_filepath = data['image file path']
#
#     def path_chosen(self, file_path):
#         self.audio_filepath = file_path
#         # self.update()
#         if self.audio_filepath == '':
#             return
#
#         try:
#             samplerate, self.data = wavfile.read(self.audio_filepath)
#             # self.set_output_val(0, data)
#         except Exception as e:
#             print(e)
#         self.num_of_samples = len(self.data)


class NodeBase(Node):
    version = 'v0.1'
    color = '#e60026'
    main_widget_pos = 'between ports'


class SoundAudioWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.signal = np.array([])

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        layout.setSizeConstraint(QLayout.SetFixedSize)  # Set the size constraint
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "speaker.png")
        image = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        imageLabel.setMargin(0)
        layout.addWidget(imageLabel)
        # button = QPushButton("Show Scope")
        # button.clicked.connect(self.window1)
        # layout.addWidget(button)
        self.setLayout(layout)


class ReadAudioWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.signal = np.array([])

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        layout.setSizeConstraint(QLayout.SetFixedSize)  # Set the size constraint
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "audio.png")
        image = QPixmap(icon_path).scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageLabel.setPixmap(image)
        imageLabel.setMargin(0)
        layout.addWidget(imageLabel)

        self.device_bit_depth_comboBox = QComboBox()
        # self.device_bit_depth_comboBox.addItem("8-bit integer")
        self.device_bit_depth_comboBox.addItem("16-bit integer")
        # self.device_bit_depth_comboBox.addItem("24-bit integer")
        # self.device_bit_depth_comboBox.addItem("32-bit integer")
        self.device_bit_depth_comboBox.setMaximumWidth(140)
        self.device_bit_depth_comboBox.setMinimumHeight(34)

        layout.addWidget(self.device_bit_depth_comboBox)

        self.output_data_type_comboBox = QComboBox()
        # self.output_data_type_comboBox.addItem("uint8")
        self.output_data_type_comboBox.addItem("int16")
        # self.output_data_type_comboBox.addItem("int32")
        self.output_data_type_comboBox.addItem("single")
        self.output_data_type_comboBox.addItem("double")
        self.output_data_type_comboBox.setMaximumWidth(140)
        self.output_data_type_comboBox.setMinimumHeight(34)

        self.device_bit_depth_comboBox.currentTextChanged.connect(self.bit_depth_change)
        self.output_data_type_comboBox.currentTextChanged.connect(self.output_data_type_change)
        self.device_bit_depth_comboBox.setCurrentText("16-bit integer")
        self.output_data_type_comboBox.setCurrentText("int16")
        # self.output_data_type_comboBox.setCurrentText("double")



        layout.addWidget(self.output_data_type_comboBox)

        self.setLayout(layout)
        self.setStyleSheet("""
                            QWidget {
                                background-color: white;
                            }
                            QLineEdit {
                                background-color: #1e242a;
                                color: white;
                                font-size: 12pt;
                            }
                            QWidget * {
                                background-color: white;
                                color: black;
                                font-size: 10pt;
                            }
                            
                        """)

        self.setLayout(layout)

    def bit_depth_change(self, bit_depth):
        format_map = {
            # "8-bit integer": pyaudio.paInt8,
            "16-bit integer": pyaudio.paInt16,
            # "24-bit integer": pyaudio.paInt24,
            # "32-bit integer": pyaudio.paInt32,
        }
        self.node.FORMAT = format_map[bit_depth]
        self.node.initialize_stream()  # Call the method to reinitialize the stream

    def output_data_type_change(self, data_type):
        dtype_map = {
            # "uint8": np.uint8,
            "int16": np.int16,
            # "int32": np.int32,
            "single": np.float32,
            "double": np.float64,
        }
        self.node.output_format = dtype_map[data_type]


class ReadAudio(NodeBase):
    title = 'Read Microphone'

    main_widget_class = ReadAudioWidget
    main_widget_pos = 'between ports'
    style = "large"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "audio.png")
    icon = icon_path

    init_inputs = [
        NodeInputBP(type_='exec'),
    ]

    init_outputs = [
        NodeOutputBP(),
    ]

    def __init__(self, params):
        super().__init__(params)

        # Parameters
        self.fs = self.get_var_val("fs")
        if self.fs is None:
            print("fs from globals")
            self.fs = globals.fs
        self.frame_size = self.get_var_val("frame_size")
        if self.frame_size is None:
            print("frame size from globals")
            self.frame_size = globals.frame_size
        self.CHUNK = self.frame_size  # Buffer size in samples
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1  # Mono
        self.RATE = self.fs  # Sample rate in Hz
        # self.output_format = np.int16
        self.output_format = np.int16

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        # Open a streaming stream
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)

    def update_event(self, inp=-1):
        if inp > -1:
            data = self.record_frame_samples()
            flag = 0
            # Convert flag to the same type as data
            flag_converted = np.array([flag], dtype=data.dtype)
            output_data = np.append(data, flag_converted)
            self.set_output_val(0, output_data)

    def initialize_stream(self):
        self.free()  # Close any existing stream
        try:
            self.stream = self.p.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.CHUNK)
        except IOError as e:
            print(f"Could not initialize the stream: {e}")
            # Handle initialization failure, possibly by notifying the user

    def record_frame_samples(self):
        # Record audio
        data = self.stream.read(self.CHUNK)

        dtype = self.output_format

        if dtype is np.float64 or dtype is np.float32:
            # Normalize 16-bit signed integers to float in range [-1, 1]
            audio_data = np.frombuffer(data, dtype=np.int16).astype(dtype) / (np.iinfo(np.int16).max + 1)
        elif dtype is np.uint8:
            # Normalize 16-bit signed integers to uint8 range
            audio_data = ((np.frombuffer(data, dtype=np.int16).astype(np.float64) + 32768) / 65535 * 255).astype(
                np.uint8)
        elif dtype is np.int32:
            # Scale 16-bit signed integers up to int32 range
            audio_data = (np.frombuffer(data, dtype=np.int16).astype(np.int32) << 16)
        else:
            # Directly use as integer types without normalization
            audio_data = np.frombuffer(data, dtype=dtype)

        return audio_data

    def free(self):
        # Stop the stream and terminate PyAudio
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


class PlayAudio(NodeBase):
    title = 'Speaker'
    style = 'large'

    main_widget_class = SoundAudioWidget
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "speaker.png")
    icon = icon_path

    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        # NodeOutputBP(),
    ]

    color = '#e60026'

    def __init__(self, params):
        super().__init__(params)

        # Parameters
        self.fs = self.get_var_val("fs")
        if self.fs is None:
            print("fs from globals")
            self.fs = globals.fs
        self.frame_size = self.get_var_val("frame_size")
        if self.frame_size is None:
            print("frame size from globals")
            self.frame_size = globals.frame_size
        self.CHUNK = self.frame_size  # Buffer size in samples
        self.FORMAT = pyaudio.paInt16  # Sample format
        self.CHANNELS = 1  # Mono
        self.RATE = self.fs  # Sample rate in Hz

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        # Open a streaming stream
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  output=True,
                                  frames_per_buffer=self.CHUNK)

    def update_event(self, inp=-1):
        if inp == 0:
            audio_data = self.input(0)

            audio_data = audio_data[:-1]  # Remove the last element
            if audio_data is not None:
                self.play_audio(audio_data)
            # self.exec_output(0)

    def play_audio(self, audio_data):
        if audio_data.size % self.CHUNK != 0:
            audio_data = np.pad(audio_data, (0, self.CHUNK - audio_data.size % self.CHUNK), 'constant')
        for i in range(0, audio_data.size, self.CHUNK):
            frame = audio_data[i:i + self.CHUNK]
            if frame.dtype == np.float32 or frame.dtype == np.float64:
                # Assuming the floating-point data is normalized to [-1.0, 1.0]
                frame = np.int16(frame * 32767)
                pass
            self.stream.write(frame.tobytes())

    def free(self):
        # Stop the stream and terminate PyAudio
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


class WriteAudioWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.signal = np.array([])

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins to 0
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "write.png")
        image = QPixmap(icon_path)
        imageLabel.setPixmap(image)
        layout.addWidget(imageLabel)
        self.window = QWidget()
        self.window.setWindowTitle("Write Destination")

        # Main layout
        main_layout = QVBoxLayout()

        # First group box for File Parameters
        file_params_group = QGroupBox("File Parameters")
        file_params_layout = QVBoxLayout()

        file_name_layout = QHBoxLayout()
        file_name_label = QLabel("File name:")
        self.file_name_edit = QLineEdit("output.wav")
        file_name_layout.addWidget(file_name_label)
        file_name_layout.addWidget(self.file_name_edit)
        file_params_layout.addLayout(file_name_layout)

        # Add more widgets for file type, audio compressor, etc. here

        file_params_group.setLayout(file_params_layout)
        main_layout.addWidget(file_params_group)

        # Second group box for Audio Parameters (similar to the first one)

        # Create OK and Cancel buttons
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.ok_clicked)
        cancel_button.clicked.connect(self.cancel_clicked)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        # Add buttons layout to main layout
        main_layout.addLayout(buttons_layout)

        self.window.setLayout(main_layout)
        self.label = QLabel("output.wav")
        self.setStyleSheet("background-color: white; color: black;")
        self.label.setStyleSheet("background-color: white; color: black; font:10pt;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.singleClickAction)
        self.click_count = 0

    def ok_clicked(self):
        file_name = self.file_name_edit.text().strip()  # Get the text and strip whitespace
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, file_name)

        # Check if the file name already has a .wav extension
        if not file_name.lower().endswith('.wav'):
            file_path += '.wav'

        # Set the output file path
        self.node.output_file = file_path

        label = f"{os.path.basename(file_path)}"
        self.label.setText(label)
        # Now check if the file exists
        if os.path.isfile(file_path):
            # File exists, you can perform operations like prompting user it will be overwritten or just use it as is
            print(f"File already exists: {file_path}")
        else:
            # File does not exist, you can create it or set it up to be created when data is written
            print(f"File will be created: {file_path}")

        # Assuming you want to close the window after clicking OK
        self.window.close()

    def cancel_clicked(self):
        # Handle the Cancel button click event
        self.window.close()

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


class WriteWavAudio(NodeBase):
    title = 'Write Audio to File'
    main_widget_class = WriteAudioWidget

    init_inputs = [
        NodeInputBP(),
    ]

    init_outputs = [
        # NodeOutputBP(),
    ]

    color = '#e60026'
    style = "large"
    main_widget_pos = 'between ports'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "write.png")
    icon = icon_path


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

        self.CHUNK = self.frame_size  # Buffer size in samples
        self.FORMAT = pyaudio.paInt16  # Sample format
        self.CHANNELS = 1  # Mono
        self.RATE = self.fs  # Sample rate in Hz

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_file = os.path.join(script_dir, "output.wav")
        self.wave_file = None
        self.p = pyaudio.PyAudio()

    def update_event(self, inp=-1):
        if inp == 0:
            audio_data = self.input(0)
            if audio_data is not None:
                self.write_audio(audio_data[:-1])
            self.exec_output(0)

    def write_audio(self, audio_data):
        if self.wave_file is None:
            self.wave_file = wave.open(self.output_file, 'wb')
            self.wave_file.setnchannels(self.CHANNELS)
            self.wave_file.setsampwidth(self.p.get_sample_size(self.FORMAT))
            self.wave_file.setframerate(self.RATE)

        self.wave_file.writeframes(audio_data.tobytes())

    def remove_event(self):
        if self.wave_file is not None:
            self.wave_file.close()
            self.wave_file = None

    import librosa


class WavWidget(MWB, QWidget):
    path_chosen = Signal(str)
    signalWAV = Signal(np.ndarray)

    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        layout = QVBoxLayout()
        imageLabel = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "read WAV.png")
        # image = QPixmap(icon_path)
        image = QPixmap(icon_path).scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        imageLabel.setPixmap(image)
        # Add the following line to set the background color to white
        imageLabel.setStyleSheet("background-color: white;")
        layout.addWidget(imageLabel)
        self.setLayout(layout)

        # initialize signalWAV_data as None
        self.signalWAV_data = None

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        file_path = QFileDialog.getOpenFileName(self, 'Select wav file', filter="Wav files (*.wav)")[0]
        try:
            file_path = os.path.relpath(file_path)
        except ValueError:
            return

        self.path_chosen.emit(file_path)

        # Load the wav file
        samplerate, audio = wavfile.read(file_path)
        self.signalWAV.emit(audio)

        # set signalWAV_data as the numpy array
        self.signalWAV_data = audio

        print(len(self.signalWAV_data))
        print(type(self.signalWAV_data))

    def isSignalWAVSet(self):
        return self.signalWAV_data is not None

    def returnWavData(self):
        return self.signalWAV_data
#
#
class ReadWav(Node):
    title = 'Read From WAV'
    main_widget_class = WavWidget
    main_widget_pos = 'between ports'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icons", "read WAV.png")
    icon = icon_path
    init_inputs = [
        NodeInputBP(type_='exec'),
    ]
    init_outputs = [
        NodeOutputBP(),
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params)

        self.data = None
        self.num_of_samples = None
        self.i = 0
        self.first_time = True

    def update_event(self, inp=-1):
        if inp > -1:

            if self.first_time and not self.main_widget().isSignalWAVSet():
                return
            if self.first_time and self.main_widget().isSignalWAVSet():
                self.data = self.main_widget().returnWavData()
                self.first_time = False
            if self.i + self.frame_size >= len(self.data):
                remaining = len(self.data) - self.i
                output_data = np.concatenate((self.data[self.i:], self.data[:self.frame_size - remaining]))
                self.i = self.frame_size - remaining
            else:
                output_data = self.data[self.i:self.i + self.frame_size]
                self.i += self.frame_size
            print(f'length is {len(output_data)}')
            self.set_output_val(0, output_data)


nodes = [
    ReadAudio,
    PlayAudio,
    ReadWavAudio,
    WriteWavAudio,
    # ReadWav,
]
