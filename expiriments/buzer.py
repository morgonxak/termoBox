import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)
p = GPIO.PWM(25, 1000)  # channel=12 frequency=50Hz
p.start(0)

while 1:
    for _ in range(80):
        p.ChangeDutyCycle(50)
        time.sleep(1)
        p.ChangeDutyCycle(0)
        time.sleep(0.5)

p.stop()