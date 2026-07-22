"""
The main REPL for the system. This file is responsible for initializing the LCD,
handling user input using curses, and calling the tools to perform the desired actions.
"""


import curses
from display import DisplayManager, IDLING, DISPLAYING, TYPING


def main(stdscr):
    """
    The main function that initializes the LCD and starts the REPL loop.
    """
    # Setup curses environment
    curses.curs_set(0)     # Hide the blinking terminal cursor
    stdscr.nodelay(False)  # Block and wait for user input

    display_manager = DisplayManager(line_length=16, num_lines=2)
    input_buffer = ""

    try:
        while True:
            # Clear the terminal screen and display debug info
            stdscr.clear()
            stdscr.addstr(
                0, 0, f"Current State: {display_manager.current_state}, Input Buffer: '{input_buffer}'")
            stdscr.addstr(1, 0, "Press Escape or Ctrl+C to exit.")
            stdscr.refresh()

            # getch() safely waits for a key and handles escape sequences for you
            char_code = stdscr.getch()

            # Handle Ctrl+C (3) or Escape (27) to Exit
            if char_code in (3, 27):
                stdscr.addstr(3, 0, "Exiting...")
                stdscr.refresh()
                break

            # Handle Enter Key (10 is \n, 13 is \r)
            elif char_code in (10, 13, curses.KEY_ENTER):
                if display_manager.current_state == TYPING and input_buffer.strip():
                    stdscr.addstr(3, 0, f"Executing command: {input_buffer}")
                    stdscr.refresh()
                    # Briefly pause to show the execution message on terminal
                    curses.napms(500)

                    result = "A result of the command execution. This text is meant to demonstrate the display of command results."
                    display_manager.display_text(result)
                    input_buffer = ""

                elif display_manager.current_state == DISPLAYING:
                    stdscr.addstr(
                        3, 0, "Exiting display mode and returning to typing mode.")
                    stdscr.refresh()
                    display_manager.reset()

            # Handles Left/Right Arrow Keys
            elif char_code == curses.KEY_LEFT:
                if display_manager.current_state == DISPLAYING:
                    display_manager.previous_page()

            elif char_code == curses.KEY_RIGHT:
                if display_manager.current_state == DISPLAYING:
                    display_manager.next_page()

            # Handle Backspace Key (127 is DEL, 8 is Backspace)
            elif char_code in (8, 127, curses.KEY_BACKSPACE):
                if display_manager.current_state == TYPING and input_buffer:
                    input_buffer = input_buffer[:-1]
                    display_manager.update_typing(input_buffer)

            # Handle Standard Typing (Printable ASCII range 32 to 126)
            elif 32 <= char_code <= 126:
                if display_manager.current_state in (TYPING, IDLING):
                    input_buffer += chr(char_code)
                    display_manager.update_typing(input_buffer)

            # Render updates to the physical hardware LCD
            display_manager.render()

    except KeyboardInterrupt:
        # Failsafe in case Ctrl+C somehow slips past the char_code check
        pass

    finally:
        display_manager.destroy()


if __name__ == "__main__":
    # wrapper() handles setup and teardown of the terminal's raw mode automatically
    curses.wrapper(main)
