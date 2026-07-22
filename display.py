"""
Display management for the LCD. This module provides functions to initialise the LCD, stores the
current state of the display, and handles the display of text and numbers. It serves as an
interface between the application logic and the LCD hardware.

The render() method must be called after any changes to the display state to reflect those
changes on the LCD.
"""

from time import sleep
from datetime import datetime

from LCD1602 import CharLCD1602

PROCESSING = "Processing..."
TYPING = "Typing..."
DISPLAYING = "Displaying..."
IDLING = "Idling..."


class DisplayManager:
    def __init__(self, line_length: int = 16, num_lines: int = 2) -> None:
        """Initializes the LCD display and state variables."""
        self.lcd = CharLCD1602()
        self.lcd.init_lcd(addr=None, bl=1)

        # Set the line length and number of lines for managing pagination and formatting.
        self.line_length = line_length
        self.num_lines = num_lines

        self.display_text_state = ""
        self.current_display_page = 0
        self.total_display_pages = 0

        self.current_state = IDLING

    # GENERAL CONTROL

    def destroy(self) -> None:
        """Cleans up the LCD display by clearing it and turning off the backlight."""
        self.lcd.clear()
        self.lcd.closelight()

    def get_idle_datetime_line(self) -> str:
        """Generates a formatted datetime string for idle mode."""
        now = datetime.now()
        date_str = now.strftime('%d/%m')
        time_str = now.strftime('%H:%M:%S')

        spaces_required = self.line_length - (len(date_str) + len(time_str))
        return date_str + (" " * spaces_required) + time_str

    def _calculate_total_pages(self, text: str) -> int:
        """Calculates the total number of pages required to display the given text."""
        capacity = self.line_length * self.num_lines
        return (len(text) + capacity - 1) // capacity

    def render(self) -> None:
        """Renders the lines to the display based on the text to display and the current page."""
        if self.current_state == IDLING:
            self.display_text_state = self.get_idle_datetime_line()

        text_to_display = self._get_current_page_text()
        lines = self._format_page_text_to_lines(text_to_display)

        for i in range(self.num_lines):
            self.lcd.write(0, i, lines[i])

    def reset(self) -> None:
        """Clears the LCD display and resets the current text state, page number, and total pages."""
        self.lcd.clear()
        self.display_text_state = self.get_idle_datetime_line()
        self.current_display_page = 0
        self.total_display_pages = 0
        self.current_state = IDLING

    # DISPLAY

    def display_text(self, text_to_display: str) -> None:
        """Sets the display mode to show the provided text and calculates pagination."""
        self.current_state = DISPLAYING
        self.current_display_page = 0
        self.display_text_state = text_to_display
        self.total_display_pages = self._calculate_total_pages(
            self.display_text_state)

    def next_page(self) -> None:
        """Advances to the next page of text, if available."""
        if self.current_display_page < self.total_display_pages - 1:
            self.current_display_page += 1

    def previous_page(self) -> None:
        """Goes back to the previous page of text, if available."""
        if self.current_display_page > 0:
            self.current_display_page -= 1

    def _get_current_page_text(self) -> str:
        """Returns the text for the current page based on pagination parameters."""
        start_index = self.current_display_page * self.line_length * self.num_lines
        end_index = start_index + self.line_length * self.num_lines
        return self.display_text_state[start_index:end_index]

    def _format_page_text_to_lines(self, page_text: str) -> list[str]:
        """
        Formats the page text into lines suitable for the LCD display.
        Returns a list of strings padded or truncated to the line length.
        """
        lines = []
        for i in range(self.num_lines):
            line_start = i * self.line_length
            line_end = line_start + self.line_length
            line_text = page_text[line_start:line_end].ljust(self.line_length)
            lines.append(line_text)
        return lines

    # TYPING

    def update_typing(self, input_buffer: str) -> None:
        """Updates the display to show the current input buffer while typing."""
        self.current_state = TYPING
        self.display_text_state = input_buffer
        self.total_display_pages = self._calculate_total_pages(
            self.display_text_state)
        self.current_display_page = max(0, self.total_display_pages - 1)


if __name__ == "__main__":
    display_manager = DisplayManager()
    display_manager.display_text(
        "Hello, this is a test message to demonstrate the LCD display management. "
        "It should handle pagination correctly. This part of the text will be on the second page."
    )
    print(display_manager.get_idle_datetime_line())
