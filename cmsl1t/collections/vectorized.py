from collections import defaultdict
import logging
import numba
import numpy as np
from rootpy.plotting import Hist

from . import BaseHistCollection
from ..utils.iterators import pairwise
from .. import PY3

logger = logging.getLogger(__name__)


@numba.jit(nopython=True)
def extend(arr1, starts, stops):
    repeat = stops - starts
    return np.repeat(arr1, repeat, axis=0)


class VectorizedHistCollection(BaseHistCollection):

    def __init__(self, innerBins, innerLabel='inner', **kwargs):
        # if we want to generalize to N dim, innerBins needs to be an array of innerBins
        dimensions = kwargs.pop('dimensions', 2)
        if PY3:
            super(VectorizedHistCollection, self).__init__(dimensions)
        else:
            BaseHistCollection.__init__(self, dimensions)

        self._innerBins = innerBins
        self._innerLabel = innerLabel
        self._innerHist = Hist(100, 0, 100, name='inner')

    def __getitem__(self, key):
        real_key = self._get_inner_indices(key)
        return defaultdict.__getitem__(self, real_key)

    def _get_inner_indices(self, values):
        '''
            Returns the pileup bin corresponding to the provided pileup value.
             - bin 0 is underflow
             - bin len(innerBins) is overflow

            :Example:
                >>> hists = VectorizedHistCollection(innerBins=[0,10,15,20,30,999])
                >>> hists._get_inner_indices([1, 11, 1111]) # returns [1, 2, 6]
        '''
        return np.digitize(values, self._innerBins)

    def add(self, name, bins, hist_type=Hist):

        bins = np.asarray(bins)
        if bins.size == 0:
            logger.error(
                'No bins specified for histogram {0}'.format(hist_name))

        if name in self[1]:
            logger.warning('Histogram {0} already exists!'.format(hist_name))
            return
        names = []
        add_name = names.append
        print(self)

        for i, (lowerEdge, upperEdge) in enumerate(pairwise(self._innerBins)):
            hist_name = f"{name}_{self._innerLabel}{lowerEdge}To{upperEdge}"
            if i + 1 not in self or hist_name not in self[i + 1]:
                add_name(hist_name)
                self[i + 1][hist_name] = Hist(bins, name=hist_name)
        logger.debug('Created {0} histograms: {1}'.format(
            len(names), ', '.join(names)))

    def fill(self):
        pass
