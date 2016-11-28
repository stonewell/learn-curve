'''
0: DIF > 0 < 0 = 0
1: DEA > 0 < 0 = 0
2: DIF > DEA, DIF < DEA, DIF = DEA
'''
import numpy

from state.macd import Macd

class MacdNDays(object):
    def __init__(self, ndays = 5):
        self.__ndays = ndays
        self.__macd_state = Macd()
        self.__states_demension, self.__states_mapping = self.__init_state_mapping_table(ndays)
        self.__values = [0] * self.__ndays

    def __init_state_mapping_table(self, ndays):
        demensions = self.__macd_state.get_states_demension()

        states_mapping = numpy.zeros(demensions)

        count = 0

        for index in numpy.ndindex(demensions):
            states_mapping[index] = count
            count += 1

        return tuple([states_mapping.size] * ndays), states_mapping

    def get_states_demension(self):
        return self.__states_demension

    def get_states(self, values):
        macd_state = self.__states_mapping[self.__macd_state.get_states(values)]
        self.__values.append(macd_state)

        if len(self.__values) > self.__ndays:
            self.__values = self.__values[- self.__ndays:]

        if len(self.__values) < self.__ndays:
            return None
        
        return tuple(self.__values)
