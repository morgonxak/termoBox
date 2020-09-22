import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)

p = GPIO.PWM(25, 1000)  # channel=12 frequency=50Hz
p.start(0)
p.ChangeDutyCycle(1)
time.sleep(0.3)
p.stop()