import threading
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

led1 = GPIO.PWM(5, 200)
led2 = GPIO.PWM(6, 200)
led3 = GPIO.PWM(13, 200)

def led_glow():
    t = threading.currentThread()
    led1.start(0)
    led2.start(100)
    led3.start(0)


    while getattr(t, "do_run", True):
        pause_time = 0.004
        for i in range(0, 101, + 1):
            sleep(pause_time)
            led1.ChangeDutyCycle(i)
            led2.ChangeDutyCycle(i)
            led3.ChangeDutyCycle(i)

        pause_time = 0.012
        for i in range(99, -1, -1):
            sleep(pause_time)
            led1.ChangeDutyCycle(i)
            led2.ChangeDutyCycle(i)
            led3.ChangeDutyCycle(i)