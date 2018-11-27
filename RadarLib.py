# Bibliotheken einbinden
import RPi.GPIO as GPIO
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
from io import BytesIO

class Radar:
    def __init__(self, motors):
        # GPIO Modus (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)

        # GPIO Pins zuweisen
        self.GPIO_TRIGGER = 20
        self.GPIO_ECHO = 21

        # Richtung der GPIO-Pins festlegen (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)

        self.motors = motors

    def distanz(self):
        # setze Trigger auf HIGH
        GPIO.output(self.GPIO_TRIGGER, True)

        # setze Trigger nach 0.01ms aus LOW
        time.sleep(0.00001)
        GPIO.output(self.GPIO_TRIGGER, False)

        StartZeit = time.time()
        StopZeit = time.time()

        # speichere Startzeit
        while GPIO.input(self.GPIO_ECHO) == 0:
            StartZeit = time.time()

        # speichere Ankunftszeit
        while GPIO.input(self.GPIO_ECHO) == 1:
            StopZeit = time.time()

        # Zeit Differenz zwischen Start und Ankunft
        TimeElapsed = StopZeit - StartZeit
        # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
        # und durch 2 teilen, da hin und zurueck
        distanz = (TimeElapsed * 34300) / 2

        return distanz

    def scan(self):
        contour=[[],[]]

        #Styling
        color = 'lime'
        plt.rcParams['text.color'] = color
        plt.rcParams['axes.labelcolor'] = color
        plt.rcParams['xtick.color'] = color
        plt.rcParams['ytick.color'] = color
        plt.rcParams['axes.edgecolor'] = 'gray'
        plt.rcParams['figure.figsize'] = 5, 5

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='polar')

        # 360deg are 404 steps at speed of 0.027
        for i in range(101):
            print("Radar-scanning... ")
            contour[0].append(math.radians(i*3.564356436))    #phi Phase
            contour[1].append(self.distanz())       #r Betrag

            #move
            for k in range(4):
                self.motors.step(1, -1)
                time.sleep(0.027)

        self.motors.off()
        contour[0].append(contour[0][0])
        contour[1].append(contour[1][0])
        ax.plot(contour[0], contour[1], color='lime', linewidth=3)

        #Styling
        ax.set_rmax(math.ceil(max(contour[1])/50.0)*50)
        ax.grid(True)
        ax.set_theta_zero_location("N")
        ax.set_title("Radarscan der Umgebung [cm]", va='bottom')
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')

        #Make Plot ready to send
        scan = BytesIO()
        fig.savefig(scan, format='png', facecolor='black')
        scan.seek(0)
        return scan, contour