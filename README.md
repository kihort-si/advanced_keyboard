# Advanced Keyboard

A Python application for managing keyboard shortcuts to automatically replace text sequences. Ideal for writers, developers, and anyone looking to save time while typing.

## Features

- Define custom text replacement rules.
- Works globally in any application.
- User-friendly graphical interface (GUI) using PyQt5.
- Autostart functionality to launch the program on system boot.
- Background process monitoring keyboard inputs.
- Supports saving and loading of replacement rules.
- Logs important events for debugging and monitoring.

## Installation

### Requirements

- Windows OS
- Python 3.8 or higher
- Required Python libraries:
  - `PyQt5`
  - `pynput`
  - `pywin32`

### Steps

1. Clone this repository:

   ```bash
   git clone https://github.com/kihort-si/advanced_keyboard.git
   cd advanced_keyboard
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the program:

   ```bash
   python main.py
   ```

### Executable File

To simplify usage, download the prebuilt executable file from the [Releases](https://github.com/kihort-si/advanced_keyboard/releases/latest) page.

## Usage

1. Launch the application.
2. Define your custom replacement rules:
   - Enter the text to replace (trigger).
   - Enter the replacement text.
   - Click "Add Rule."
3. Start the program by clicking the "Start" button.
4. Enable autostart from the settings to automatically run the program on system boot.

## Development

If you'd like to contribute or build the project locally:

### Build Executable

1. Install `pyinstaller`:

   ```bash
   pip install pyinstaller
   ```

2. Build the executable:

   ```bash
   pyinstaller --onefile --windowed main.py
   ```

3. The executable will be available in the `dist/` folder.

## Logging

Logs are saved to `shortcut_replacer.log` in the same directory as the application. Check this file for troubleshooting.

## Contributing

Contributions are welcome! Please fork this repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Download

[Download the latest version (.exe)](https://github.com/kihort-si/advanced_keyboard/releases/latest)

