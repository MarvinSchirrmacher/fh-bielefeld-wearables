from functools import partial

from kivy.clock import Clock
from neopixel import *

RGB_MAX = 255
LED_COUNT = 30  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP = ws.WS2811_STRIP_GRB  # Strip type and colour ordering


class LedStripeController:
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
        self.__settings.bind(lighting_mode=self.set_mode)

        self.__mode_initializer = {
            'Manuell': self.set_mode_manual,
            'Automatik': self.set_mode_automatic,
            'Ausgeschaltet': self.set_mode_off
        }

        self.__animation = None
        self.__animation_interval = animation_interval
        self.__animation_position = 0

    def set_mode(self, instance, value):
        """
        Sets the lighting mode and start any action if needed.

        :param instance: The calling event instance.
        :param value: The new mode.
        :return:
        """
        if not self.__settings.lighting_mode == 'Manuell':
            Clock.unschedule(self.__animation)

        self.__mode_initializer[value]()
        self.__settings.lighting_mode = value

    def set_mode_off(self):
        """
        Switches all LEDs off.
        :return:
        """
        for i in range(self.__stripe.numPixels()):
            self.__stripe.setPixelColor(i, Color(0, 0, 0))
        self.__stripe.show()

    def set_mode_manual(self):
        """
        Schedules the configured lighting animation and enables the manual
        switching betwenn on and off.
        :return:
        """
        self.__animation = Clock.schedule_interval(
            partial(self.__rainbow_cycle, self), self.__animation_interval)

    def set_mode_automatic(self):
        """
        Calls method set_mode_manual until now.
        :return:
        """
        self.set_mode_off()

    def __rainbow_cycle(self, *largs):
        """
        Draw rainbow that uniformly distributes itself across all pixels.
        :param largs:
        :return:
        """
        number_of_pixels = self.__stripe.numPixels()
        self.__increment_animation_position()

        for i in range(self.__stripe.numPixels()):
            self.__stripe.setPixelColor(i, self.__wheel(
                (int(i * (RGB_MAX + 1) / number_of_pixels) +
                 self.__animation_position) & RGB_MAX))
        self.__stripe.show()

    def __increment_animation_position(self):
        """
        Increments the animation position and resets it if RGB_MAX is reached.
        :return:
        """
        self.__animation_position += 1
        if self.__animation_position == RGB_MAX + 1:
            self.__animation_position = 0

    def __wheel(self, pos):
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
