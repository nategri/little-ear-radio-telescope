import time
import numpy as np
import RPi.GPIO as GPIO
import datetime

HEARTBEAT_PIN = 18
DATA_PIN = 32

class VoltageData:
    def __init__(self):
        self._prev_time = time.time()
        GPIO.setup(DATA_PIN, GPIO.IN)
        self._state = GPIO.input(DATA_PIN)

        self._voltage = None

    def _update(self):
        curr_state = GPIO.input(DATA_PIN)

        if curr_state != self._state:
            curr_time = time.time()
            diff = curr_time - self._prev_time

            self._voltage = diff

            self._state = curr_state
            self._prev_time = curr_time

        return self._voltage

    def get_voltage(self):
        curr_voltage = self._voltage
        while True:
            time.sleep(0.001)
            output = self._update()
            if output != curr_voltage:
                break
        return output

class Heartbeat:
    def __init__(self):
        GPIO.setup(HEARTBEAT_PIN, GPIO.OUT)
        self._state = 0

    def tick(self):
        GPIO.output(HEARTBEAT_PIN, self._state)
        self._state = not self._state

if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)

    voltage_data = VoltageData()
    #heartbeat = Heartbeat()

    #heartbeat.tick()

    while True:
        voltage = voltage_data.get_voltage()
        #heartbeat.tick()
        print(voltage)

        with open('voltage.out', 'a') as f:
            f.write(datetime.datetime.utcnow().isoformat()+' '+str(voltage)+'\n')
