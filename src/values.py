import os
import sys
import logging

class Values(object):
    def __init__(self, *args):
        self._close, self._dif, self._dea, self._close_change, self._dif_change, self._dea_change = args

    def get_dif(self):
        return self._dif

    def get_dea(self):
        return self._dea

    def get_dif_changes(self):
        return self._dif_change

    def get_dea_changes(self):
        return self._dea_change
    
    def get_changes(self):
        return self._close_change
