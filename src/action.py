'''
1 buy
2 sell
0 keep
'''

def get_action_count():
    return 3

def get_reinforcement(action, values):
    changes = values.get_changes()

    if changes < 0:
        if action == 2:
            return changes * -1
        else:
            return changes
    if changes > 0:
        if action == 1:
            return changes
        else:
            return changes * -1

    return changes