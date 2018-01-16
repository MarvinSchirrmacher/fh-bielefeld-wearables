from kivy.clock import Clock

import importlib

from settings import Settings

module_rpi = importlib.util.find_spec("RPi")
module_spi = importlib.util.find_spec("spi")
dependencies_are_installed = module_rpi is not None and module_spi is not None
if dependencies_are_installed:
    from mfrc522.mfrc522 import MFRC522


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

        if not dependencies_are_installed:
            self.__read_callback = lambda x: print("Can not read")
        else:
            self.__rfid_reader = MFRC522()
            self.__read_callback = self.__read

    def start(self, read_interval: float = 1 / 2.):
        """
        Starts the cyclically reading for any rfid tags.
        :param read_interval: The read frequency in seconds.
        :return:
        """
        self.__reader = Clock.schedule_interval(
            self.__read_callback, read_interval)

    def stop(self):
        """
        Stops the cyclically reading for any rfid tags.
        :return:
        """
        Clock.unschedule(self.__reader)

    def __read(self):
        """
        Reads any tag and updates the current configuration if a tag was
        detected.
        :return:
        """
        status, tag_type = self.__reader.MFRC522_Request(self.__reader.PICC_REQIDL)
        if status != self.__reader.MI_OK:
            return

        status, uid = self.__reader.MFRC522_Anticoll()
        if not status == self.__reader.MI_OK:
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
        self.__reader.MFRC522_SelectTag(uid)
        status = self.__reader.MFRC522_Auth(
            self.__reader.PICC_AUTHENT1A,
            self.__authentication_key_length,
            self.__authentication_key, uid)

        if status == self.__reader.MI_OK:
            self.__reader.MFRC522_Read(self.__authentication_key_length)
            self.__reader.MFRC522_StopCrypto1()
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
        if self.__settings.current_configuration.contains(uid):
            self.__settings.current_configuration.remove(uid)
        else:
            self.__settings.current_configuration.append(uid)
