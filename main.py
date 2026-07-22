"""
The main REPL for the system. This file is responsible for initializing the LCD,
handling user input using curses, and calling the tools to perform the desired actions.
"""

import curses
from display import DisplayManager, IDLING, DISPLAYING, TYPING


def render_terminal_debug(stdscr: 'curses._CursesWindow', display_manager: DisplayManager, input_buffer: str) -> None:
    """Clears the terminal screen and displays current debug information."""
    stdscr.clear()
    stdscr.addstr(
        0, 0, f"Current State: {display_manager.current_state}, Input Buffer: '{input_buffer}'")
    stdscr.addstr(1, 0, "Press Escape or Ctrl+C to exit.")
    stdscr.refresh()


def process_keystroke(char_code: int, stdscr: 'curses._CursesWindow', display_manager: DisplayManager, input_buffer: str) -> tuple[str, bool]:
    """
    Processes a single keystroke and updates the display manager and input buffer accordingly.
    Returns a tuple containing the (updated_input_buffer, keep_running_flag).
    """
    # Handle Ctrl+C (3) or Escape (27) to Exit
    if char_code in (3, 27):
        stdscr.addstr(3, 0, "Exiting...")
        stdscr.refresh()
        return input_buffer, False

    # Handle Enter Key (10 is \n, 13 is \r)
    if char_code in (10, 13, curses.KEY_ENTER):
        if display_manager.current_state == TYPING and input_buffer.strip():
            stdscr.addstr(3, 0, f"Executing command: {input_buffer}")
            stdscr.refresh()
            curses.napms(500)  # Briefly pause to show the execution message

            result = "Yes, Tom is a massive wasteman!!"
            display_manager.display_text(result)
            return "", True  # Clear buffer on submission

        elif display_manager.current_state == DISPLAYING:
            stdscr.addstr(
                3, 0, "Exiting display mode and returning to typing mode.")
            stdscr.refresh()
            display_manager.reset()
            return input_buffer, True

    # Handle Left/Right Arrow Keys for Pagination
    if char_code == curses.KEY_LEFT and display_manager.current_state == DISPLAYING:
        display_manager.previous_page()
    elif char_code == curses.KEY_RIGHT and display_manager.current_state == DISPLAYING:
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

    return input_buffer, True


def main(stdscr: 'curses._CursesWindow') -> None:
    """The main function that initializes the LCD and starts the REPL loop."""
    # Setup curses environment
    curses.curs_set(0)     # Hide the blinking terminal cursor
    # Waits 50ms before running the loop to continue the render
    stdscr.timeout(50)

    display_manager = DisplayManager(line_length=16, num_lines=2)
    input_buffer = ""
    keep_running = True

    try:
        while keep_running:
            # 1. Render terminal UI
            render_terminal_debug(stdscr, display_manager, input_buffer)

            # 2. Get Input
            char_code = stdscr.getch()

            # 3. Handle Input
            if char_code != -1:
                input_buffer, keep_running = process_keystroke(
                    char_code, stdscr, display_manager, input_buffer
                )

            # 4. Render updates to the physical hardware LCD
            display_manager.render()

    except KeyboardInterrupt:
        # Failsafe in case Ctrl+C somehow slips past the char_code check
        pass
    finally:
        display_manager.destroy()


if __name__ == "__main__":
    # wrapper() handles setup and teardown of the terminal's raw mode automatically
    curses.wrapper(main)
