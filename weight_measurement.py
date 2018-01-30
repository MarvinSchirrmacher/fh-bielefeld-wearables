from threading import Event, Thread

import time

from UUGear import *

ARDUINO_ID = 'UUGear-Arduino-4713-9982'


class WeightMeasurement:
    def __init__(self, on_schoolbag_put_on, on_schoolbag_put_down, settings, measurement_interval: float = 1 / 10.):
        self.__attach_arduino()
        if not self.__arduino.isValid():
            print('[WeightMeasurement] Arduino initialization failed')
            return

        self.__measure_thread = None
        self.__stop_measurement_thread = Event()
        self.__measurement_interval = measurement_interval
        self.__start_measure_thread()
        self.__on_schoolbag_put_on = on_schoolbag_put_on
        self.__on_schoolbag_put_down = on_schoolbag_put_down
        self.__is_put_on = None

    def __del__(self):
        self.__stop_measurement()
        self.__detach_arduino()

    def __attach_arduino(self):
        UUGearDevice.setShowLogs(0)
        self.__arduino = UUGearDevice(ARDUINO_ID)

    def __detach_arduino(self):
        if not self.__arduino.isValid():
            self.__arduino.detach()
            self.__arduino.stopDeamon()
            print('[weight_measurement] Device is valid: detach')
            return
        print('[weight_measurement] Device is invalid: detach')
        self.__arduino.detach()
        self.__arduino.stopDeamon()

    def __measure(self):
        # sensor_left = self.__arduino.analogRead(2)
        # sensor_right = self.__arduino.analogRead(3)
        # print('%4d - %4d - %4d' % (sensor_left, sensor_right, (sensor_left+sensor_right)/2))

        if self.__arduino.analogRead(2) > 100 and self.__arduino.analogRead(3) > 100 and (
                self.__is_put_on is None or self.__is_put_on is False):
            self.__on_schoolbag_put_on()
            self.__is_put_on = True
            print('put on')
        elif self.__arduino.analogRead(2) <= 100 and self.__arduino.analogRead(3) <= 100 and (
                self.__is_put_on is None or self.__is_put_on is True):
            self.__on_schoolbag_put_down()
            self.__is_put_on = False
            print('put down')

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
