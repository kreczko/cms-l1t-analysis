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
        if not isinstance(key, (list, np.ndarray, np.generic)):
            key = np.array([key])
        real_keys = self._get_inner_indices(key)
        # Python tries to copy the whole nested default dict ... which is infinite
        # print(key, real_keys)
        # return object()
        return VectorizedBinProxy(self, real_keys)
        return [defaultdict.__getitem__(self, k) for k in real_keys.tolist()]

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

        if name in defaultdict.__getitem__(self, 1):
            logger.warning('Histogram {0} already exists!'.format(hist_name))
            return
        names = []
        add_name = names.append

        for i, (lowerEdge, upperEdge) in enumerate(pairwise(self._innerBins)):
            hist_name = f"{name}_{self._innerLabel}{lowerEdge}To{upperEdge}"
            if i + 1 not in self or hist_name not in defaultdict.__getitem__(self, i + 1):
                add_name(hist_name)
                defaultdict.__getitem__(self, i + 1)[hist_name] = Hist(bins, name=hist_name)
        logger.debug('Created {0} histograms: {1}'.format(
            len(names), ', '.join(names)))

    def fill(self, x, w=None):
        if w is None:
            w = np.ones()



class VectorizedBinProxy(object):

    def __init__(self, collection, inner_indices):
        self.collection = collection
        self._inner_indices = inner_indices

    def __getitem__(self, key):
        # TODO, if key != string, return a BinProxy
        return VectorizedHistProxy(self, key)

    def __add__(self, other):
        if self.collection != other.collection:
            msg = 'Cannot add VectorizedBinProxy for two different collections'
            logger.error(msg)
            raise ValueError(msg)
        self._inner_indices = np.append(self._inner_indices, other._inner_indices)
        return self

    def __eq__(self, other):
        if self.collection != other.collection:
            msg = 'Cannot compare VectorizedBinProxy for two different collections'
            logger.error(msg)
            raise ValueError(msg)
        return self._inner_indices.tolist() == other._inner_indices.tolist()

    def flatten(self):
        self._inner_indices = np.unique(self._inner_indices)
        return self

class VectorizedHistProxy(object):

    def __init__(self, bin_proxy, hist_name):
        self._bin_proxy = bin_proxy.flatten()
        self._hist_name = hist_name

    def fill(self, x, w=None):
        if w is None:
            w = np.ones(x)
