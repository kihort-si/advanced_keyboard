import sys
import json
from PyQt5 import QtWidgets, QtGui
from pynput import keyboard
import threading


class ShortcutReplacer:
    def __init__(self):
        self.replacements = {}
        self.current_text = ""
        self.listener = None
        self.load_rules()

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
        except Exception as e:
            print(f"Error saving rules: {e}")

    def load_rules(self):
        try:
            with open("rules.json", "r") as file:
                self.replacements = json.load(file)
        except FileNotFoundError:
            self.replacements = {}
        except Exception as e:
            print(f"Error loading rules: {e}")

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
                print(f"Error: {e}")

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.replacer = ShortcutReplacer()

        self.setWindowTitle("Shortcut Replacer")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QtWidgets.QVBoxLayout()

        self.trigger_input = QtWidgets.QLineEdit(self)
        self.trigger_input.setPlaceholderText("Enter trigger text")
        self.replacement_input = QtWidgets.QLineEdit(self)
        self.replacement_input.setPlaceholderText("Enter replacement text")

        self.add_button = QtWidgets.QPushButton("Add Rule", self)
        self.add_button.clicked.connect(self.add_rule)

        self.rules_list = QtWidgets.QListWidget(self)
        self.load_rules_into_list()

        self.start_button = QtWidgets.QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_replacer)
        self.stop_button = QtWidgets.QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_replacer)

        self.layout.addWidget(self.trigger_input)
        self.layout.addWidget(self.replacement_input)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.rules_list)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)

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

    def load_rules_into_list(self):
        self.rules_list.clear()
        for trigger, replacement in self.replacer.replacements.items():
            self.rules_list.addItem(f"{trigger} -> {replacement}")

    def start_replacer(self):
        threading.Thread(target=self.replacer.start, daemon=True).start()

    def stop_replacer(self):
        self.replacer.stop()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
