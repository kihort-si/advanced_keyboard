import sys
import json
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from pynput import keyboard
import threading
import ctypes
import logging

logging.basicConfig(
    filename="shortcut_replacer.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

PRESET_REPLACEMENTS = {
    "--": "—",
    "...": "…",
    "(c)": "©",
    "(r)": "®",
    "(tm)": "™"
}


class PresetSelectionWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Preset Replacements")
        self.setGeometry(200, 200, 300, 400)

        self.layout = QtWidgets.QVBoxLayout()

        self.preset_list = QtWidgets.QListWidget(self)
        self.preset_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        for trigger, replacement in PRESET_REPLACEMENTS.items():
            item = QtWidgets.QListWidgetItem(f"{trigger} -> {replacement}")
            item.setData(Qt.UserRole, (trigger, replacement))
            self.preset_list.addItem(item)

        self.import_button = QtWidgets.QPushButton("Import Selected", self)
        self.import_button.clicked.connect(self.accept)

        self.layout.addWidget(self.preset_list)
        self.layout.addWidget(self.import_button)

        self.setLayout(self.layout)

    def get_selected_presets(self):
        selected = []
        for item in self.preset_list.selectedItems():
            selected.append(item.data(Qt.UserRole))
        return selected


class ShortcutReplacer:
    def __init__(self):
        self.replacements = {}
        self.current_text = ""
        self.listener = None
        self.load_rules()
        self.validate_rules()

    def add_replacement(self, trigger, replacement):
        self.replacements[trigger] = replacement
        self.save_rules()

    def remove_replacement(self, trigger):
        if trigger in self.replacements:
            del self.replacements[trigger]
            self.save_rules()

    def save_rules(self):
        try:
            with open("rules.json", "w") as file:
                json.dump(self.replacements, file)
                logging.info("Rules saved successfully.")
        except Exception as e:
            logging.error(f"Error saving rules: {e}")

    def load_rules(self):
        try:
            with open("rules.json", "r") as file:
                self.replacements = json.load(file)
                logging.info("Rules loaded successfully.")
        except FileNotFoundError:
            self.replacements = {}
            logging.warning("Rules file not found. Starting with an empty set of rules.")
        except Exception as e:
            logging.error(f"Error loading rules: {e}")

    def validate_rules(self):
        if not isinstance(self.replacements, dict):
            logging.error("Invalid rules format detected. Resetting to default.")
            self.replacements = {}

    def import_presets(self):
        self.replacements.update(PRESET_REPLACEMENTS)
        self.save_rules()
        logging.info("Preset replacements imported.")

    def start(self):
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char:
                    self.current_text += key.char
                    for trigger, replacement in self.replacements.items():
                        if self.current_text.endswith(trigger):
                            for _ in range(len(trigger)):
                                keyboard.Controller().press(keyboard.Key.backspace)
                                keyboard.Controller().release(keyboard.Key.backspace)
                            keyboard.Controller().type(replacement)
                            self.current_text = ""
            except Exception as e:
                logging.error(f"Error during key press handling: {e}")

        try:
            self.listener = keyboard.Listener(on_press=on_press)
            self.listener.start()
            logging.info("Listener started successfully.")
        except Exception as e:
            self.listener = None
            logging.error(f"Error starting listener: {e}")

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()
            logging.info("Listener stopped successfully.")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.replacer = ShortcutReplacer()

        self.setWindowTitle("Advanced Keyboard")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setGeometry(100, 100, 600, 500)

        self.layout = QtWidgets.QVBoxLayout()

        self.trigger_input = QtWidgets.QLineEdit(self)
        self.trigger_input.setPlaceholderText("Enter trigger text")
        self.replacement_input = QtWidgets.QLineEdit(self)
        self.replacement_input.setPlaceholderText("Enter replacement text")

        self.add_button = QtWidgets.QPushButton("Add Rule", self)
        self.add_button.clicked.connect(self.add_rule)

        self.import_button = QtWidgets.QPushButton("Import Presets", self)
        self.import_button.clicked.connect(self.open_preset_window)

        self.rules_list = QtWidgets.QListWidget(self)
        self.load_rules_into_list()

        self.start_button = QtWidgets.QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_replacer)
        self.stop_button = QtWidgets.QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_replacer)

        self.autostart_checkbox = QtWidgets.QCheckBox("Enable Autostart", self)
        self.autostart_checkbox.setChecked(self.check_autostart())
        self.autostart_checkbox.stateChanged.connect(self.toggle_autostart)

        self.layout.addWidget(self.trigger_input)
        self.layout.addWidget(self.replacement_input)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.import_button)
        self.layout.addWidget(self.rules_list)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.autostart_checkbox)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def add_rule(self):
        trigger = self.trigger_input.text()
        replacement = self.replacement_input.text()
        if trigger and replacement:
            self.replacer.add_replacement(trigger, replacement)
            self.rules_list.addItem(f"{trigger} -> {replacement}")
            self.trigger_input.clear()
            self.replacement_input.clear()
            logging.info(f"Added rule: {trigger} -> {replacement}")

    def open_preset_window(self):
        dialog = PresetSelectionWindow(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_presets = dialog.get_selected_presets()
            for trigger, replacement in selected_presets:
                self.replacer.add_replacement(trigger, replacement)
            self.load_rules_into_list()
            logging.info("Selected presets imported into the rules list.")

    def load_rules_into_list(self):
        self.rules_list.clear()
        for trigger, replacement in self.replacer.replacements.items():
            self.rules_list.addItem(f"{trigger} -> {replacement}")

    def start_replacer(self):
        threading.Thread(target=self.replacer.start, daemon=True).start()
        logging.info("Shortcut replacer started.")

    def stop_replacer(self):
        self.replacer.stop()
        logging.info("Shortcut replacer stopped.")

    def check_autostart(self):
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup',
                                    'ShortcutReplacer.lnk')
        return os.path.exists(startup_path)

    def toggle_autostart(self, state):
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup',
                                    'ShortcutReplacer.lnk')
        exe_path = sys.executable
        if state == Qt.Checked:
            try:
                self.create_autostart_shortcut(startup_path, exe_path)
                logging.info("Autostart enabled.")
            except Exception as e:
                logging.error(f"Failed to enable autostart: {e}")
        else:
            try:
                if os.path.exists(startup_path):
                    os.remove(startup_path)
                    logging.info("Autostart disabled.")
            except Exception as e:
                logging.error(f"Failed to disable autostart: {e}")

    def create_autostart_shortcut(self, shortcut_path, target_path):
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.Save()
            logging.info("Autostart shortcut created successfully.")
        except ImportError:
            logging.error("Error: pywin32 module is required for creating shortcuts")
        except Exception as e:
            logging.error(f"Error creating autostart shortcut: {e}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
