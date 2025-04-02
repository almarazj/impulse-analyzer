import sys
import json
from PyQt5.QtWidgets import QApplication
from src.gui import ImpulseAnalyzrGUI

CONFIG_PATH = "config.json"
try:
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print(f"Error: Configuration file '{CONFIG_PATH}' not found.")
    sys.exit(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImpulseAnalyzrGUI(config)
    window.show()
    sys.exit(app.exec_())