from kivy.clock import Clock

from settings import Settings


class Trimmer:
    def __init__(self, settings: Settings):
        """
        Saves a reference to the settings.
        :return:
        """
        self.__settings = settings
        self.__analyzer = None

    def start(self, analysis_interval: float = 1 / 2.):
        """
        Start the cyclically analysis of the pressure distribution.
        :param analysis_interval: The analysis frequency in seconds.
        :return:
        """
        self.__analyzer = Clock.schedule_interval(self.__analyse, analysis_interval)

    def stop(self):
        """
        Stops the cyclically analysis of the pressure distribution.
        :return:
        """
        Clock.unschedule(self.__analyzer)

    @staticmethod
    def __analyse(dt):
        """
        Reads several sensor data to calculate the current pressure
        distribution if the school bag is currently carried.
        :param dt:
        :return:
        """
        print('Analyse pressure distribution with parameter "dt" = "%s"' % str(dt))
