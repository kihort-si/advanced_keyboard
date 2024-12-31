import sys
import threading
from PyQt5 import QtGui, QtWidgets
from pynput import keyboard


class ShortcutReplacer:
    def __init__(self):
        self.replacements = {}
        self.currentText = ""
        self.listeners = None

    def add_replacement(self, trigger, value):
        self.replacements[trigger] = value

    def remove_replacement(self, trigger):
        if trigger in self.replacements:
            del self.replacements[trigger]

    def start(self):
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char:
                    self.currentText += key.char
                    for trigger, value in self.replacements.items():
                        if self.currentText.endswith(trigger):
                            for _ in range(len(trigger)):
                                keyboard.Controller().press(keyboard.Key.backspace),
                                keyboard.Controller().release(keyboard.Key.backspace),
                            keyboard.Controller().type(value)
                            self.currentText = ""
            except Exception as e:
                print(f"Error: {e}")

        self.listeners = keyboard.Listener(on_press=on_press)
        self.listeners.start()

    def stop(self):
        if self.listeners:
            self.listeners.stop()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.replacer = ShortcutReplacer()

        self.setWindowTitle("Advanced Keyboard")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QtWidgets.QVBoxLayout()

        self.trigger_input = QtWidgets.QLineEdit(self)
        self.trigger_input.setPlaceholderText("Enter trigger text")
        self.replacement_input = QtWidgets.QLineEdit(self)
        self.replacement_input.setPlaceholderText("Enter replacement text")

        self.add_button = QtWidgets.QPushButton("Add Rule", self)
        self.add_button.clicked.connect(self.add_rule)

        self.rules_list = QtWidgets.QListWidget(self)

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

    def start_replacer(self):
        threading.Thread(target=self.replacer.start, daemon=True).start()

    def stop_replacer(self):
        self.replacer.stop()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
