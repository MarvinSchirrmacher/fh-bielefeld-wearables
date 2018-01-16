import json
from os.path import dirname, abspath

from kivy.properties import NumericProperty, ObjectProperty, StringProperty, OptionProperty
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Settings:
    def __init__(self):
        self.__root_directory = dirname(abspath(__file__))
        self.__settings_file_path = self.__root_directory + '/settings.json'

        self.gender = OptionProperty('None', options=['male', 'female', 'undefined'])
        self.birthday = StringProperty('undefined')
        self.height = NumericProperty(0)
        self.weight = NumericProperty(0)

        self.__load()
        self.__setup_watchdog()

    def __load(self):
        """
        Opens the json settings file and reads in all values.
        :return:
        """
        with open(self.__settings_file_path) as settings_file:
            settings = json.load(settings_file)
            self.gender = settings['gender']
            self.birthday = settings['birthday']
            self.height = settings['height']
            self.weight = settings['weight']

    def __setup_watchdog(self):
        """
        Sets up a file watchdog which recognizes any changes in the settings
        file and triggers an settings update.
        :return:
        """
        self.settings_handler = SettingsFileHandler(
            self.__settings_file_path, self.__load)
        self.observer = Observer()
        self.observer.schedule(
            self.settings_handler, path=self.__root_directory, recursive=False)
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
