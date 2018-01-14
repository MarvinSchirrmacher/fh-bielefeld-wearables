import json
from os.path import dirname

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class SchoolBagApp(App):
    """
    Program entry point which starts the graphical user interface and with it
    all subroutines.
    """
    def build(self):
        self.root_directory = dirname(__file__)
        self.settings_file_path = self.root_directory + '/settings.json'

        self.setup_pressure_distribution()
        self.button = Button(text='Intelligente Schultasche')
        self.load_settings()
        self.setup_settings_watchdog()

        return self.button

    def load_settings(self):
        """
        Opens the json settings file and reads in all values.
        :return:
        """
        with open(self.settings_file_path) as settings_file:
            self.settings = json.load(settings_file)
            self.button.text = str(self.settings)

    def setup_pressure_distribution(self):
        """
        Sets up and schedules a routine which cyclically analyses the pressure
        distribution of the carried school bag.
        :return:
        """
        Clock.schedule_interval(self.analyse_pressure_distribution, 1 / 10.)

    def analyse_pressure_distribution(self, dt):
        """
        Reads several sensor data to calculate the current pressure
        distribution if the school bag is currently carried.
        :param dt:
        :return:
        """
        pass

    def setup_settings_watchdog(self):
        """
        Sets up a file watchdog which recognizes any changes in the settings
        file and triggers an settings update.
        :return:
        """
        self.settings_handler = SettingsFileHandler(
            self.settings_file_path, self.load_settings)
        self.observer = Observer()
        self.observer.schedule(
            self.settings_handler, path=self.root_directory, recursive=False)
        self.observer.start()


class SettingsFileHandler(FileSystemEventHandler):
    """
    Handler for the settings file watchdog.
    """

    def __init__(self, settings_file_path, load_settings):
        super().__init__()
        self.settings_file_path = settings_file_path
        self.load_settings = load_settings

    def on_modified(self, event):
        if event.src_path != self.settings_file_path:
            return
        self.load_settings()


if __name__ == '__main__':
    SchoolBagApp().run()
