import time
import busio
import board
import adafruit_amg88xx

i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)

def processing(temp):
    if temp <= 32.5:
        temp = temp + 4.3 + abs(32.5 - temp) / 1.23076923
    else:
        temp = temp + 4.3

    return temp

while True:
    for row in amg.pixels:
        for temp in row:
            print(["{0:.1f}".format(processing(temp)) for temp in row])
    print("\n")
    time.sleep(1)
