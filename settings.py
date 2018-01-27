import datetime
import json
import locale
import os
import sys
from os.path import dirname, abspath

from kivy.adapters.listadapter import ListAdapter
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty, OptionProperty, ListProperty
from kivy.uix.image import Image
from kivy.uix.listview import ListItemLabel, CompositeListItem
from kivy.uix.selectableview import SelectableView
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ListItemImage(SelectableView, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Settings(EventDispatcher):
    WEEKDAY = {
        0: 'monday',
        1: 'tuesday',
        2: 'wednesday',
        3: 'thursday',
        4: 'friday',
        5: 'saturday',
        6: 'sunday'
    }
    FILE_WRITE_PERMISSION = 'w'

    gender = OptionProperty('male', options=['male', 'female'])
    birthday = StringProperty()
    height = NumericProperty(0)
    weight = NumericProperty(0)
    lighting_mode = OptionProperty('off', options=['off', 'manual', 'automatic'])
    animation_type = StringProperty()
    current_content = ListProperty()
    target_content = ListProperty()

    def __init__(self, *args, **kwargs):
        """
        Determines the location of the settings file, initially loads all
        settings values and sets up the changes observer.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.__root_directory = dirname(abspath(__file__)) + '/'
        self.__settings_file_path = self.__root_directory + 'data.json'
        self.__new_tags_file_path = self.__root_directory + 'newRFID.json'

        if sys.platform.startswith('darwin'):
            locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
        now = datetime.datetime.now()
        self.current_day = self.WEEKDAY[0]  # now.weekday()]
        self.current_day_translated = now.strftime('%A')
        print('Today is %s' % self.current_day_translated)

        self.content_to_insert = []
        self.content_to_remove = []
        self.__initialize_comparison_lists()
        self.__load()
        self.__setup_changes_observer()

    def save(self):
        """
        Save the current settings to the given json file.
        :return:
        """
        with open(self.__settings_file_path, self.FILE_WRITE_PERMISSION) as file:
            settings_to_save = {
                'gender': self.gender,
                'birthday': self.birthday,
                'height': self.height,
                'weight': self.weight,
                'lightingMode': self.lighting_mode,
                'animationType': self.animation_type,
                'tags': self.tags,
                'currentContent': self.current_content
            }
            json.dump(settings_to_save, file)

    def register_new_tag(self, tag):
        """
        Appends a new tag to the list of new tags and updates the new tags file.
        :param tag:
        :return:
        """
        if tag in self.__new_tags:
            return
        self.__new_tags.append(tag)
        self.__update_new_tags_file()

    def __load(self):
        """
        Loads all properties by reading in the json settings files.
        :return:
        """
        self.__read_in_settings_file()
        self.__read_in_new_tags_file()
        self.__update_new_tags()

    def __read_in_settings_file(self):
        if os.stat(self.__settings_file_path).st_size == 0:
            self.tags = {}
            return

        with open(self.__settings_file_path) as settings_file:
            settings = json.load(settings_file)
            self.gender = settings['gender']
            self.birthday = settings['birthday']
            self.height = settings['height']
            self.weight = settings['weight']
            self.lighting_mode = settings['lightingMode']
            self.animation_type = settings['animationType']
            self.tags = settings['tags']
            self.target_content = [
                tag for tag in self.tags if
                self.current_day in self.tags[tag]
                and self.tags[tag][self.current_day] == "1"]
            self.current_content = settings['currentContent']

        self.update_comparison_lists(None, None)

    def __read_in_new_tags_file(self):
        """
        Opens the new tags file and copies its list into the internal list of
        new tags.
        :return:
        """
        if os.stat(self.__new_tags_file_path).st_size == 0:
            self.__new_tags = []
            return

        with open(self.__new_tags_file_path) as file:
            tags_object = json.load(file)
            self.__new_tags = tags_object['tags']

    def __update_new_tags(self):
        """
        Deletes any tag from the list of new tags if it is listed in the list
        of known tags.
        :return:
        """
        for tag in self.tags:
            if tag not in self.__new_tags:
                continue
            self.__new_tags.remove(tag)

        self.__update_new_tags_file()

    def __update_new_tags_file(self):
        """
        Opens the new tags file and overrides its content with the internal
        list of new tags.
        :return:
        """
        with open(self.__new_tags_file_path, self.FILE_WRITE_PERMISSION) as file:
            json.dump({'tags': self.__new_tags}, file)

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

    def __initialize_comparison_lists(self):
        self.__data_converter = lambda row, item: {
            'orientation': 'horizontal',
            'cls_dicts': [
                {'cls': ListItemImage, 'kwargs': {'source': item['image']}},
                {'cls': ListItemLabel, 'kwargs': {'text': item['name']}}
            ]
        }

        self.content_to_insert_adapter = ListAdapter(
            data=self.content_to_insert,
            args_converter=self.__data_converter,
            cls=CompositeListItem)

        self.content_to_remove_adapter = ListAdapter(
            data=self.content_to_remove,
            args_converter=self.__data_converter,
            cls=CompositeListItem)

    def update_comparison_lists(self, instance, value):
        self.content_to_insert = set(self.target_content).difference(self.current_content)
        self.content_to_insert_adapter.data = [
            {'image': 'icons/default_image.png', 'name': 'Unbekanntes Material'} if tag not in self.tags else
            {'image': 'icons/%s.png' % self.tags[tag]['imgName'], 'name': self.tags[tag]['materialName']}
            for tag in self.content_to_insert]
        self.content_to_insert_adapter.data.prop.dispatch(
            self.content_to_insert_adapter.data.obj())

        self.content_to_remove = set(self.current_content).difference(self.target_content)
        self.content_to_remove_adapter.data = [
            {'image': 'icons/default_image.png', 'name': 'Unbekanntes Material'} if tag not in self.tags else
            {'image': 'icons/%s.png' % self.tags[tag]['imgName'], 'name': self.tags[tag]['materialName']}
            for tag in self.content_to_remove]
        self.content_to_remove_adapter.data.prop.dispatch(
            self.content_to_remove_adapter.data.obj())


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
