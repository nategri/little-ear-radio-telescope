import sys
import RPi.GPIO as GPIO

ENABLE = 37

if __name__ == "__main__":
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ENABLE, GPIO.OUT)

    if sys.argv[1] == 'on':
        GPIO.output(ENABLE, GPIO.HIGH)
    elif sys.argv[1] == 'off':
        GPIO.output(ENABLE, GPIO.LOW)
