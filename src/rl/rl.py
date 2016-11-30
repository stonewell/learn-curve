from math import exp

import random
import numpy

import state.macd

class ReinforceLearn(object):
    def __init__(self, state, action):
        self.__state = state
        self.__action = action

        demensions = self.__state.get_states_demension()
        demensions += tuple([self.__action.get_action_count()])

        self.table = numpy.zeros(demensions, dtype = float)

        self.first = True
        self.last_state = None
        self.learning_rate = 0.1
        self.discount_rate = 0.9
        self.exploitation_rate = 1.0

    def _get_max_qvalue(self, st):
        return self.table[tuple(map(int, st))].max()

    def _get_best_action(self, st):
        return self.table[tuple(map(int, st))].argmax()

    def _get_qvalue(self, st, action):
        index = map(int, st + tuple([action]))
        
        return self.table[tuple(index)]

    def _set_qvalue(self, st, action, qvalue):
        index = st + tuple([action])
        index = map(int, list(index))

        self.table[tuple(index)] = qvalue

    def get_state(self, values):
        states = self.__state.get_states(values)

        return states

    def learn(self, values, st):
        if self.first:
            self.first = False
            self.last_state = st
            return

        for i in range(self.__action.get_action_count()):
            reinforcement = self.__action.get_reinforcement(i, values)

            old_qvalue = self._get_qvalue(self.last_state, i)

            new_qvalue = ((1 - self.learning_rate) * old_qvalue +
                self.learning_rate * (reinforcement + self.discount_rate * self._get_max_qvalue(st)))
            self._set_qvalue(self.last_state, i, new_qvalue)
        self.last_state = st

    def select_action(self, state):
        sum = 0.0

        action_values = numpy.zeros(self.__action.get_action_count(), dtype=float)
        for i in range(self.__action.get_action_count()):
            qvalue = self._get_qvalue(state, i)
            action_values[i] = exp(self.exploitation_rate * qvalue)

        sum = action_values.sum()

        if sum == 0.0:
            return self._get_best_action(state)

        action_values /= sum

        action = 0
        cum_prob = 0.0
        random_num = random.random()

        while random_num > cum_prob and action < self.__action.get_action_count():
            cum_prob += action_values[action]
            action += 1

        return action - 1 if action > 1 else action

if __name__ == "__main__":
    rl = ReinforceLearn()
    print rl.table
    print rl.state_mapping
    print rl.state_mapping.sum(1)
    print rl.state_mapping.sum(2)
    print rl.state_mapping[2].argmax(),rl.state_mapping[2].max()
    print rl.state_mapping.argmax(2),rl.state_mapping.max(2)
    print rl.state_mapping.argmax(1),rl.state_mapping.max(1)
