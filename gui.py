import sys
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QPixmap, QIntValidator
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QRadioButton, QLineEdit, QComboBox, QCheckBox, QTabWidget,
    QWidget, QTableWidget, QHeaderView, QFileDialog, QFrame, QScrollArea)


with open("config.json", "r") as config_file:
    config = json.load(config_file)

OCTAVE_BANDS = config["frequency_bands"]["octave"]
THIRD_OCTAVE_BANDS = config["frequency_bands"]["third_octave"]
PARAMETERS = config["parameters"]
FILTER_OPTIONS = config["combos"]["filter"]
SMOOTHING_OPTIONS = config["combos"]["smoothing"]
COLUMN_WIDTH = config["column_width"]


class ImpulseAnalyzrGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImpulseAnalyzr")
        self.setMinimumSize(1100, 600)


        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)


        # Left Panel
        self.left_panel = QVBoxLayout()
        self.left_panel_widget = QWidget()
        self.left_panel_widget.setLayout(self.left_panel)
        self.left_panel_widget.setFixedWidth(300)
        self.main_layout.addWidget(self.left_panel_widget)


        # Right Panel
        self.right_panel = QVBoxLayout()
        self.right_panel_widget = QWidget()
        self.right_panel_widget.setLayout(self.right_panel)
        self.main_layout.addWidget(self.right_panel_widget, stretch=3)


        # Left Panel: Logo
        self.logo_label = QLabel()
        pixmap = QPixmap("res/u3f.png").scaled(280, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.left_panel.addWidget(self.logo_label)


        # Left Panel: Tabs for Import
        self.tab_widget = QTabWidget()
        self.tab_ir = QWidget()
        self.tab_ss = QWidget()
        self.tab_widget.addTab(self.tab_ir, "Import IR")
        self.tab_widget.addTab(self.tab_ss, "Import SS")
        self.left_panel.addWidget(self.tab_widget)


        # Tab: Import Impulse Response
        self.tab_ir_layout = QVBoxLayout(self.tab_ir)
        self.ir_file_layout = QHBoxLayout()
        self.ir_name_input = QLineEdit()
        self.ir_name_input.setPlaceholderText("Select file...")
        self.browse_ir_button = QPushButton("Browse...")
        self.browse_ir_button.clicked.connect(self.browse_ir_file)
        self.ir_file_layout.addWidget(self.ir_name_input)
        self.ir_file_layout.addWidget(self.browse_ir_button)
        self.tab_ir_layout.addLayout(self.ir_file_layout)

        self.ir_channel_layout = QHBoxLayout()
        self.ch_left = QRadioButton("Left Channel")
        self.ch_right = QRadioButton("Right Channel")
        self.ir_channel_layout.addWidget(self.ch_left)
        self.ir_channel_layout.addWidget(self.ch_right)
        self.tab_ir_layout.addLayout(self.ir_channel_layout)


        # Tab: Import Sine Sweep
        self.tab_ss_layout = QVBoxLayout(self.tab_ss)
        self.ss_file_layout = QHBoxLayout()
        self.ss_name_input = QLineEdit()
        self.ss_name_input.setPlaceholderText("Select Sine Sweep file...")
        self.browse_ss_button = QPushButton("Browse...")
        self.browse_ss_button.clicked.connect(self.browse_ss_file)
        self.ss_file_layout.addWidget(self.ss_name_input)
        self.ss_file_layout.addWidget(self.browse_ss_button)
        self.tab_ss_layout.addLayout(self.ss_file_layout)


        # Left Panel: Options
        self.options_frame = QFrame()
        self.options_frame.setFrameShape(QFrame.StyledPanel)
        self.options_layout = QGridLayout(self.options_frame)
        self.left_panel.addWidget(self.options_frame)

        self.filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(FILTER_OPTIONS)
        self.filter_combo.currentIndexChanged.connect(self.update_table_headers)
        self.options_layout.addWidget(self.filter_label, 0, 0)
        self.options_layout.addWidget(self.filter_combo, 0, 1)

        self.smoothing_label = QLabel("Smoothing:")
        self.smoothing_combo = QComboBox()
        self.smoothing_combo.addItems(SMOOTHING_OPTIONS)
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


        # Right Panel: Plot Area
        self.plot_frame = QFrame()
        self.plot_frame.setFrameShape(QFrame.StyledPanel)
        self.plot_frame.setMinimumHeight(300)
        self.right_panel.addWidget(self.plot_frame, stretch=1)
        self.init_placeholder_plot()

        # Right Panel: Table Area
        self.table_widget = QTableWidget(8, len(OCTAVE_BANDS) + 1)
        self.table_widget.setHorizontalHeaderLabels(["Param."] + OCTAVE_BANDS)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.set_table_height()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.table_widget)
        self.scroll_area.setFixedHeight(self.table_widget.height())
        self.right_panel.addWidget(self.scroll_area)
        

    def set_table_height(self):
        table_height = self.table_widget.horizontalHeader().height()
        for row in range(self.table_widget.rowCount()):
            table_height += self.table_widget.rowHeight(row)
        self.table_widget.setFixedHeight(table_height)

    def showEvent(self, event):
        super().showEvent(event)
        self.set_column_behavior()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_column_behavior()
        
        
    def browse_ir_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Impulse Response File", "", "All Files (*)")
        if file_name:
            self.ir_name_input.setText(file_name)


    def browse_ss_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Sine Sweep File", "", "All Files (*)")
        if file_name:
            self.ss_name_input.setText(file_name)        
       
       
    def init_placeholder_plot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self.plot_frame)
        layout.addWidget(self.canvas)

        ax = self.figure.add_subplot(111)
        ax.plot([0, 1, 2, 3], [0, 1, 0, 1], label="Placeholder Line")
        ax.set_title("Placeholder Plot")
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        ax.legend()

        self.canvas.draw()       
        
        
    def set_column_behavior(self):
        total_table_width = self.table_widget.verticalHeader().width() + self.table_widget.horizontalHeader().length()
        available_width = self.scroll_area.width()

        if total_table_width <= available_width:
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            for col in range(self.table_widget.columnCount()):
                self.table_widget.setColumnWidth(col, COLUMN_WIDTH)

        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
           
                
    def update_table_headers(self):
        selected_filter = self.filter_combo.currentText()
        if selected_filter == "Octave Bands":
            headers = ["Param."] + OCTAVE_BANDS
        elif selected_filter == "Third Octave Bands":
            headers = ["Param."] + THIRD_OCTAVE_BANDS
            
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.set_column_behavior()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImpulseAnalyzrGUI()
    window.show()
    sys.exit(app.exec_())