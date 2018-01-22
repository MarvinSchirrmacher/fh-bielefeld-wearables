import sys

from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, partial

from settings import Settings

if sys.platform.startswith('linux'):
    from mfrc522.mfrc522 import MFRC522
else:
    from mock.mfrc522_mock import MFRC522


class ContentManagement:
    """
    Manages the school bag content.

    Checks for new rfid tags, updates the current configuration and
    compares the current configuration with the configured configuration
    for the current day.
    """

    def __init__(self, settings: Settings):
        """
        Saves a reference to the settings and sets up the rfid reader.
        :param settings: The settings object to read from.
        """
        self.__settings = settings
        self.__reader = None
        self.__authentication_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.__authentication_key_length = 8

        self.__rfid_reader = MFRC522()
        self.__read_callback = self.__read

    def start(self, read_interval: float = 1 / 2.):
        """
        Starts the cyclically reading for any rfid tags.
        :param read_interval: The read frequency in seconds.
        :return:
        """
        self.__reader = Clock.schedule_interval(
            partial(self.__read_callback, self), read_interval)

    def stop(self):
        """
        Stops the cyclically reading for any rfid tags.
        :return:
        """
        Clock.unschedule(self.__reader)

    def __read(self, *largs):
        """
        Reads any tag and updates the current configuration if a tag was
        detected.
        :return:
        """
        status, tag_type = self.__rfid_reader.MFRC522_Request(self.__rfid_reader.PICC_REQIDL)
        if status != self.__rfid_reader.MI_OK:
            return

        status, uid = self.__rfid_reader.MFRC522_Anticoll()
        if not status == self.__rfid_reader.MI_OK:
            return

        if not self.__authenticate(uid):
            return

        self.__update_current_configuration(uid)

    def __authenticate(self, uid):
        """
        Authenticates the given rfid tag uid.
        :param uid: The rfid tag uid.
        :return: True if authenticated, else False.
        """
        self.__rfid_reader.MFRC522_SelectTag(uid)
        status = self.__rfid_reader.MFRC522_Auth(
            self.__rfid_reader.PICC_AUTHENT1A,
            self.__authentication_key_length,
            self.__authentication_key, uid)

        if status == self.__rfid_reader.MI_OK:
            self.__rfid_reader.MFRC522_Read(self.__authentication_key_length)
            self.__rfid_reader.MFRC522_StopCrypto1()
            return True
        else:
            return False

    def __update_current_configuration(self, uid):
        """
        Adds the given uid to the current configuration if it does not contains
        the uid, else removes the uid from the current configuration.
        :param uid: The uid to look for.
        :return:
        """
        print('[Content management] Update current configuration')
        if uid in self.__settings.current_content:
            self.__settings.current_content.remove(uid)
        else:
            self.__settings.current_content.append(uid)


class ContentListItem(ListProperty):
    name = StringProperty()
    tag = StringProperty()

    def __init__(self, name='unnamed', tag='0000 0000 0000'):
        super().__init__()
        self.name = StringProperty(name)
        self.tag = StringProperty(tag)
