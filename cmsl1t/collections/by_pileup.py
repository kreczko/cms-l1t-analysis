import numpy as np
import logging
from collections import defaultdict

from cmsl1t.utils.iterators import pairwise
from cmsl1t.io import to_root
from . import BaseHistCollection

logger = logging.getLogger(__name__)
# TODO: inherit from BinnedHistogramCollection


class HistogramsByPileUpCollection(BaseHistCollection):
    '''
        Specialisation of BaseHistCollection to bin histograms by pileup

        :Example:
            >>> hists = HistogramsByPileUp(pileupBins=[0,10,15,20,30,999])
            >>> pileup=11
            >>> # translates pileup=11 to 2nd pileup bin
            >>> hists[pileup] = Hist(bins=np.arange(-1, 1.5, 0.05))
    '''

    def __init__(self, pileupBins, dimensions=1, initialValue=0):
        from rootpy.plotting import Hist
        BaseHistCollection.__init__(self, dimensions, initialValue)
        self._pileupBins = pileupBins
        self._pileupHist = Hist(100, 0, 100, name='nVertex')

    def add(self, hist_name, bins=[]):
        from rootpy.plotting import Hist
        '''
            Specialisation for 2 dimensions
            TODO: generalise
        '''
        bins = np.array(bins)
        if bins.size == 0:
            logger.error(
                'No bins specified for histogram {0}'.format(hist_name))

        if hist_name in self[self._pileupBins[0]].keys():
            logger.warning('Histogram {0} already exists!'.format(hist_name))
            return
        hist_names = []
        add_name = hist_names.append

        for puBinLower, puBinUpper in pairwise(self._pileupBins):
            name = '{0}_pu{1}To{2}'.format(
                hist_name, puBinLower, puBinUpper)
            if not self[puBinLower] or not self[puBinLower][hist_name]:
                add_name(name)
                self[puBinLower][hist_name] = Hist(bins, name=name)
        logger.debug('Created {0} histograms: {1}'.format(
            len(hist_names), ', '.join(hist_names)))

    def set_pileup(self, pileUp):
        self._pileUp = pileUp
        if np.size(pileUp) > 1:
            self._pileupHist.fill_array(pileUp)
        else:
            self._pileupHist.fill(pileUp)

    def fill(self, hist_name, x, w=1.0):
        h = self[self._pileUp][hist_name]
        if not h:
            msg = 'Histogram {0} does not exist'.format(hist_name)
            logger.error(msg)
            raise NameError(msg)

        h.fill(x, w)

    def _get_pu_bin(self, pileup):
        '''
            Returns the pileup bin corresponding to the provided pileup value.

            :Example:
                >>> hists = HistogramsByPileUp(pileupBins=[0,10,15,20,30,999])
                >>> hists._get_pu_bin(1) # returns 0
                >>> hists._get_pu_bin(11) # returns 1
                >>> hists._get_pu_bin(1111) # returns -1
        '''
        if pileup > max(self._pileupBins):
            return -1

        bins = pairwise(self._pileupBins)
        for i, (lowerEdge, upperEdge) in enumerate(bins):
            if pileup >= lowerEdge and pileup < upperEdge:
                return i
        return 0

    def __getitem__(self, key):
        real_key = self._get_pu_bin(key)
        return defaultdict.__getitem__(self, real_key)

    def summarise(self):
        '''
            Sums histograms across PU bins
        '''
        raise NotImplementedError

    def to_root(self, output_file):
        '''
            Saves the instance into a ROOT file
        '''
        # need to add pileupHist manually
        to_root([self, self._pileupHist], output_file)

    @staticmethod
    def from_root(input_file):
        from rootpy.io.pickler import load
        instance, pileupHist = load(input_file)
        instance._pileupHist = pileupHist
        return instance
