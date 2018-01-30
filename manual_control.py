from threading import Event, Thread
import RPi.GPIO as GPIO
import time

CONTROLPIN = 39;


class ManualControl:

    def __init__(self, turn_lights_on, turn_lights_off, change_lighting_mode,
                 read_control_button_interval: float = 1 / 10.):
        self.__manual_control_thread = None
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(CONTROLPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.__stop_manual_control_thread = Event()
        self.__read_control_button_interval = read_control_button_interval
        self.__turn_lights_on = turn_lights_on
        self.__turn_lights_off = turn_lights_off
        self.__change_lighting_mode = change_lighting_mode
        self.__start_manual_control_thread()

    def __del__(self):
        self.__stop_control_thread()

    def __read_control_button(self):
        print(GPIO.input(CONTROLPIN))

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
