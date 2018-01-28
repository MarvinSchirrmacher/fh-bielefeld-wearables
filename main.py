from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel

from content_management import ContentManagement
from led_stripe_controller import LedStripeController
from settings import Settings
from trimmer import Trimmer


class Management(TabbedPanel):
    """
    Base management class for all business logic.
    """
    settings = Settings()
    content_management = ContentManagement(settings)
    led_stripe_controller = LedStripeController(settings)
    trimmer = Trimmer(settings, led_stripe_controller)

    def __init__(self):
        super().__init__()

    def __del__(self):
        self.content_management.__del__()
        self.led_stripe_controller.__del__()


class SchoolBagApp(App):
    """
    Program entry point which starts the graphical user interface and the
    management class.
    """

    def build(self):
        self.__management = Management()
        return self.__management

    def on_stop(self):
        self.__management.__del__()


if __name__ == '__main__':
    SchoolBagApp().run()
