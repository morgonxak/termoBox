import smbus
import time

class LCD_I2C:
  # Define some device parameters
  I2C_ADDR  = 0x27 # I2C device address - установка адреса устройства
  LCD_WIDTH = 16   # Maximum characters per line - максимальное количество знаков в строке

  # Define some device constants - определим некоторые константы
  LCD_CHR = 1 # Mode - Sending data - отправка данных
  LCD_CMD = 0 # Mode - Sending command - отправка команды

  LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line - адрес в RAM дисплея для первой строки
  LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line - адрес в RAM дисплея для второй строки
  LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line - адрес в RAM дисплея для третье строки
  LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line - адрес в RAM дисплея для четвёртой строки

  LCD_BACKLIGHT  = 0x08  # On - подсветка включена
  #LCD_BACKLIGHT = 0x00  # Off - подсветка выключена

  ENABLE = 0b00000100 # Enable bit

  # Timing constants - временные константы
  E_PULSE = 0.0005
  E_DELAY = 0.0005

  #Open I2C interface - открытие интерфейса
  #bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
  bus = smbus.SMBus(1) # Rev 2 Pi uses 1

  def lcd_init(self):
    # Initialise display
    self.lcd_byte(0x33, self.LCD_CMD) # 110011 Initialise - инициализация
    self.lcd_byte(0x32, self.LCD_CMD) # 110010 Initialise - инициализация
    self.lcd_byte(0x06, self.LCD_CMD) # 000110 Cursor move direction - направление движения курсора
    self.lcd_byte(0x0C, self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off  - дисплей включён, курсор показывает, мигание курсора выключено
    self.lcd_byte(0x28, self.LCD_CMD) # 101000 Data length, number of lines, font size - длина данных, количество строк, размер шрифта
    self.lcd_byte(0x01, self.LCD_CMD) # 000001 Clear display - очистка дисплея
    time.sleep(self.E_DELAY)

  def lcd_byte(self, bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command

    bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
    bits_low = mode | ((bits<<4) & 0xF0) | self.LCD_BACKLIGHT

    # High bits
    self.bus.write_byte(self.I2C_ADDR, bits_high)
    self.lcd_toggle_enable(bits_high)

    # Low bits
    self.bus.write_byte(self.I2C_ADDR, bits_low)
    self.lcd_toggle_enable(bits_low)

  def lcd_toggle_enable(self, bits):
    # Toggle enable
    time.sleep(self.E_DELAY)
    self.bus.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
    time.sleep(self.E_PULSE)
    self.bus.write_byte(self.I2C_ADDR,(bits & ~self.ENABLE))
    time.sleep(self.E_DELAY)

  def lcd_string(self, message,line):
    # Send string to display

    message = message.ljust(self.LCD_WIDTH," ")

    self.lcd_byte(line, self.LCD_CMD)

    for i in range(self.LCD_WIDTH):
      self.lcd_byte(ord(message[i]),self.LCD_CHR)

  def main(self):
    # Main program block - главный блок программы

    # Initialise display  - инициализируем дисплей
    self.lcd_init()

    while True:

      # Send some test - отправим на дисплей тестовые строки
      self.lcd_string("Привет         <" ,self.LCD_LINE_1)
      self.lcd_string("Пака        <", self.LCD_LINE_2)

      time.sleep(3)

      # Send some more text - ещё текст
      self.lcd_string(">         термо",self.LCD_LINE_1)
      self.lcd_string(">        I2C LCD",self.LCD_LINE_2)

      time.sleep(3)

if __name__ == '__main__':

  try:
    test = LCD_I2C()
    test.main()
  except KeyboardInterrupt:
    pass
  finally:
    test.lcd_byte(0x01, test.LCD_CMD)