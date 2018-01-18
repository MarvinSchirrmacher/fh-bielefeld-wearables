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


class SchoolBagApp(App):
    """
    Program entry point which starts the graphical user interface and the
    management class.
    """

    def build(self):
        return Management()


if __name__ == '__main__':
    SchoolBagApp().run()
