from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel

from content_management import ContentManagement
from settings import Settings
from trimmer import Trimmer


class Management(TabbedPanel):
    """
    Base management class for all business logic.
    """
    settings = Settings()
    trimmer = Trimmer(settings)
    content_management = ContentManagement(settings)

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
