""" Display management for the LCD. This module provides functions to initialise the LCD, stores the current state of the display, and handles the display of text and numbers. It serves as an interface between the application logic and the LCD hardware. 
The render() method must be called after any changes to the display state to reflect those changes on the LCD. """

from time import sleep
from datetime import datetime

from LCD1602 import CharLCD1602

PROCESSING = "Processing..."

TYPING = "Typing..."

DISPLAYING = "Displaying..."

IDLING = "Idling..."


class DisplayManager:
    def __init__(self, line_length: int = 16, num_lines: int = 2):
        # Initializes the LCD display.
        self.lcd = CharLCD1602()
        self.lcd.init_lcd(addr=None, bl=1)

        # Set the line length and number of lines for the LCD display. These values are used to manage text pagination and formatting.
        self.line_length = line_length
        self.num_lines = num_lines

        # Initialize the values for displaying and display lines. The current state is set to IDLING_STATE by default.
        self.display_text_state = ""
        self.current_display_page = 0
        self.total_display_pages = 0

        # Sets the current state of the display
        self.current_state = IDLING

    # GENERAL CONTROL

    def destroy(self):
        """ Cleans up the LCD display by clearing it and turning off the backlight. This method should be called when the application is exiting to ensure that the LCD is left in a clean state. """
        self.lcd.clear()
        self.lcd.closelight()

    def get_idle_datetime_line(self) -> str:
        """ Generates a datetime line for displaying on idle mode """
        date = datetime.now().strftime('%d/%m')
        time = datetime.now().strftime('%H:%M:%S')

        spaces_required = self.line_length - (len(date) + len(time))

        return date + (" " * spaces_required) + time

    def render(self):
        """ Renders the lines to the display based on the text to display and the current page """

        # If in idling mode, display idling display
        if self.current_state == IDLING:
            self.display_text_state = self.get_idle_datetime_line()

        # Gets the current page of text and formats the lines
        text_to_display = self._get_current_page_text()
        lines = self._format_page_text_to_lines(text_to_display)

        # Writes the lines to the LCD bus
        for i in range(self.num_lines):
            self.lcd.write(0, i, lines[i])

    def reset(self):
        """ Clears the LCD display and resets the current text state, page number, and total pages. """
        self.lcd.clear()
        self.display_text_state = self.get_idle_datetime_line()
        self.current_display_page = 0
        self.total_display_pages = 0
        self.current_state = IDLING

    #  DISPLAY

    def display_text(self, text_to_display: str):
        """ Sets the display mode to show the provided text. This method updates the current state to DISPLAYING_STATE, sets the text to be displayed, resets the current page to 0, and calculates the total number of pages based on the length of the text and the display capacity. """
        self.current_state = DISPLAYING
        self.current_display_page = 0
        self.display_text_state = text_to_display

        # Calculate the total number of pages based on the length of the text and the display capacity
        self.total_display_pages = (len(self.display_text_state) + self.line_length *
                                    self.num_lines - 1) // (self.line_length * self.num_lines)

    def next_page(self):
        """ Advances to the next page of text, if available. """
        if self.current_display_page < self.total_display_pages - 1:
            self.current_display_page += 1

    def previous_page(self):
        """ Goes back to the previous page of text, if available. """
        if self.current_display_page > 0:
            self.current_display_page -= 1

    def _get_current_page_text(self) -> str:
        """ Returns the text for the current page, given the current page number, number of lines, and the line length. """
        start_index = self.current_display_page * self.line_length * self.num_lines
        end_index = start_index + self.line_length * self.num_lines
        page_text = self.display_text_state[start_index:end_index]

        return page_text

    def _format_page_text_to_lines(self, page_text: str) -> list[str]:
        """ Formats the page text into lines suitable for the LCD display. 
        Returns a list of strings, each representing a line on the LCD. If the text is shorter than the line length, it pads with spaces. If it's longer, it truncates to fit the line length. """
        lines = []
        # For each available line on the LCD, slice the page text and pad it to the line length.
        for i in range(self.num_lines):
            line_start = i * self.line_length
            line_end = line_start + self.line_length
            line_text = page_text[line_start:line_end].ljust(self.line_length)
            lines.append(line_text)

        return lines

    # TYPING

    def update_typing(self, input_buffer: str):
        """ Updates the display to show the current input buffer while typing. This method sets the current state to TYPING, updates the display text state with the input buffer, and sets the current page so that the last character of the input buffer is visible. """
        self.current_state = TYPING
        self.display_text_state = input_buffer

        # Calculate the total number of pages based on the length of the input buffer and the display capacity
        self.total_display_pages = (len(self.display_text_state) + self.line_length *
                                    self.num_lines - 1) // (self.line_length * self.num_lines)

        # Set the current page to show the last part of the input buffer
        self.current_display_page = max(0, self.total_display_pages - 1)


if __name__ == "__main__":
    display_manager = DisplayManager()
    display_manager.display_text(
        "Hello, this is a test message to demonstrate the LCD display management. It should handle pagination correctly. This part of the text will be on the second page.")

    print(display_manager.get_idle_display())
