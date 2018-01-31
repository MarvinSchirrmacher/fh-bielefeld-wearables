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
COLOR_RED = Color(RGB_MAX, 0, 0)

LED_COUNT = 30  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = int(BRIGHTNESS_MAX * 1)  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP = ws.WS2811_STRIP_GRB  # Strip type and colour ordering

MODE_OFF = 'off'
MODE_MANUAL = 'manual'
MODE_AUTOMATIC = 'automatic'

ANIMATION_TYPE_CONSTANT = 'constant'
ANIMATION_TYPE_RAINBOW = 'rainbow'
ANIMATION_TYPE_CYCLE = 'cycle'
ANIMATION_TYPE_WIPE = 'wipe'
ANIMATION_TYPE_CHASE = 'chase'
ANIMATION_TYPE_ALERT = 'alert'

ANIMATION_TYPES = [
    ANIMATION_TYPE_CONSTANT,
    ANIMATION_TYPE_RAINBOW,
    ANIMATION_TYPE_CYCLE,
    ANIMATION_TYPE_WIPE,
    ANIMATION_TYPE_CHASE,
    ANIMATION_TYPE_ALERT
]

LIGHTING_AREA = {
    'rearTop': [22, 23, 24, 25, 26, 27, 28, 29],
    'rearBottom': [4, 5, 6, 7, 8, 9],
    'rearLeft': [10, 11, 12, 13],
    'rearRight': [0, 1, 2, 3],
    'frontLeft': [14, 15, 16, 17],
    'frontRight': [18, 19, 20, 21]
}

PIXELS = LIGHTING_AREA['rearTop'] + LIGHTING_AREA['rearLeft'] + \
         LIGHTING_AREA['rearBottom'] + LIGHTING_AREA['rearRight']

