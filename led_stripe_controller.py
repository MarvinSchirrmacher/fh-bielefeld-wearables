import sys
import time
from threading import Thread, Event

if sys.platform.startswith('linux'):
    from neopixel import ws, Adafruit_NeoPixel, Color
else:
    from mock.neopixel_mock import ws, Adafruit_NeoPixel, Color

RGB_MAX = 255
BRIGHTNESS_MAX = 255
COLOR_WHITE = Color(RGB_MAX, RGB_MAX, RGB_MAX)
COLOR_WHITE_0_5 = Color(127, 127, 127)
COLOR_BLACK = Color(0, 0, 0)

LED_COUNT = 30  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = int(BRIGHTNESS_MAX * 1)  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP = ws.WS2811_STRIP_GRB  # Strip type and colour ordering


class LedStripeController:
    LIGHTING_AREA = {
        'rearTop': [22, 23, 24, 25, 26, 27, 28, 29],
        'rearBottom': [4, 5, 6, 7, 8, 9],
        'rearLeft': [10, 11, 12, 13],
        'rearRight': [0, 1, 2, 3],
        'frontLeft': [14, 15, 16, 17],
        'frontRight': [18, 19, 20, 21]
    }

    def __init__(self, settings, animation_interval: float = 1 / 50.):
        """
        Initializes the led stripe and sets the modes and animations.
        :param settings: The settings which handles the lighting mode.
        :param animation_interval: The time in seconds in which to update an animation.
        """
        self.__stripe = Adafruit_NeoPixel(
            LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
            LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
        self.__stripe.begin()

        self.__settings = settings
        self.__settings.bind(
            lighting_mode=self.set_mode,
            animation_type=self.set_animation)

        self.__mode_initializer = {
            'manual': self.set_mode_manual,
            'automatic': self.set_mode_automatic,
            'off': self.set_mode_off
        }
        self.__animation_methods = {
            'constant': self.__constant,
            'rainbow': self.__rainbow,
            'cycle': self.__rainbow_cycle,
            'wipe': self.__color_wipe,
            'chase': self.__theater_chase
        }

        self.__animation_thread = None
        self.__stop_animation_thread = Event()
        self.__animation_interval = animation_interval
        self.__pixel_iteration = 0
        self.__color_iteration = 0
        self.__animation_toggle = 0
        self.__animation_method = self.__animation_methods[self.__settings.animation_type]

    def __del__(self):
        self.stop_animation()

    def set_mode(self, instance, mode):
        """
        Sets the lighting mode and starts any action if needed.

        :param instance: The calling event instance.
        :param mode: The new mode.
        :return:
        """
        assert(instance == self.__settings)

        self.stop_animation()
        self.__mode_initializer[mode]()

    def set_mode_off(self):
        """
        Switches off all LEDs.
        :return:
        """
        for i in range(self.__stripe.numPixels()):
            self.__stripe.setPixelColor(i, COLOR_BLACK)
        self.__stripe.show()

    def set_mode_manual(self):
        """
        Schedules the configured lighting animation and enables the manual
        switching between on and off.
        :return:
        """
        self.start_animation()

    def set_mode_automatic(self):
        """
        Calls method set_mode_manual until now.
        :return:
        """
        self.set_mode_off()

    def set_animation(self, instance, animation_type):
        """
        Sets the animation method corresponding to the animation type.
        :param instance: The calling event instance.
        :param animation_type: The name of the animation type to use.
        :return:
        """
        assert(instance == self.__settings)

        self.__animation_method = self.__animation_methods[animation_type]

    def start_animation(self):
        """
        Starts the animation thread which cyclically calls the method to update
        the currently selected animation.
        :return:
        """
        if self.__animation_thread is not None \
                and not self.__animation_thread.is_alive:
            return
        self.__animation_thread = Thread(
            target=self.__animation_thread_method, daemon=True)
        self.__animation_thread.start()

    def stop_animation(self):
        """
        Stops the animation thread if it is alive.
        :return:
        """
        if self.__animation_thread is None:
            return
        if not self.__animation_thread.is_alive:
            return

        self.__stop_animation_thread.set()
        self.__animation_thread.join()

    def __animation_thread_method(self):
        """
        The thread method which cyclically calls the animation update method.
        :return:
        """
        while True:
            if self.__stop_animation_thread.is_set():
                self.set_mode_off()
                return
            self.__update_animation()
            time.sleep(self.__animation_interval)

    def __update_animation(self):
        """
        Increments the animation properties, updates the pixel configuration
        and updates the LEDs.
        :return:
        """
        self.__increment_animation_iteration()
        if self.__animation_method():
            self.__stripe.show()

    def __constant(self):
        """
        Sets each pixel to white.
        :return:
        """
        if self.__stripe.getPixelColor(self.__pixel_iteration) == COLOR_WHITE_0_5:
            return False
        self.__stripe.setPixelColor(self.__pixel_iteration, COLOR_WHITE_0_5)
        return True

    def __color_wipe(self):
        """
        Wipe color across display a pixel at a time.
        :return:
        """
        prior_pixel = self.__pixel_iteration - 1 if self.__pixel_iteration > 0 else self.__stripe.numPixels() - 1
        self.__stripe.setPixelColor(prior_pixel, COLOR_BLACK)
        self.__stripe.setPixelColor(self.__pixel_iteration, COLOR_WHITE)
        return True

    def __rainbow(self):
        """
        Draw rainbow that fades across all pixels at once.
        :return:
        """
        for i in range(self.__stripe.numPixels()):
            self.__stripe.setPixelColor(i, self.__wheel(
                (self.__pixel_iteration + self.__color_iteration) & 255))
        return True

    def __rainbow_cycle(self):
        """
        Draw rainbow that uniformly distributes itself across all pixels.
        :return:
        """
        for i in range(self.__stripe.numPixels()):
            self.__stripe.setPixelColor(i, self.__wheel(
                (int(i * 256 / self.__stripe.numPixels()) + self.__color_iteration) & 255))
        return True

    def __theater_chase(self):
        """
        Movie theater light style chaser animation.
        :return:
        """
        return False
    #     for i in range(0, self.__stripe.numPixels(), 3):
    #         self.__stripe.setPixelColor(i + self.__animation_toggle, COLOR_WHITE)
    #     strip.show()
    #     time.sleep(wait_ms / 1000.0)
    #     for i in range(0, self.__stripe.numPixels(), 3):
    #         self.__stripe.setPixelColor(i + self.__animation_toggle, COLOR_BLACK)

    def __theater_chase_rainbow(self):
        """
        Rainbow movie theater light style chaser animation.
        :return:
        """
        return False
    #     for j in range(256):
    #         for q in range(3):
    #             for i in range(0, strip.numPixels(), 3):
    #                 strip.setPixelColor(i + q, wheel((i + j) % 255))
    #             strip.show()
    #             time.sleep(wait_ms / 1000.0)
    #             for i in range(0, strip.numPixels(), 3):
    #                 strip.setPixelColor(i + q, 0)

    def __increment_animation_iteration(self):
        """
        Increments the animation properties and resets them if their maximum
        values are reached.
        :return:
        """
        self.__color_iteration += 1
        if self.__color_iteration == RGB_MAX + 1:
            self.__color_iteration = 0

        self.__pixel_iteration += 1
        if self.__pixel_iteration == self.__stripe.numPixels():
            self.__pixel_iteration = 0

        self.__animation_toggle += 1
        if self.__animation_toggle == 3:
            self.__animation_toggle = 0

    @staticmethod
    def __wheel(pos):
        """
        Generate rainbow colors across 0-255 positions.
        :param pos: The current animation position.
        :return:
        """
        if pos < 85:
            return Color(pos * 3, RGB_MAX - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(RGB_MAX - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, RGB_MAX - pos * 3)
