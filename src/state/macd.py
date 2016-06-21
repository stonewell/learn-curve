'''
0: DIF > 0 < 0 = 0
1: DEA > 0 < 0 = 0
2: DIF > DEA, DIF < DEA, DIF = DEA
'''

def get_states_demension():
    return (3, 3, 3)

def get_states(values):
    dif = values.get_dif()
    dea = values.get_dea()
    
    s_dif = 0 if dif > 0 else 1 if dif < 0 else 2
    s_dea = 0 if dea > 0 else 1 if dea < 0 else 2
    s_dif_dea = 0 if dif > dea else 1 if dif < dea else 2
    
    return (s_dif, s_dea, s_dif_dea)
