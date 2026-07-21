#!/usr/bin/env python3
import time
import smbus
import subprocess
from typing import Optional, List

class CharLCD1602(object):
    """
    A class to control a 16x2 Character LCD via an I2C adapter (PCF8574 or PCF8574A).
    Handles the low-level 4-bit interface communication over I2C.
    """
    def __init__(self) -> None:
        """
        Initializes the CharLCD1602 object.
        
        Sets up the SMBus (I2C bus) interface, defaults the backlight to ON, 
        and defines the standard I2C addresses for the PCF8574 (0x27) and 
        PCF8574A (0x3f) expander chips commonly used on these displays.
        """
        # Note you need to change the bus number to 0 if running on a revision 1 Raspberry Pi.
        self.bus = smbus.SMBus(1)
        self.BLEN = 1  # turn on/off background light
        self.PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
        self.PCF8574A_address = 0x3f  # I2C address of the PCF8574A chip.
        self.LCD_ADDR = self.PCF8574_address  

    def _write_word(self, addr: int, data: int) -> None:
        """
        [INTERNAL] Writes a single byte of data to the specified I2C address.
        
        This function ensures that the backlight state (Bit 3 / 0x08) is preserved 
        or disabled based on the current configuration in self.BLEN.
        
        Args:
            addr (int): The I2C address of the LCD.
            data (int): The 8-bit data to send to the I2C expander.
        """
        temp = data
        if self.BLEN == 1:
            temp |= 0x08  # Preserve the backlight ON bit
        else:
            temp &= 0xF7  # Mask out the backlight bit (turn OFF)
        self.bus.write_byte(addr, temp)

    def _send_command(self, comm: int) -> None:
        """
        [INTERNAL] Sends an instruction command to the LCD controller.
        
        Because the I2C expander uses a 4-bit interface to the LCD, the 8-bit command 
        must be split into two 4-bit nibbles (high and low). The function sets RS = 0 
        to indicate a command, and toggles the Enable (EN) pin to latch the data.
        
        Args:
            comm (int): The 8-bit command to send.
        """
        # Send bit7-4 firstly (High Nibble)
        buf = comm & 0xF0
        buf |= 0x04               # RS = 0, RW = 0, EN = 1
        self._write_word(self.LCD_ADDR, buf)
        time.sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self._write_word(self.LCD_ADDR, buf)
        
        # Send bit3-0 secondly (Low Nibble)
        buf = (comm & 0x0F) << 4
        buf |= 0x04               # RS = 0, RW = 0, EN = 1
        self._write_word(self.LCD_ADDR, buf)
        time.sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self._write_word(self.LCD_ADDR, buf)

    def _send_data(self, data: int) -> None:
        """
        [INTERNAL] Sends a single character (data) to be displayed on the LCD.
        
        Similar to _send_command, this splits the 8-bit data into two 4-bit nibbles.
        However, it sets RS = 1 to indicate to the LCD controller that this is 
        character data to be printed, rather than an instruction.
        
        Args:
            data (int): The 8-bit ASCII value of the character to display.
        """
        # Send bit7-4 firstly (High Nibble)
        buf = data & 0xF0
        buf |= 0x05               # RS = 1, RW = 0, EN = 1
        self._write_word(self.LCD_ADDR, buf)
        time.sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self._write_word(self.LCD_ADDR, buf)
        
        # Send bit3-0 secondly (Low Nibble)
        buf = (data & 0x0F) << 4
        buf |= 0x05               # RS = 1, RW = 0, EN = 1
        self._write_word(self.LCD_ADDR, buf)
        time.sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self._write_word(self.LCD_ADDR, buf)

    def _i2c_scan(self) -> List[str]:
        """
        [INTERNAL] Scans the I2C bus (bus 1) for connected devices using system shell commands.
        
        Returns:
            List[str]: A list of strings containing the hex addresses of found I2C devices.
        """
        cmd = "i2cdetect -y 1 |awk 'NR>1 {$1=\"\";print}'"
        result = subprocess.check_output(cmd, shell=True).decode()
        result = result.replace("\n", "").replace(" --", "")
        i2c_list = result.split(' ')
        return i2c_list

    def init_lcd(self, addr: Optional[int] = None, bl: int = 1) -> bool:
        """
        [PUBLIC] Initializes the LCD hardware and prepares it for displaying data.
        
        This method will scan the I2C bus to automatically find the LCD address if 
        none is provided. It then runs the specific HD44780 initialization sequence.
        
        Args:
            addr (Optional[int]): A specific I2C address to use. Defaults to None (auto-detect).
            bl (int): Backlight state (1 for ON, 0 for OFF). Defaults to 1.
            
        Returns:
            bool: True if initialization was successful, False if an error occurred.
        """
        i2c_list = self._i2c_scan()
        if addr is None:
            if '27' in i2c_list:
                self.LCD_ADDR = self.PCF8574_address
            elif '3f' in i2c_list:
                self.LCD_ADDR = self.PCF8574A_address
            else:
                raise IOError("I2C address 0x27 or 0x3f not found.")
        else:
            self.LCD_ADDR = addr
            if str(hex(addr)).strip('0x') not in i2c_list:
                raise IOError(f"I2C address {str(hex(addr))} or 0x3f not found.")    
        
        self.BLEN = bl
        try:
            self._send_command(0x33) # Must initialize to 8-line mode at first
            time.sleep(0.005)
            self._send_command(0x32) # Then initialize to 4-line mode
            time.sleep(0.005)
            self._send_command(0x28) # 2 Lines & 5*7 dots
            time.sleep(0.005)
            self._send_command(0x0C) # Enable display without cursor
            time.sleep(0.005)
            self._send_command(0x01) # Clear Screen
            self.bus.write_byte(self.LCD_ADDR, 0x08)
        except:
            return False
        else:
            return True

    def clear(self) -> None:
        """
        [PUBLIC] Clears the entire LCD screen and returns the cursor to the home position.
        """
        self._send_command(0x01) # Clear Screen

    def openlight(self) -> None:
        """
        [PUBLIC] Hardcodes a command to manually turn on the backlight via I2C address 0x27,
        and then closes the SMBus connection.
        """
        self.bus.write_byte(0x27, 0x08)
        self.bus.close()

    def write(self, x: int, y: int, text: str) -> None:
        """
        [PUBLIC] Writes a text string to the LCD starting at a specific x, y coordinate.
        
        Args:
            x (int): The column position (0 to 15). Automatically constrained to bounds.
            y (int): The row position (0 to 1). Automatically constrained to bounds.
            text (str): The string of text to display.
        """
        if x < 0:
            x = 0
        if x > 15:
            x = 15
        if y < 0:
            y = 0
        if y > 1:
            y = 1
            
        # Move cursor: 0x80 is the base command for setting DDRAM address.
        addr = 0x80 + 0x40 * y + x
        self._send_command(addr)
        
        for chr in text:
            self._send_data(ord(chr))

    def display_num(self, x: int, y: int, num: int) -> None:
        """
        [PUBLIC] Writes a single ASCII character/number at a specific x, y coordinate.
        
        Args:
            x (int): The column position.
            y (int): The row position.
            num (int): The ASCII integer value of the character to display.
        """
        addr = 0x80 + 0x40 * y + x
        self._send_command(addr)
        self._send_data(num)
        
def loop() -> None:
    """
    The main execution loop for the script.
    Continually clears the screen, displays 'Hello World!' on the first line, 
    and updates a running counter on the second line every second.
    """
    count = 0
    while(True):
        lcd1602.clear()
        lcd1602.write(0, 0, '  Hello World!  ')
        lcd1602.write(0, 1, '  Counter: ' + str(count))
        time.sleep(1)
        count += 1

def destroy() -> None:
    """
    Cleans up the LCD by clearing the display when the program is interrupted or stopped.
    """
    lcd1602.clear()

lcd1602 = CharLCD1602()  

if __name__ == '__main__':
    print('Program is starting ... ')
    lcd1602.init_lcd(addr=None, bl=1)
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