class LedStripeController:

    def __init__(self, settings, animation_interval: float = 1 / 25.):
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
            MODE_OFF: self.set_mode_off,
            MODE_MANUAL: self.set_mode_manual,
            MODE_AUTOMATIC: self.set_mode_automatic
        }
        self.__animation_methods = {
            ANIMATION_TYPE_CONSTANT: (self.__constant, None),
            ANIMATION_TYPE_RAINBOW: (self.__rainbow, None),
            ANIMATION_TYPE_CYCLE: (self.__rainbow_cycle, None),
            ANIMATION_TYPE_WIPE: (self.__wipe, None),
            ANIMATION_TYPE_CHASE: (self.__theatre_chase_entry, self.__theatre_chase_exit),
            ANIMATION_TYPE_ALERT: (self.__alert, None)
        }

        self.__animation_interval = animation_interval
        self.__pixel_iteration = 0
        self.__color_iteration = 0
        self.__color_toggle = 0

        self.__animation_entry = None
        self.__animation_exit = None

        self.__is_put_on = False
        self.__turn_on = False

        self.set_animation(self.__settings, self.__settings.animation_type)
        self.set_mode(self.__settings, self.__settings.lighting_mode)

        self.__stop_animation_thread = Event()
        self.__animation_thread = Thread(
            target=self.__animation_thread_method, daemon=True)
        self.__animation_thread.start()

    def __del__(self):
        """
        Stops the animation thread.
        :return:
        """
        if self.__animation_thread is None:
            return
        if not self.__animation_thread.is_alive:
            return

        self.__stop_animation_thread.set()
        self.__animation_thread.join()

    def on_schoolbag_put_on(self):
        """
        Remembers that the bag is now put on what will retrigger the animation.
        :return:
        """
        self.__is_put_on = True

    def on_schoolbag_put_down(self):
        """
        Switches off the lights if the automatic lighting mode is on.
        :return:
        """
        self.__is_put_on = False
        if self.__settings.lighting_mode == MODE_AUTOMATIC:
            self.__turn_off_all_pixels()

    def on_toggle_lighting_state(self):
        """
        Toggles the lighting between on and off when the manual ligthing mode
        is on.
        :return:
        """
        self.__turn_on = not self.__turn_on
        if self.__settings.lighting_mode == MODE_MANUAL and not self.__turn_on:
            self.__turn_off_all_pixels()

    def on_set_next_animation(self):
        """
        Sets the animation to the next animation type.
        :return:
        """
        index = ANIMATION_TYPES.index(self.__settings.animation_type)
        index = index + 1 if index < len(ANIMATION_TYPES) - 1 else 0
        self.__settings.animation_type = ANIMATION_TYPES[index]

    def set_mode(self, instance, mode):
        """
        Sets the lighting mode and starts any action if needed.

        :param instance: The calling event instance.
        :param mode: The new mode.
        :return:
        """
        assert (instance == self.__settings)
        self.__mode_initializer[mode]()

    def set_mode_off(self):
        """
        Switches off all LEDs.
        :return:
        """
        self.__turn_off_all_pixels()

    def set_mode_automatic(self):
        """
        :return:
        """
        if not self.__is_put_on:
            self.__turn_off_all_pixels()

    def set_mode_manual(self):
        """
        Schedules the configured lighting animation and enables the manual
        switching between on and off.
        :return:
        """
        if not self.__turn_on:
            self.__turn_off_all_pixels()

    def set_animation(self, instance, animation_type):
        """
        Sets the animation method corresponding to the animation type.
        :param instance: The calling event instance.
        :param animation_type: The name of the animation type to use.
        :return:
        """
        assert (instance == self.__settings)
        self.__animation_entry = self.__animation_methods[animation_type][0]
        self.__animation_exit = self.__animation_methods[animation_type][1]

    def __animation_thread_method(self):
        """
        The thread method which cyclically calls the animation methods.
        :return:
        """
        while True:
            if self.__stop_animation_thread.is_set():
                self.set_mode_off()
                return

            if self.__settings.lighting_mode == MODE_OFF:
                continue

            if self.__settings.lighting_mode == MODE_MANUAL and not self.__turn_on:
                continue

            if self.__settings.lighting_mode == MODE_AUTOMATIC and not self.__is_put_on:
                continue

            self.__increment_animation_iteration()

            if self.__animation_entry():
                self.__stripe.show()
            time.sleep(self.__animation_interval)

            if self.__animation_exit is None:
                continue

            if self.__animation_exit():
                self.__stripe.show()

    def __set_pixel(self, color):
        """
        Set all pixels to <color>.
        :param color: The color to set a pixel to.
        :return:
        """
        if self.__stripe.getPixelColor(self.__pixel_iteration) == color:
            return False
        self.__stripe.setPixelColor(self.__pixel_iteration, color)
        return True

    def __turn_off_all_pixels(self):
        """
        Sets all pixels to color black and triggers a led stripe update.
        :return:
        """
        self.__set_and_show_all_pixels(COLOR_BLACK)

    def __set_and_show_all_pixels(self, color):
        """
        Sets all pixels to <color>.
        :param color: The to set the pixel to.
        :return:
        """
        for i in range(self.__stripe.numPixels()):
            self.__stripe.setPixelColor(i, color)

        self.__stripe.show()

    def __constant(self):
        """
        Sets the current pixel to white.
        :return: True if the pixels have to be updated, else False.
        """
        if self.__stripe.getPixelColor(self.__pixel_iteration) == COLOR_WHITE_0_5:
            return False

        for i in range(self.__stripe.numPixels()):
            self.__stripe.setPixelColor(i, COLOR_WHITE_0_5)
        return True

    def __wipe(self):
        """
        Wipe color across display a pixel at a time.
        :return: True if the pixels have to be updated, else False.
        """
        prior_pixel = self.__pixel_iteration - 1 if self.__pixel_iteration > 0 else self.__stripe.numPixels() - 1
        self.__stripe.setPixelColor(prior_pixel, COLOR_BLACK)
        self.__stripe.setPixelColor(self.__pixel_iteration, COLOR_WHITE)
        return True

    def __rainbow(self):
        """
        Draw rainbow that fades across all pixels at once.
        :return: True if the pixels have to be updated, else False.
        """
        for i in range(self.__stripe.numPixels()):
            color = self.__wheel((i + self.__color_iteration) & RGB_MAX)
            self.__stripe.setPixelColor(i, color)
        return True

    def __rainbow_cycle(self):
        """
        Draw rainbow that uniformly distributes itself across all pixels.
        :return: True if the pixels have to be updated, else False.
        """
        for i in range(self.__stripe.numPixels()):
            self.__stripe.setPixelColor(i, self.__wheel(
                (int(i * 256 / self.__stripe.numPixels()) + self.__color_iteration) & RGB_MAX))
        return True

    def __theatre_chase_entry(self):
        """
        Movie theater light style chaser animation; turns on the lights method.
        :return: True if the pixels have to be updated, else False.
        """
        return self.__theater_chase(COLOR_WHITE)

    def __theatre_chase_exit(self):
        """
        Movie theater light style chaser animation; exit method.
        :return: True if the pixels have to be updated, else False.
        """
        return self.__theater_chase(COLOR_BLACK)

    def __theater_chase(self, color):
        """
        Movie theater light style chaser animation.
        :param color: The color to set.
        :return: True if the pixels have to be updated, else False.
        """
        for i in range(0, self.__stripe.numPixels(), 3):
            self.__stripe.setPixelColor(i + self.__color_toggle, color)
        return True

    def __alert(self):
        """
        Alert animation by blinking red.
        :return: True if the pixels have to be updated, else False.
        """
        if self.__color_toggle != 0:
            return False

        current_color = self.__stripe.getPixelColor(self.__pixel_iteration)
        color = COLOR_RED if current_color is COLOR_BLACK else COLOR_BLACK

        for i in range(0, self.__stripe.numPixels()):
            self.__stripe.setPixelColor(i, color)
        return True

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

        self.__color_toggle += 1
        if self.__color_toggle == 3:
            self.__color_toggle = 0

    @staticmethod
    def __wheel(pos):
        """
        Generate rainbow colors across 0-255 positions.
        :param pos: The current animation position.
        :return:
        """
        sec = 3
        lim = int(RGB_MAX / sec)

        if pos < lim * 1:
            return Color(pos * sec, RGB_MAX - pos * sec, 0)
        elif pos < lim * 2:
            pos -= lim
            return Color(RGB_MAX - pos * sec, 0, pos * sec)
        else:
            pos -= lim * 2
            return Color(0, pos * sec, RGB_MAX - pos * sec)
