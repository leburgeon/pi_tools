""" The main REPL for the system. This file is responsible for initializing the LCD, handling user input, and calling the tools to perform the desired actions. It serves as the entry point for the application. """

import sys

from LCD1602 import CharLCD1602
from input_handler import get_single_keypress
from display import DisplayManager, DISPLAYING, TYPING


def main():
    """
    The main function that initializes the LCD and starts the REPL loop.
    """
    display_manager = DisplayManager(line_length=16, num_lines=2)

    input_buffer = ""

    try:
        while True:
            # Gets the single keypress from the user without waiting for Enter.
            char = get_single_keypress()

            # Handle Ctrl+C or Escape to Exit
            if char in ('\x03', '\x1b'):
                print("Exiting...")
                break

            # Handle Enter Key (Execute Command)
            elif char in ('\r', '\n'):
                # Handles Enter Key when the display is in TYPING state and the input buffer is not empty
                if display_manager.current_state == TYPING and input_buffer.strip():
                    print(f"Executing command: {input_buffer}")
                    result = "A result of the command execution. This text is meant to demonstrate the display of command results."
                    display_manager.display_text(result)
                    input_buffer = ""

                elif display_manager.current_state == DISPLAYING:
                    print('Exiting display mode and returning to typing mode.')
                    display_manager.reset()

            # Handles left/right arrow keys for navigation (if needed)
            elif char in ('\x1b[D', '\x1b[C'):  # Left and Right Arrow Keys
                if display_manager.current_state == DISPLAYING:
                    if char == '\x1b[D':  # Left Arrow
                        display_manager.previous_page()
                    elif char == '\x1b[C':  # Right Arrow
                        display_manager.next_page()

            # Handle Backspace Key
            elif char in ('\x7f', '\x08'):
                if display_manager.current_state == TYPING and input_buffer:
                    input_buffer = input_buffer[:-1]
                    display_manager.update_input(input_buffer)

            elif display_manager.current_state == TYPING:
                input_buffer += char
                display_manager.update_typing(input_buffer)

            display_manager.render()

    except KeyboardInterrupt:
        display_manager.destroy()
        sys.exit(0)


if __name__ == "__main__":
    main()
