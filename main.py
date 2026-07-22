""" The main REPL for the system. This file is responsible for initializing the LCD, handling user input, and calling the tools to perform the desired actions. It serves as the entry point for the application. """

import sys

from LCD1602 import CharLCD1602
from input_handler import get_single_keypress


def main():
    """
    The main function that initializes the LCD and starts the REPL loop.
    """
    lcd = CharLCD1602()
    lcd.init_lcd(addr=None, bl=1)

    try:
        while True:
            input_buffer = ""

            char = get_single_keypress()

            # Handle Ctrl+C or Escape to Exit
            if char in ('\x03', '\x1b'):
                print("Exiting...")
                break

            # Handle Enter Key (Execute Command)
            if char in ('\r', '\n'):
                print(f"Executing command: {input_buffer}")
                # Here you would call the appropriate function to handle the command.
                # For demonstration, we'll just clear the input buffer.
                input_buffer = ""
                lcd.clear()
                continue

            # Handle Backspace Key
            elif char in ('\x7f', '\x08'):
                input_buffer = input_buffer[:-1]

    except KeyboardInterrupt:
        lcd.destroy()
        sys.exit(0)


if __name__ == "__main__":
    main()
