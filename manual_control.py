from threading import Event, Thread
import RPi.GPIO as GPIO
import time

CONTROLPIN = 37;


class ManualControl:
    def __init__(self, turn_lights_on, turn_lights_off, change_lighting_mode,
                 read_control_button_interval: float = 1 / 10.):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(CONTROLPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.__turn_lights_on = turn_lights_on
        self.__turn_lights_off = turn_lights_off
        self.__change_lighting_mode = change_lighting_mode

        self.__manual_control_thread = None
        self.__stop_manual_control_thread = Event()
        self.__read_control_button_interval = read_control_button_interval
        self.__start_manual_control_thread()
        self.__press_count = 0

    def __del__(self):
        self.__stop_control_thread()

    def __read_control_button(self):
        if GPIO.input(CONTROLPIN) == 0:
            self.__press_count += 1
        elif GPIO.input(CONTROLPIN) == 1:
            self.__read_control_button_interval(self.__press_count)
            self.__press_count = 0

    def __react_to_button_released(self, intervals_pressed):
        if intervals_pressed > 3:
            self.__change_animation_mode()
        else:
            self.__toggle_lighting_state()

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

        self.__manual_control_thread_method.set()
        self.__manual_control_thread.join()
