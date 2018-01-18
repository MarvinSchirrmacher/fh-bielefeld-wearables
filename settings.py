import json
from os.path import dirname, abspath

from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty, OptionProperty
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Settings(EventDispatcher):
    gender = OptionProperty(
        'Männlich', options=['Männlich', 'Weiblich'])
    birthday = StringProperty()
    height = NumericProperty(0)
    weight = NumericProperty(0)
    lighting_mode = OptionProperty(
        'Ausgeschaltet', options=['Manuell', 'Automatik', 'Ausgeschaltet'])

    def __init__(self, *args, **kwargs):
        """
        Determines the location of the settings file, initially loads all
        settings values and sets up the changes observer.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.__root_directory = dirname(abspath(__file__)) + '/../bleno-master/examples/schoolbag/'
        self.__settings_file_path = self.__root_directory + 'data.json' # '/settings.json'

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
            self.lighting_mode = settings['lightingMode']
            #self.week_content = settings['week_content'] # Jonthan did not implemented this until now in his settings file
            #self.current_content = settings['current_content'] # Jonthan did not implemented this until now in his settings file
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

    def __init__(self, settings_file_path, load_settings):
        super().__init__()
        self.settings_file_path = settings_file_path
        self.load_settings = load_settings

    def on_modified(self, event):
        if event.src_path != self.settings_file_path:
            return
        self.load_settings()
