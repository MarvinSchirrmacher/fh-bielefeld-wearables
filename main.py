from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel

from settings import Settings
from trimmer import Trimmer


class Management(TabbedPanel):
    settings = ObjectProperty(None, allownone=True)
    trimmer = ObjectProperty(None, allownone=True)

    def __init__(self):
        super().__init__()
        self.settings = ObjectProperty(Settings(), allownone=True)
        self.trimmer = ObjectProperty(Trimmer(), allownone=True)


class SchoolBagApp(App):
    """
    Program entry point which starts the graphical user interface and with it
    all subroutines.
    """
    def build(self):
        return Management()


if __name__ == '__main__':
    SchoolBagApp().run()
