import json
from os.path import dirname, abspath

import sys
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty, OptionProperty
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Settings(EventDispatcher):
    gender = OptionProperty('Männlich', options=['Männlich', 'Weiblich']) \
        if sys.platform.startswith('linux') else \
        OptionProperty('male', options=['male', 'female'])
    birthday = StringProperty()
    height = NumericProperty(0)
    weight = NumericProperty(0)
    lighting_mode = OptionProperty('Ausgeschaltet', options=['Manuell', 'Automatik', 'Ausgeschaltet']) \
        if sys.platform.startswith('linux') else \
        OptionProperty('off', options=['off', 'manual', 'automatic'])

    def __init__(self, *args, **kwargs):
        """
        Determines the location of the settings file, initially loads all
        settings values and sets up the changes observer.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if sys.platform.startswith('linux'):
            self.__root_directory = '/home/pi/Downloads/bleno-master/examples/schoolbag/'
            self.__settings_file_path = self.__root_directory + 'data.json'
        else:
            self.__root_directory = dirname(abspath(__file__)) + '/'
            self.__settings_file_path = self.__root_directory + 'settings.json'

        self.__load()
        self.__setup_changes_observer()

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
            self.lighting_mode = settings['lightingMode' if sys.platform.startswith('linux') else 'lighting_mode']
            self.current_content = settings['current_content']
            self.tags = settings['tags']

    def save(self):
        """
        Save the current settings to the given json file.
        :return:
        """
        raise NotImplementedError()

    def __setup_changes_observer(self):
        """
        Sets up a file observer which recognizes any changes in the settings
        file and triggers an update of all settings.
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

    def __init__(self, settings_file_path, reload_settings):
        super().__init__()
        self.settings_file_path = settings_file_path
        self.reload_settings = reload_settings

    def on_modified(self, event):
        if event.src_path != self.settings_file_path:
            return
        self.reload_settings()
