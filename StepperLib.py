import RPi.GPIO as GPIO

class StepperMotor:

    def __init__(self):
        self.__PinsLeft = [10, 22, 27, 17]
        self.__PinsRight = [18, 23, 24, 25]
        self.__Sequences = [[1, 0, 1, 0], [1, 0, 0, 1], [0, 1, 0, 1], [0, 1, 1, 0]]
        self.__SeqStateLeft = 0
        self.__SeqStateRight= 0
        #self.__WaitTime = 0.002

        ## Inialize pins:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False) 
        for i in (self.__PinsLeft + self.__PinsRight):
            GPIO.setup(i, GPIO.OUT)
            GPIO.output(i, GPIO.LOW)

    def __del__(self):
        """Object destructor: GPIO cleaning on exit."""
        GPIO.cleanup()

    def step(self, LeftDirection, RightDirection):
        """Do a simple step, and update the state for the next one."""
        self.__SeqStateLeft = (self.__SeqStateLeft + LeftDirection) % 4
        self.__SeqStateRight = (self.__SeqStateRight + RightDirection) % 4
        for i in range(0,4):
            GPIO.output(self.__PinsLeft[i], self.__Sequences[self.__SeqStateLeft][i])
            GPIO.output(self.__PinsRight[i], self.__Sequences[self.__SeqStateRight][i])
        #sleep(self.__WaitTime)

    def off(self):
        for i in (self.__PinsLeft + self.__PinsRight):
            GPIO.output(i, GPIO.LOW)
        
