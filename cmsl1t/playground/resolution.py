'''
    To replicate the container behaviour of TL1Resolution
    but without the plotting elements.
    Stores itself into a ROOT file.
'''
import logging
import numpy as np
from rootpy.plotting import Hist
import cmsl1t.geometry as geo

logger = logging.getLogger(__name__)


class Resolution(object):
    BINS = {
        'position': np.arange(-0.3, 0.3, 0.005),
        'energy': np.arange(-1, 1.5, 0.05),
    }

    def __init__(self):
        self._hists = {}

    def save(self, output_file):
        '''
            Saves the instance into a ROOT file
        '''
        from rootpy.io.pickler import dump
        if not output_file.endswith('.root'):
            output_file += '.root'
        dump(self._hists, output_file)

    def add_hist_set(self, prefix, regions=geo.eta_regions, bins=[]):
        if not bins:
            bins = Resolution.BINS['position']

        for region in regions:
            name = prefix + region
            if name in self._hists:
                logger.warning('Overwriting existing histogram {0}'.format(name))
                del self._hists[name]
            logger.debug('Adding histogram {0}'.format(name))
            self._hists[name] = Hist(bins, name=name)

    def fill(self, prefix, x, pileUp=0):
        pass

    def __getitem__(self, key):
        return self._hists[key]
