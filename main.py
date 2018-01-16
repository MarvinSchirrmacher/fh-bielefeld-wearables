from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel

from settings import Settings
from trimmer import Trimmer


class Management(TabbedPanel):
    settings = ObjectProperty(Settings())
    trimmer = ObjectProperty(Trimmer())

    def __init__(self):
        super().__init__()


class SchoolBagApp(App):
    """
    Program entry point which starts the graphical user interface and with it
    all subroutines.
    """
    def build(self):
        return Management()


if __name__ == '__main__':
    SchoolBagApp().run()
