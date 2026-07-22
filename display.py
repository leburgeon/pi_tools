""" Display management for the LCD. This module provides functions to initialise the LCD, stores the current state of the display, and handles the display of text and numbers. It serves as an interface between the application logic and the LCD hardware. """

from time import sleep

from LCD1602 import CharLCD1602


class DisplayManager:
    def __init__(self, line_length: int = 16, num_lines: int = 2):
        self.lcd = CharLCD1602()
        self.lcd.init_lcd(addr=None, bl=1)
        self.line_length = line_length
        self.num_lines = num_lines
        self.current_text = ""
        self.current_page = 0

    def clear_text_state(self):
        """ Clears the LCD display and resets the current text state. """
        self.lcd.clear()
        self.current_text = ""

    def new_text_state(self, text_to_display: str):
        """ Updates the current text to display and resets the page number. """
        self.current_text = text_to_display
        self.current_page = 0  # Reset to the first page whenever the text is updated

    def next_page(self):
        """ Advances to the next page of text, if available. """
        total_pages = (len(self.current_text) + self.line_length *
                       self.num_lines - 1) // (self.line_length * self.num_lines)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.display_current_page()

    def previous_page(self):
        """ Goes back to the previous page of text, if available. """
        if self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()

    def display_current_page(self):
        """ Displays the current page of text on the LCD. This distributes the text across the available lines and handles any necessary padding or truncation. """
        start_index = self.current_page * self.line_length * self.num_lines
        end_index = start_index + self.line_length * self.num_lines
        page_text = self.current_text[start_index:end_index]

        # Debug statement
        print(f"Displaying page {self.current_page + 1}: '{page_text}'")


if __name__ == "__main__":
    display_manager = DisplayManager()
    display_manager.new_text_state(
        "Hello, this is a test message to demonstrate the LCD display management. It should handle pagination correctly. This part of the text will be on the second page.")
    display_manager.display_current_page()

    print("Waiting for 2 seconds before moving to the next page...")
    sleep(2)  # Wait for 2 seconds before moving to the next page
    display_manager.next_page()

    print("Waiting for 2 seconds before moving back to the previous page...")
    sleep(2)  # Wait for 2 seconds before moving back to the previous page
    display_manager.previous_page()
