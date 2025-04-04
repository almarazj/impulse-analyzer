import os
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QPixmap, QIntValidator
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QRadioButton, QLineEdit, QComboBox, QCheckBox, QTabWidget,
    QWidget, QTableWidget, QHeaderView, QFileDialog, QFrame, QScrollArea, QMessageBox)

from src.utils.audio_utils import import_ir, cut_ir, AudioData
from src.utils.plots_utils import plot_ir, placeholder_plot


class ImpulseAnalyzrGUI(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.setWindowTitle("ImpulseAnalyzr")
        self.setMinimumSize(1100, 600)
        self.resize(1200, 800)
        
        self.config = config
        self.load_config_parameters()
        self.audio_data = None
        self.last_directory = ""
        
        self.setup_ui()
        self.setup_connections()
        
        
    def load_config_parameters(self):
        """Extract parameters from config."""
        self.OCTAVE_BANDS = self.config["frequency_bands"]["octave"]
        self.THIRD_OCTAVE_BANDS = self.config["frequency_bands"]["third_octave"]
        self.PARAMETERS = self.config["parameters"]
        self.FILTER_OPTIONS = self.config["combos"]["filter"]
        self.SMOOTHING_OPTIONS = self.config["combos"]["smoothing"]
        self.COLUMN_WIDTH = self.config["column_width"]


    def setup_ui(self):
        """Set up the UI components."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.setup_left_panel()
        self.setup_right_panel()
        
        
    def setup_left_panel(self):
        """Set up the left panel of the GUI."""
        self.left_panel = QVBoxLayout()
        self.left_panel_widget = QWidget()
        self.left_panel_widget.setLayout(self.left_panel)
        self.left_panel_widget.setFixedWidth(300)
        self.main_layout.addWidget(self.left_panel_widget)
        
        self.setup_logo()
        self.setup_import_tabs()
        self.setup_options_panel()
        self.setup_actions_panel()
        
    
    def setup_logo(self):
        """Set up the logo in the left panel."""
        self.logo_label = QLabel()
        pixmap = QPixmap("res/u3f.png").scaled(280, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.left_panel.addWidget(self.logo_label)


    def setup_import_tabs(self):
        """Set up the import tabs in the left panel."""
        # Left Panel: Tabs for Import
        self.tab_widget = QTabWidget()
        self.tab_ir = QWidget()
        self.tab_ss = QWidget()
        self.tab_widget.addTab(self.tab_ir, "Import IR")
        self.tab_widget.addTab(self.tab_ss, "Import SS")
        self.left_panel.addWidget(self.tab_widget)
        
        self.setup_import_ir_tab()
        self.setup_import_ss_tab()
        
    
    def setup_import_ir_tab(self):
        """Set up the Import IR tab."""
        # Tab: Import Impulse Response
        self.tab_ir_layout = QVBoxLayout(self.tab_ir)
        self.ir_file_layout = QHBoxLayout()
        self.ir_name_input = QLineEdit()
        self.ir_name_input.setPlaceholderText("Select file...")
        self.browse_ir_button = QPushButton("Browse...")
        self.ir_file_layout.addWidget(self.ir_name_input)
        self.ir_file_layout.addWidget(self.browse_ir_button)
        self.tab_ir_layout.addLayout(self.ir_file_layout)

        self.ir_channel_layout = QHBoxLayout()
        self.ch_left = QRadioButton("Left Channel")
        self.ch_right = QRadioButton("Right Channel")
        self.ir_channel_layout.addWidget(self.ch_left)
        self.ir_channel_layout.addWidget(self.ch_right)
        self.tab_ir_layout.addLayout(self.ir_channel_layout)
        
        self.file_label = QLabel("File Name: --")
        self.fs_label = QLabel("Sample Rate: --")
        self.ch_label = QLabel("Number of Channels: --")
        self.len_label = QLabel("File Duration: --")
        self.tab_ir_layout.addWidget(self.file_label)
        self.tab_ir_layout.addWidget(self.fs_label)
        self.tab_ir_layout.addWidget(self.ch_label)
        self.tab_ir_layout.addWidget(self.len_label)


    def setup_import_ss_tab(self):
        """Set up the Import Sine Sweep tab."""
        # Tab: Import Sine Sweep
        self.tab_ss_layout = QVBoxLayout(self.tab_ss)
        self.ss_file_layout = QHBoxLayout()
        self.ss_name_input = QLineEdit()
        self.ss_name_input.setPlaceholderText("Select Sine Sweep file...")
        self.browse_ss_button = QPushButton("Browse...")
        self.ss_file_layout.addWidget(self.ss_name_input)
        self.ss_file_layout.addWidget(self.browse_ss_button)
        self.tab_ss_layout.addLayout(self.ss_file_layout)

    
    def setup_options_panel(self):
        """Set up the options panel in the left panel."""
        # Left Panel: Options
        self.options_frame = QFrame()
        self.options_frame.setFrameShape(QFrame.StyledPanel)
        self.options_layout = QGridLayout(self.options_frame)
        self.left_panel.addWidget(self.options_frame)

        self.filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(self.FILTER_OPTIONS)
        self.options_layout.addWidget(self.filter_label, 0, 0)
        self.options_layout.addWidget(self.filter_combo, 0, 1)

        self.smoothing_label = QLabel("Smoothing:")
        self.smoothing_combo = QComboBox()
        self.smoothing_combo.addItems(self.SMOOTHING_OPTIONS)
        self.options_layout.addWidget(self.smoothing_label, 1, 0)
        self.options_layout.addWidget(self.smoothing_combo, 1, 1)

        self.lundeby_checkbox = QCheckBox("Lundeby")
        self.options_layout.addWidget(self.lundeby_checkbox, 2, 0)

        self.window_length_layout = QHBoxLayout()
        self.window_length_label = QLabel("Window length:")
        self.window_length_input = QLineEdit()
        self.window_length_input.setPlaceholderText("ms")
        self.window_length_input.setValidator(QIntValidator(0, 999))
        self.window_length_layout.addWidget(self.window_length_label)
        self.window_length_layout.addWidget(self.window_length_input)
        self.options_layout.addLayout(self.window_length_layout, 2, 1)
        
        
    def setup_actions_panel(self):
        """Set up the actions panel in the left panel."""
        # Left Panel: Actions
        self.actions_frame = QFrame()
        self.actions_frame.setFrameShape(QFrame.StyledPanel)
        self.actions_layout = QVBoxLayout(self.actions_frame)
        self.left_panel.addWidget(self.actions_frame)

        self.calculate_button = QPushButton("Calculate!")
        self.clear_button = QPushButton("Clear")
        self.export_button = QPushButton("Export as CSV")
        self.copy_button = QPushButton("Copy to Clipboard")
        self.actions_layout.addWidget(self.calculate_button)
        self.actions_layout.addWidget(self.clear_button)
        self.actions_layout.addWidget(self.export_button)
        self.actions_layout.addWidget(self.copy_button)


    def setup_right_panel(self):
        """Set up the right panel of the GUI."""
        # Right Panel
        self.right_panel = QVBoxLayout()
        self.right_panel_widget = QWidget()
        self.right_panel_widget.setLayout(self.right_panel)
        self.main_layout.addWidget(self.right_panel_widget, stretch=3)
        
        self.setup_plot_area()
        self.setup_table_area()
    
    
    def setup_plot_area(self):
        """Set up the plot area in the right panel."""       
        # Right Panel: Plot Area
        self.plot_frame = QFrame()
        self.plot_frame.setFrameShape(QFrame.StyledPanel)
        self.plot_frame.setMinimumHeight(300)
        self.right_panel.addWidget(self.plot_frame, stretch=1)
        self.figure, self.canvas = placeholder_plot(self.plot_frame)


    def setup_table_area(self):
        """Set up the table area in the right panel."""
        # Right Panel: Table Area
        self.table_widget = QTableWidget(8, len(self.OCTAVE_BANDS) + 1)
        self.table_widget.setHorizontalHeaderLabels(["Param."] + self.OCTAVE_BANDS)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.set_table_height()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.table_widget)
        self.scroll_area.setFixedHeight(self.table_widget.height())
        self.right_panel.addWidget(self.scroll_area)
    
    
    # CONNECTIONS
    def setup_connections(self):
        """Set up signal-slot connections."""
        # File browsing
        self.browse_ir_button.clicked.connect(self.on_browse_ir_clicked)
        self.browse_ss_button.clicked.connect(self.on_browse_ss_clicked)
        
        # Channel selection
        self.ch_left.toggled.connect(self.on_channel_toggled)
        self.ch_right.toggled.connect(self.on_channel_toggled)

        # Actions
        # self.calculate_button.clicked.connect(self.on_calculate_clicked)
        # self.clear_button.clicked.connect(self.on_clear_clicked)
        # self.export_button.clicked.connect(self.on_export_clicked)
        # self.copy_button.clicked.connect(self.on_copy_clicked)
        
        # Filter and smoothing options
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        self.smoothing_combo.currentIndexChanged.connect(self.on_smoothing_changed)

        
    def on_browse_ir_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Impulse Response File", "", "All Files (*)")
        if not file_name:
            return
        try:
            self.ir_name_input.setText(file_name)
            self.audio_data = import_ir(file_name)

            self.file_label.setText(f"File Name: {os.path.basename(file_name)}")
            self.fs_label.setText(f"Sample Rate: {self.audio_data.sample_rate} Hz")
            self.ch_label.setText(f"Number of Channels: {2 if self.audio_data.is_stereo else 1}")
            self.len_label.setText(f"File Duration: {round(self.audio_data.duration, 2)} s")
                
            self.update_channel_buttons(self.audio_data.is_stereo)
    
            plot_ir(self.figure, self.audio_data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")      


    def on_browse_ss_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Sine Sweep File", "", "All Files (*)")
        if file_name:
            self.ss_name_input.setText(file_name) 

       
    def on_channel_toggled(self):
        if self.ch_left.isChecked() and self.audio_data:
            plot_ir(self.figure, self.audio_data, channel="L")
        elif self.ch_right.isChecked() and self.audio_data:
            plot_ir(self.figure, self.audio_data, channel="R")
 

    def update_channel_buttons(self, is_stereo):
        """Update the state of the channel radio buttons based on whether the file is stereo or mono."""
        self.ch_left.setChecked(False)
        self.ch_right.setChecked(False)
        
        if is_stereo:
            self.ch_left.setDisabled(False)
            self.ch_right.setDisabled(False)
        else:
            self.ch_left.setDisabled(True)
            self.ch_right.setDisabled(True) 


    def on_filter_changed(self):
        selected_filter = self.filter_combo.currentText()
        if selected_filter == "Octave Bands":
            headers = ["Param."] + self.OCTAVE_BANDS
        elif selected_filter == "Third Octave Bands":
            headers = ["Param."] + self.THIRD_OCTAVE_BANDS
            
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.set_column_behavior()


    def on_smoothing_changed(self):
        """Update the state of Lundeby checkbox and window length input based on smoothing option."""
        selected_smoothing = self.smoothing_combo.currentText()
        if selected_smoothing == "Moving Median Avg.":
            self.lundeby_checkbox.setEnabled(False)
            self.lundeby_checkbox.setChecked(False)
            self.window_length_input.setEnabled(True)
        elif selected_smoothing == "Schroeder":
            self.lundeby_checkbox.setEnabled(True)
            self.window_length_input.setEnabled(False)
            self.window_length_input.clear()
        else:
            self.lundeby_checkbox.setEnabled(True)
            self.window_length_input.setEnabled(True)


    # BEHAVIOR
    def showEvent(self, event):
        super().showEvent(event)
        self.set_column_behavior()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_column_behavior()
        self.resize_plot()
    
        
    def resize_plot(self):
        if hasattr(self, 'canvas') and self.canvas is not None:
            self.figure.tight_layout()
            self.canvas.draw()
    
    
    def set_table_height(self):
        table_height = self.table_widget.horizontalHeader().height()
        for row in range(self.table_widget.rowCount()):
            table_height += self.table_widget.rowHeight(row)
        self.table_widget.setFixedHeight(table_height)
        
        
    def set_column_behavior(self):
        total_table_width = self.table_widget.verticalHeader().width() + self.table_widget.horizontalHeader().length()
        available_width = self.scroll_area.width()

        if total_table_width <= available_width:
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            for col in range(self.table_widget.columnCount()):
                self.table_widget.setColumnWidth(col, self.COLUMN_WIDTH)

        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)