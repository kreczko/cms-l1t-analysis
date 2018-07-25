"""
Tracks values for particular event variables
To be used as
    - cmsl1t.analyzers.inspector:
      inputs:
       - var1
       - var2

where var* is an attribute of an event (e.g. 'run').
If attributes of objects need to be accessed, simply use the '.' notation, e.g. "l1Sums_Htt.et"

"""
from BaseAnalyzer import BaseAnalyzer
import numpy as np
import os


class Analyzer(BaseAnalyzer):

    def __init__(self, **kwargs):
        super(Analyzer, self).__init__(**kwargs)
        self._inputs = []
        self._inputs = self.params['inputs']
        self._map = {}
        for i in self._inputs:
            self._map[i] = []

    def prepare_for_events(self, reader):
        return True

    def reload_histograms(self, input_file):
        return True

    def fill_histograms(self, entry, event):
        for i in self._inputs:
            value = None
            if '.' in i:
                var, attr = i.split('.')
                value = getattr(event[var], attr)
            else:
                value = event[i]
            self._map[i].append(value)
        return True

    def write_histograms(self):
        out_dir = self.output_folder
        for key, value in self._map.items():
            out_file = os.path.join(out_dir, key)
            data = np.asarray(value)
            np.save(out_file, data)
        return True

    def make_plots(self):
        return True
