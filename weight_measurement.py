from threading import Event, Thread

import time

from UUGear import *

ARDUINO_ID = 'UUGear-Arduino-4713-9982'


class WeightMeasurement:
    def __init__(self, measurement_interval: float = 1 / 50.):
        self.__attach_arduino()
        if not self.__arduino.isValid():
            return

        self.__measure_thread = None
        self.__stop_measurement_thread = Event()
        self.__measurement_interval = measurement_interval
        self.__start_measure_thread()

    def __del__(self):
        self.__stop_measurement()
        self.__detach_arduino()

    def __attach_arduino(self):
        UUGearDevice.setShowLogs(0)
        self.__arduino = UUGearDevice(ARDUINO_ID)

    def __detach_arduino(self):
        if not self.__arduino.isValid():
            return

        self.__arduino.detach()
        self.__arduino.stopDeamon()

    def __measure(self):
        print("Sensor1: %0.2f" % (float(self.__arduino.analogRead(2)) * 5 / 1024), "V")
        print("Sensor2: %0.2f" % (float(self.__arduino.analogRead(3)) * 5 / 1024), "V")

    def __measure_thread_method(self):
        while True:
            if self.__stop_measurement_thread.is_set():
                return
            self.__measure()
            time.sleep(self.__measurement_interval)

    def __start_measure_thread(self):
        if self.__measure_thread is not None \
                and not self.__measure_thread.is_alive:
            return
        if self.__arduino is None or not self.__arduino.isValid():
            return
        self.__measure_thread = Thread(
            target=self.__measure_thread_method, daemon=True)
        self.__measure_thread.start()

    def __stop_measurement(self):
        if self.__measure_thread is None:
            return
        if not self.__measure_thread.is_alive:
            return

        self.__stop_measurement_thread.set()
        self.__measure_thread.join()
