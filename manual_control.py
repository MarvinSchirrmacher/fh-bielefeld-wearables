from threading import Event, Thread
import time

import sys

if sys.platform.startswith('linux'):
    import RPi.GPIO as GPIO
else:
    from mock.rpi_mock import GPIO

CONTROL_PIN = 37
BUTTON_PRESSED = 0
BUTTON_LONG_PRESSED = 6


class ManualControl:
    def __init__(self, toggle_lighting_state, set_next_animation_type,
                 read_control_button_interval: float = 1 / 10.):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(CONTROL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.__toggle_lighting_state = toggle_lighting_state
        self.__set_next_animation_type = set_next_animation_type

        self.__manual_control_thread = None
        self.__stop_manual_control_thread = Event()
        self.__read_control_button_interval = read_control_button_interval
        self.__was_pressed = False
        self.__press_count = 0
        self.__start_manual_control_thread()

    def __del__(self):
        self.__stop_control_thread()

    def __read_control_button(self):
        is_now_pressed = BUTTON_PRESSED == GPIO.input(CONTROL_PIN)
        released = self.__was_pressed and not is_now_pressed

        if is_now_pressed:
            self.__press_count += 1
            if self.__press_count == BUTTON_LONG_PRESSED:
                self.__on_button_was_pressed(True)
        elif released:
            if self.__press_count < BUTTON_LONG_PRESSED:
                self.__on_button_was_pressed(False)
            self.__press_count = 0

        self.__was_pressed = is_now_pressed

    def __on_button_was_pressed(self, was_long_pressed):
        if was_long_pressed:
            self.__toggle_lighting_state()
        else:
            self.__set_next_animation_type()

    def __manual_control_thread_method(self):
        while True:
            if self.__stop_manual_control_thread.is_set():
                return
            self.__read_control_button()
            time.sleep(self.__read_control_button_interval)

    def __start_manual_control_thread(self):
        if self.__manual_control_thread is not None \
                and not self.__manual_control_thread.is_alive:
            return
        self.__manual_control_thread = Thread(
            target=self.__manual_control_thread_method, daemon=True)
        self.__manual_control_thread.start()

    def __stop_control_thread(self):
        if self.__manual_control_thread is None:
            return
        if not self.__manual_control_thread.is_alive:
            return

        self.__stop_manual_control_thread.set()
        self.__manual_control_thread.join()
