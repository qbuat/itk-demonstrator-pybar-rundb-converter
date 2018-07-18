from .converter import *


ALL_FEBS = [
        "JP1_1",
        "JP1_2",
        "JP1_3",
        "JP1_4",
        "JP2_1",
        "JP2_2",
        "JP2_3",
        "JP2_4",
        "JP3_1",
        "JP3_2",
        "JP3_3",
        "JP3_4",
        "JP4_1",
        "JP4_2",
        "JP4_3",
        "JP4_4",
        "KEK122_1",
        "KEK122_2",
        "KEK123_1",
        "KEK123_2",
        "KEK123_3",
        "KEK123_4",
        "QSI18_3",
        "QSI18_4",
        ]

class pybar_run(object):
    def __init__(self, number, run_type='init', febs=ALL_FEBS):
        self._number = number
        self._run_type = run_type
        self._febs = febs

    @property
    def run_number(self):
        return self._number

    @property
    def run_type(self):
        return self._run_type

    @property
    def febs(self):
        return self._febs

    @property
    def name(self):
        return 'run_{}_{}'.format(self._number, self._run_type)
