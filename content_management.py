import datetime

from kivy.adapters.listadapter import ListAdapter
from kivy.event import EventDispatcher
from kivy.properties import ListProperty
from kivy.uix.image import Image
from kivy.uix.listview import CompositeListItem, ListItemLabel
from kivy.uix.selectableview import SelectableView

from service.informer import Informer
from tag_registration import TagRegistration


class ContentManagement(EventDispatcher):
    """
    Manages the school bag content.

    Checks for new rfid tags, updates the current configuration and
    compares the current configuration with the configured configuration
    for the current day.
    """

    WEEKDAY = {
        0: 'monday',
        1: 'tuesday',
        2: 'wednesday',
        3: 'thursday',
        4: 'friday',
        5: 'saturday',
        6: 'sunday'
    }
    target_content = ListProperty()
    content_to_insert = ListProperty()
    content_to_remove = ListProperty()

    def __init__(self, settings, *args, **kwargs):
        """
        Saves a reference to the settings and sets up the rfid reader.
        :param settings: The settings object to read from.
        """
        super().__init__(*args, **kwargs)
        self.__settings = settings
        self.__settings.bind(
            current_content=self.update_content_lists,
            tags=self.update_content_lists)
        self.__updated_content = False
        self.target_content = self.__determine_today_s_target_content()

        self.__tag_registration = TagRegistration(
            self.__update_current_configuration)
        self.__tag_registration.start_tag_reading()

        self.__initialize_content_adapter()

    def __del__(self):
        """
        Stops the tag reader.
        :return:
        """
        self.__tag_registration.stop_tag_reading()

    def __determine_today_s_target_content(self):
        """
        Returns a list of tags which are needed for the current weekday.
        :return: The target content tag list.
        """
        now = datetime.datetime.now()
        self.current_day = self.WEEKDAY[now.weekday()]

        return [
            tag for tag in self.__settings.tags
            if self.current_day in self.__settings.tags[tag]
            and self.__settings.tags[tag][self.current_day] == "1"]

    def __update_current_configuration(self, tag):
        """
        Adds the given uid to the current configuration if it does not contains
        the uid, else removes the uid from the current configuration.
        :param tag: The tag uid to look for.
        :return:
        """
        if tag not in self.__settings.tags:
            Informer.show_popup(
                'Tasche packen',
                'Neues Schumaterial erkannt.\n'
                'Bitte zuerst in der App registrieren. :)')
            self.__settings.register_new_tag(tag)

        if tag in self.__settings.current_content:
            self.__settings.current_content.remove(tag)
        else:
            self.__settings.current_content.append(tag)

        self.__settings.save()

        if self.content_to_insert or self.content_to_remove:
            return

        Informer.show_popup(
            'Tasche packen',
            'Die Tasche ist richtig gepackt, es kann losgehen. :)')

    def __initialize_content_adapter(self):
        """
        Initializes the list view adapters for the insert and remove content
        lists.
        :return:
        """
        self.__data_converter = lambda row, item: {
            'orientation': 'horizontal',
            'cls_dicts': [
                {'cls': ListItemImage, 'kwargs': {'source': item['image']}},
                {'cls': ListItemLabel, 'kwargs': {'text': item['name']}}
            ]
        }

        self.current_content_adapter = ListAdapter(
            data=self.__settings.current_content,
            args_converter=self.__data_converter,
            cls=CompositeListItem)

        self.content_to_insert_adapter = ListAdapter(
            data=self.content_to_insert,
            args_converter=self.__data_converter,
            cls=CompositeListItem)

        self.content_to_remove_adapter = ListAdapter(
            data=self.content_to_remove,
            args_converter=self.__data_converter,
            cls=CompositeListItem)

        self.update_content_lists(self.__settings, self.__settings.current_content)

    def update_content_lists(self, instance, value):
        """
        Compares the target content list with the current content list to fill
        the insert and the remove content list.
        :param instance: The calling settings.
        :param value: Updated setting property.
        :return:
        """
        assert(instance == self.__settings)

        self.target_content = self.__determine_today_s_target_content()
        self.__settings.current_content = set(self.__settings.current_content)\
            .intersection(self.__settings.tags.keys())

        self.__update_tag_list_adapter(
            self.current_content_adapter,
            self.__settings.current_content)

        self.content_to_insert = set(self.target_content)\
            .difference(self.__settings.current_content)
        self.__update_tag_list_adapter(
            self.content_to_insert_adapter,
            self.content_to_insert)

        self.content_to_remove = set(self.__settings.current_content)\
            .difference(self.target_content)
        self.__update_tag_list_adapter(
            self.content_to_remove_adapter,
            self.content_to_remove)

    def __update_tag_list_adapter(self, adapter: ListAdapter, tags):
        adapter.data = [
            {
                'image': 'icons/default_image.png',
                'name': 'Unbekanntes Material'
            }
            if tag not in self.__settings.tags else
            {
                'image': 'icons/%s.png' % self.__settings.tags[tag]['imgName'],
                'name': self.__settings.tags[tag]['materialName']
            }
            for tag in tags
        ]
        adapter.data.prop.dispatch(adapter.data.obj())


class ListItemImage(SelectableView, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
