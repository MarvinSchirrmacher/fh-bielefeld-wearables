from threading import Event, Thread

import sys

import time

if sys.platform.startswith('linux'):
    from mfrc522.mfrc522 import MFRC522
else:
    from mock.mfrc522_mock import MFRC522


class TagRegistration:
    def __init__(self, update_tags_list):
        """
        Sets up the rfid reader.
        """
        self.__rfid_reader = MFRC522()
        self.__authentication_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.__authentication_key_length = 8
        self.__rfid_registration = {
            'uid': [],
            'counter': 0,
            'errors': 0
        }

        self.__update_tags_list = update_tags_list

        self.__read_thread = None
        self.__stop_read_thread = Event()

    def start_tag_reading(self):
        """
        Starts the cyclically reading for any rfid tags.
        :return:
        """
        if self.__read_thread is not None and not self.__read_thread.is_alive:
            return

        self.__read_thread = Thread(target=self.__read_thread_method, daemon=True)
        self.__read_thread.start()

    def stop_tag_reading(self):
        """
        Stops the cyclically reading for any rfid tags.
        :return:
        """
        if self.__read_thread is None:
            return
        if not self.__read_thread.is_alive:
            return

        self.__stop_read_thread.set()
        self.__read_thread.join()

    def __read_thread_method(self):
        """
        Cyclically reads for any rfid tag in front of the reader.

        Can be stopped by setting the __stop_read_thread event.
        :return:
        """
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
        if not self.__read_succeeded(status):
            return

        status, uid = self.__rfid_reader.MFRC522_Anticoll()
        if not status == self.__rfid_reader.MI_OK:
            print('[Content management] RFID anticoll failed')
            return

        if not self.__authenticate_read(uid):
            print('[Content management] RFID authentication failed')
            return

        if not self.__reached_acceptance_level(uid):
            return

        print('[Content management] Accepted uid')
        uid_hex = [format(fragment, '02x') for fragment in uid]
        self.__update_tags_list('-'.join(uid_hex))

    def __read_succeeded(self, status):
        """
        Compensates unsuccessful reads as they cyclically occur although a tag
        remains in front of the reader.
        :param status: The the read status.
        :return: True if reading succeeded, else False.
        """
        if status != self.__rfid_reader.MI_OK:
            if self.__rfid_registration['errors'] < 1:
                self.__rfid_registration['errors'] += 1
            else:
                self.__rfid_registration['counter'] = 0
            return False

        self.__rfid_registration['errors'] = 0
        return True

    def __authenticate_read(self, uid):
        """
        Authenticates the given unique id.
        :param uid: The rfid tag unique id.
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

    RFID_REGISTRATION_ACCEPTANCE = 2

    def __reached_acceptance_level(self, uid):
        """
        Counts the number of reads of the same unique id one after the other.

        A unique id has to be read twice to be accepted as being read in. That
        way the user has to hold the tag in front of the reader for at least
        one second.
        :param uid: The unique id which was registered by the reader.
        :return: True if the unique id reached the acceptance level, else False.
        """
        if uid == self.__rfid_registration['uid']:
            self.__rfid_registration['counter'] += 1
        else:
            self.__rfid_registration['uid'] = uid
            self.__rfid_registration['counter'] = 1

        if self.__rfid_registration['counter'] < self.RFID_REGISTRATION_ACCEPTANCE:
            return False

        self.__rfid_registration['counter'] = 0
        return True
