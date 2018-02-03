from threading import Event, Thread

import time

import sys

if sys.platform.startswith('linux'):
    from UUGear import *
else:
    from mock.uugear_mock import *

ARDUINO_ID = 'UUGear-Arduino-4713-9982'


class WeightMeasurement:
    LEFT_SENSOR = 2
    RIGHT_SENSOR = 3

    def __init__(self, settings, on_schoolbag_put_on, on_schoolbag_put_down, measurement_interval: float = 1 / 10.):
        self.__attach_arduino()
        if not self.__arduino.isValid():
            print('[WeightMeasurement] Arduino initialization failed')
            return

        self.__settings = settings
        self.__measure_thread = None
        self.__stop_measurement_thread = Event()
        self.__measurement_interval = measurement_interval
        self.__on_schoolbag_put_on = on_schoolbag_put_on
        self.__on_schoolbag_put_down = on_schoolbag_put_down
        self.__is_put_on = False
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
        self.__arduino.stopDaemon()

    def __measure(self):
        self.__measure_sensor_values()

        if self.__compare_sensor_values(lambda v: v > 100) and not self.__is_put_on:
            self.__on_schoolbag_put_on()
            self.__is_put_on = True
        elif self.__compare_sensor_values(lambda v: v <= 100) and self.__is_put_on:
            self.__on_schoolbag_put_down()
            self.__is_put_on = False

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

    def __measure_sensor_values(self):
        self.__left_value = self.__arduino.analogRead(self.LEFT_SENSOR)
        self.__right_value = self.__arduino.analogRead(self.RIGHT_SENSOR)

    def __compare_sensor_values(self, compare):
        return compare(self.__left_value) and compare(self.__right_value)
