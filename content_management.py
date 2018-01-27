import sys
import time
from threading import Thread, Event

from kivy.properties import StringProperty, ListProperty

from settings import Settings

if sys.platform.startswith('linux'):
    from mfrc522.mfrc522 import MFRC522
else:
    from mock.mfrc522_mock import MFRC522


RFID_REGISTRATION_ACCEPTANCE = 2


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
        self.__read_thread = None
        self.__stop_read_thread = Event()
        self.__authentication_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.__authentication_key_length = 8
        self.__rfid_reader = MFRC522()
        self.__rfid_registration = {
            'uid': [],
            'counter': 0,
            'buffer': 0
        }
        self.start_rfid_reading()

    def start_rfid_reading(self):
        """
        Starts the cyclically reading for any rfid tags.
        :return:
        """
        if self.__read_thread is not None and not self.__read_thread.is_alive:
            return

        self.__read_thread = Thread(target=self.__read_thread_method)
        self.__read_thread.start()

    def stop_rfid_reading(self):
        """
        Stops the cyclically reading for any rfid tags.
        :return:
        """
        if self.__read_thread is None:
            return
        if not self.__read_thread.is_alive:
            return

        self.__stop_read_thread.set()

    def __read_thread_method(self):
        while True:
            if self.__stop_read_thread.is_set():
                return

            self.__read()
            time.sleep(0.25)

    def __read(self):
        """
        Reads any tag and updates the current configuration if a tag was
        detected.
        :return:
        """
        status, tag_type = self.__rfid_reader.MFRC522_Request(self.__rfid_reader.PICC_REQIDL)
        if status != self.__rfid_reader.MI_OK:
            if self.__rfid_registration['buffer'] < 1:
                self.__rfid_registration['buffer'] += 1
            else:
                self.__rfid_registration['counter'] = 0
            return

        self.__rfid_registration['buffer'] = 0

        status, uid = self.__rfid_reader.MFRC522_Anticoll()
        if not status == self.__rfid_reader.MI_OK:
            print('[Content management] RFID anticoll failed')
            return

        if not self.__authenticate(uid):
            print('[Content management] RFID authentication failed')
            return

        if uid == self.__rfid_registration['uid']:
            self.__rfid_registration['counter'] += 1
        else:
            self.__rfid_registration['uid'] = uid
            self.__rfid_registration['counter'] = 1

        if self.__rfid_registration['counter'] < RFID_REGISTRATION_ACCEPTANCE:
            return

        self.__rfid_registration['counter'] = 0

        print('[Content management] Accepted uid')
        uid_hex = [format(fragment, '02x') for fragment in uid]
        self.__update_current_configuration('-'.join(uid_hex))

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

        if status != self.__rfid_reader.MI_OK:
            return False

        self.__rfid_reader.MFRC522_Read(self.__authentication_key_length)
        self.__rfid_reader.MFRC522_StopCrypto1()
        return True

    def __update_current_configuration(self, tag):
        """
        Adds the given uid to the current configuration if it does not contains
        the uid, else removes the uid from the current configuration.
        :param tag: The tag uid to look for.
        :return:
        """
        print('[Content management] Update current configuration')
        if tag not in self.__settings.tags:
            print('[Content management] The tag "%s" is new and have to be registered via smartphone app' % tag)
            self.__settings.register_new_tag(tag)

        if tag in self.__settings.current_content:
            print('[Content management] Remove tag form current content')
            self.__settings.current_content.remove(tag)
        else:
            print('[Content management] Append tag to current content')
            self.__settings.current_content.append(tag)

        self.__settings.save()


class ContentListItem(ListProperty):
    name = StringProperty()
    tag = StringProperty()

    def __init__(self, name='unnamed', tag='0000 0000 0000'):
        super().__init__()
        self.name = StringProperty(name)
        self.tag = StringProperty(tag)
