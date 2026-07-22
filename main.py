""" The main REPL for the system. This file is responsible for initializing the LCD, handling user input, and calling the tools to perform the desired actions. It serves as the entry point for the application. """

from LCD1602 import CharLCD1602


def main():
    """
    The main function that initializes the LCD and starts the REPL loop.
    """
    lcd = CharLCD1602()
    lcd.init_lcd(addr=None, bl=1)

    try:
        while True:
            input_buffer = input("Enter command: ")
            lcd.write(0, 0, input_buffer)
    except KeyboardInterrupt:
        lcd.destroy()


if __name__ == "__main__":
    main()
