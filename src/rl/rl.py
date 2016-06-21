from math import exp

import random
import numpy

import state.macd
import action

class rl(object):
    def __init__(self):
        self.state_mapping, self.state_count = self._init_state_mapping_table()
        self.table = numpy.zeros((self.state_count, action.get_action_count()), dtype = float)
        self.first = True
        self.last_state = None
        self.last_action = None
        self.learning_rate = 0.1
        self.discount_rate = 0.9
        self.exploitation_rate = 1.0

    def _init_state_mapping_table(self):
        demensions = state.macd.get_states_demension()

        sm = numpy.zeros(demensions)

        count = 0
        
        for index in numpy.ndindex(demensions):
            sm[index] = count
            count += 1

        return sm, sm.size

    def _get_max_qvalue(self, state):
        return self.table[state].max()

    def _get_best_action(self, state):
        return self.table[state].argmax()

    def _get_qvalue(self, state, action):
        return self.table[state][action]

    def _set_qvalue(self, state, action, qvalue):
        self.table[state][action] = qvalue

    def get_state(self, values):
        macd_states = state.macd.get_states(values)

        state = self.state_mapping[macd_states]

        return state
        
    def learn(self, state, action):
        reinforcement = action.get_reinforcement(action)

        if self.first:
            self.last_state, self.last_action = state, action
            return

        old_qvalue = self._get_qvalue(self.last_state, self.last_action)
        new_qvalue = (1 - self.learning_rate) * old_qvalue + self.learning_rate * (reinforcement + self.discount_rate * self._get_max_qvalue(state))
        self._set_qvalue(self.last_state, self.last_action, new_qvalue)
        self.last_state, self.last_action = state, action

    def select_action(self, state):
        sum = 0.0

        action_values = numpy.zeros(action.get_action_count(), dtype=float)
        for i in range(action.get_action_count()):
            qvalue = self._get_value(state, i)
            action_values[i] = exp(self.exploitation_rate * qvalue)

        sum = action_values.sum()

        if sum == 0.0:
            return self._get_best_action(state)
        
        action_values /= sum

        action = 0
        cum_prob = 0.0
        random_num = random.random()

        while random_num > cum_prob and action < action.get_action_count():
            cum_prod += action_values[action]
            action += 1

        return action - 1 if action > 1 else action

if __name__ == "__main__":
    rl = rl()
    print rl.table
    print rl.state_mapping
    print rl.state_mapping.sum(1)
    print rl.state_mapping.sum(2)
    print rl.state_mapping[2].argmax(),rl.state_mapping[2].max()
    print rl.state_mapping.argmax(2),rl.state_mapping.max(2)
    print rl.state_mapping.argmax(1),rl.state_mapping.max(1)
