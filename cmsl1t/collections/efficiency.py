"""
    .. module:: collections.efficiency
       :synopsis: Module for creating efficiency(turnon)-curves
"""
import numpy as np

from . import HistogramsByPileUpCollection

from cmsl1t.utils.iterators import pairwise
import logging

logger = logging.getLogger(__name__)


class _EfficiencyCurve(object):

    def __init__(self, name, bins, threshold):
        from rootpy.plotting import Hist
        self._pass = Hist(bins, name=name + '_pass')
        self._total = Hist(bins, name=name + '_total')
        self._dist = Hist(bins, name=name + '_dist')
        self._threshold = threshold
        self._efficiency = None

    def fill(self, recoValue, l1Value, weight=1.):
        """ Fills the histograms used for efficiency calculation
        :param recoValue: the reconstructed quanity
        :type recoValue: float
        :param l1Value: the L1 Trigger quantity
        :type l1Value: float
        :param weight: weight to fill the histograms with, default=1.0
        :type weight: float
        """
        self._total.fill(recoValue, weight)
        self._dist.fill(l1Value, weight)
        if l1Value > self._threshold:
            self._pass.fill(recoValue, weight)

    def fill_array(self, recoValue, l1Value, weight=None):
        """ Fills the histograms used for efficiency calculation
        :param recoValue: the reconstructed quanity
        :type recoValue: array of floats
        :param l1Value: the L1 Trigger quantity
        :type l1Value: array of floats
        :param weight: weight to fill the histograms with, default=1.0
        :type weight: array of floats
        """
        if weight is None:
            weight = np.ones(np.size(recoValue))
        self._total.fill_array(recoValue, weight)
        self._dist.fill_array(l1Value, weight)
        self._pass.fill_array(recoValue[l1Value > self._threshold], weight[l1Value > self._threshold])

    def calculate_efficiency(self):
        from rootpy import asrootpy
        from ROOT import TEfficiency
        self._efficiency = asrootpy(TEfficiency(self._pass, self._total))
        self._efficiency.SetName(self._total.GetName() + '_eff')

    def get_efficiency(self):
        if not self._efficiency:
            self.calculate_efficiency()
        return self._efficiency


class EfficiencyCollection(HistogramsByPileUpCollection):
    '''
        The EfficiencyCollection allows for easy creation and access to turon-on
        curves (efficiency curves). For each variable it stores (for each
        pileup bin) 3 objects:
         - the true distribution
         - the observed distribution
         - their ratio (efficiency)

        The EfficiencyCollection is a 3D collection of histogram name, pileUp and
        thresholds:
        >>> histograms = EfficiencyCollection(pileUpBins=0, 13, 20, 999])
        >>> histograms.add_variable('JetPt', thresholds = [30, 50, 70, 100])
        >>> histograms.set_pileup(pileUp)
        >>> histograms.fill('JetPt', jetPtReco, jetPtL1)

    '''

    def __init__(self, pileupBins=[0, 13, 20, 999]):
        self._dimensions = 3
        self._thresholds = {}
        HistogramsByPileUpCollection.__init__(
            self, pileupBins=pileupBins, dimensions=self._dimensions)
        self._pileUp = 0
        self._pileUpBins = pileupBins

    def add_variable(self, variable, bins, thresholds):
        """ This function adds a variable to be tracked by this collection.
        :param variable: The variable name
        :type name: str.
        :param bins: The bins to be used for the variable
        :type bins: list.
        :param thresholds: A list of thresholds for L1 values
        :type thresholds: list.
        """
        # TODO: this will no longer work since 1st dimension is pileup
        if variable in self.keys():
            logger.warn('Variable {0} already exists!')
            return
        self._thresholds[variable] = thresholds
        hist_names = []
        add_name = hist_names.append

        for puBinLower, puBinUpper in pairwise(self._pileUpBins):
            for threshold in thresholds:
                name = '{0}_threshold_gt{1}_pu{2}To{3}'.format(
                    variable, threshold, puBinLower, puBinUpper)
                if not self[puBinLower][variable][threshold]:
                    add_name(name)
                    self[puBinLower][variable][
                        threshold] = _EfficiencyCurve(name, bins, threshold)
        logger.debug('Created {0} histograms: {1}'.format(
            len(hist_names), ', '.join(hist_names)))

    def fill(self, hist_name, recoValue, l1Value, w=1.0):
        h = self[self._pileUp][hist_name]
        if not h:
            logger.error('Histogram {0} does not exist'.format(hist_name))
            return
        if hist_name not in self._thresholds:
            logger.warn('No valid current thresholds.')
        for threshold in self._thresholds[hist_name]:
            h[threshold].fill(recoValue, l1Value, w)

    def fill_array(self, hist_name, recoValue, l1Value, w=None):
        if w is None:
            w = np.ones(np.size(recoValue))
        # TODO: proper indexing for vectorized input
        h = self[-1][hist_name]
        if not h:
            logger.error('Histogram {0} does not exist'.format(hist_name))
            return
        if hist_name not in self._thresholds:
            logger.warn('No valid current thresholds.')
        for threshold in self._thresholds[hist_name]:
            h[threshold].fill_array(recoValue, l1Value, w)

    def _calculateEfficiencies(self):
        for puBinLower, _ in pairwise(self._pileUpBins):
            for hist in self[puBinLower].keys():
                for threshold in self._thresholds[hist]:
                    self[puBinLower][hist][threshold].calculate_efficiency()

    def to_root(self, output_file):
        self._calculateEfficiencies()
        HistogramsByPileUpCollection.to_root(self, output_file)
