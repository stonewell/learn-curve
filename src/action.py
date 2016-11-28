'''
1 buy
2 sell
0 keep
'''

class DefaultAction(object):
    def get_action_count(self):
        return 3

    def get_reinforcement(self, action, values):
        changes = values.get_changes()

        if action == 2:
            return changes * -1
        else:
            return changes
