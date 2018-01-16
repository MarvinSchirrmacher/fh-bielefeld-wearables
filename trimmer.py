from kivy.clock import Clock


class Trimmer:
    def __init__(self):
        """
        Sets up and schedules a routine which cyclically analyses the pressure
        distribution of the carried school bag.
        :return:
        """
        self.__analyzer = None

    def start(self):
        self.__analyzer = Clock.schedule_interval(self.analyse, 1 / 2.)

    def stop(self):
        Clock.unschedule(self.__analyzer)

    @staticmethod
    def analyse(dt):
        """
        Reads several sensor data to calculate the current pressure
        distribution if the school bag is currently carried.
        :param dt:
        :return:
        """
        print('Analyse pressure distribution with parameter "dt" = "%s"' % str(dt))
