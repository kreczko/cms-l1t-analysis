from collections import defaultdict
import logging
import numba
import numpy as np
from rootpy.plotting import Hist

from . import BaseHistCollection
from ..utils.iterators import pairwise
from .. import PY3

logger = logging.getLogger(__name__)


def extend(arr1, starts, stops):
    repeat = stops - starts
    return np.repeat(arr1, repeat, axis=0)


class VectorizedHistCollection(BaseHistCollection):

    def __init__(self, innerBins, innerLabel='inner', **kwargs):
        # if we want to generalize to N dim, innerBins needs to be an array of innerBins
        # TODO: last dimension should probably be a normal dictionary
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
        return VectorizedBinProxy(self, real_keys)
        # return [defaultdict.__getitem__(self, k) for k in real_keys.tolist()]

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

        for i, hist_name in enumerate(self._create_hist_names(name)):
            if i + 1 not in self or hist_name not in defaultdict.__getitem__(self, i + 1):
                add_name(hist_name)
                defaultdict.__getitem__(self, i + 1)[hist_name] = Hist(bins, name=hist_name)
        logger.debug('Created {0} histograms: {1}'.format(
            len(names), ', '.join(names)))

    def _create_hist_names(self, name):
        for i, (lowerEdge, upperEdge) in enumerate(pairwise(self._innerBins)):
            yield f"{name}_{self._innerLabel}{lowerEdge}To{upperEdge}"

    def get_hist_name(self, name, innerIndex):
        lowerEdge, upperEdge = self._innerBins[innerIndex - 1], self._innerBins[innerIndex]
        return f"{name}_{self._innerLabel}{lowerEdge}To{upperEdge}"

    def fill(self, x, w=None):
        if w is None:
            w = np.ones()


class VectorizedBinProxy(object):

    def __init__(self, collection, inner_indices):
        self.collection = collection
        self._inner_indices = inner_indices
        # self._inner_values = inner_values

    def __getitem__(self, key):
        # TODO, if key != string, return a BinProxy of the bin above
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
        self._bin_proxy = bin_proxy
        self._hist_name = hist_name

    def _split_input(self, x, w):
        inner_indices = self._bin_proxy._inner_indices
        # TODO: what if x is not jagged
        inner_indices = extend(inner_indices, x.starts, x.stops)
        for u in np.unique(inner_indices):
            mask = inner_indices == u
            yield u, x.content[mask], w[mask]

    def _get_hist(self, inner_index):
        hist_name = self._bin_proxy.collection.get_hist_name(self._hist_name, inner_index)
        return defaultdict.__getitem__(self._bin_proxy.collection, inner_index)[hist_name]

    def fill(self, x, w=None):
        if w is None:
            # TODO: what if x is not jagged
            w = np.ones(len(x.content))
        for i, x_i, w_i in self._split_input(x, w):
            hist = self._get_hist(i)
            hist.fill_array(x_i, w_i)
