class ws:
    WS2811_STRIP_GRB = 0

    def __init__(self):
        pass


class Adafruit_NeoPixel:
    def __init__(self, led_count, led_pin, led_freq_hz, led_dma,
                 led_invert, led_brightness, led_channel, led_strip):
        pass

    def begin(self):
        pass

    def numPixels(self):
        return 30

    def getPixelColor(self, pixel):
        return Color(0, 0, 0)

    def setPixelColor(self, pixel, color):
        pass

    def show(self):
        print('[Adafruit NeoPixel] Show')

class Color:
    def __init__(self, r, g, b):
        pass
