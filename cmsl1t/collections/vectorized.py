import awkward
from collections import defaultdict
import logging
import numpy as np
import random
from rootpy.plotting import Hist

from . import BaseHistCollection
from ..utils.iterators import pairwise
from ..io import to_root

logger = logging.getLogger(__name__)


def extend(arr1, starts, stops):
    repeat = stops - starts
    return np.repeat(arr1, repeat, axis=0)


def split_input(inner_indices, x, w):
    content = x
    if hasattr(x, 'starts'):
        inner_indices = extend(inner_indices, x.starts, x.stops)
        content = x.content

    for u in np.unique(inner_indices):
        mask = inner_indices == u
        if not isinstance(mask, (list, np.ndarray)):
            mask = np.array([mask])
        yield u, content[mask], w[mask]


class VectorizedHistCollection(BaseHistCollection):

    def __init__(self, innerBins, innerLabel='inner', **kwargs):
        # if we want to generalize to N dim, innerBins needs to be an array of innerBins
        # TODO: last dimension should probably be a normal dictionary
        dimensions = kwargs.pop('dimensions', 2)
        self._name = kwargs.pop('name', str(hex(random.getrandbits(128)))[2:10])
        self._execute_before_write = kwargs.pop('execute_before_write', [])
        super(VectorizedHistCollection, self).__init__(dimensions)

        self._innerBins = innerBins
        self._innerLabel = innerLabel
        self._innerHist = Hist(100, 0, 100, name=innerLabel + '_' + self._name)

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

    def add(self, name, bins, hist_type=Hist, **kwargs):
        title = kwargs.pop('title', name)
        bins = np.asarray(bins)
        if bins.size == 0:
            logger.error(
                'No bins specified for histogram {0}'.format(name))

        if name in defaultdict.__getitem__(self, 1):
            logger.warning('Histogram {0} already exists!'.format(name))
            return
        names = []
        add_name = names.append

        for i, hist_name in enumerate(self._create_hist_names(name)):
            if i + 1 not in self or hist_name not in defaultdict.__getitem__(self, i + 1):
                add_name(hist_name)
                defaultdict.__getitem__(self, i + 1)[hist_name] = hist_type(bins, name=hist_name, title=title)
        logger.debug('Created {0} histograms: {1}'.format(
            len(names), ', '.join(names)))

    def _create_hist_names(self, name):
        for lowerEdge, upperEdge in pairwise(self._innerBins):
            yield f"{name}_{self._innerLabel}{lowerEdge}To{upperEdge}"

    def get_hist_name(self, name, innerIndex):
        lowerEdge, upperEdge = self._innerBins[innerIndex - 1], self._innerBins[innerIndex]
        return f"{name}_{self._innerLabel}{lowerEdge}To{upperEdge}"

    def inner_fill(self, x, w=None):
        if w is None:
            w = np.ones(np.size(x))
        self._innerHist.fill_array(x, w)

    def to_root(self, output_file):
        for func in self._execute_before_write:
            func(self)
        to_root([self, self._innerHist], output_file)


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

    def _get_hist(self, inner_index):
        hist_name = self._bin_proxy.collection.get_hist_name(self._hist_name, inner_index)
        return defaultdict.__getitem__(self._bin_proxy.collection, inner_index)[hist_name]

    def fill(self, x, w=None):
        if not isinstance(x, (list, np.ndarray, awkward.JaggedArray)):
            x = np.array([x])
        if w is None:
            n = np.size(x.content) if hasattr(x, 'content') else np.size(x)
            w = np.ones(n)
        for i, x_i, w_i in split_input(self._bin_proxy._inner_indices, x, w):
            hist = self._get_hist(i)
            hist.fill_array(x_i, w_i)

# class VectorizedEfficiencyProxy(object):

# def split_input():
#     a = np.array([1, 12, 1, 10, 50, 10])
#     b = np.array([10, 20, 30, 40, 50, 60])
#     arg = a.argsort(kind='stable')
#     offsets, = np.where(np.r_[True, np.diff(a[arg]) > 0])
#     output = awkward.JaggedArray.fromoffsets(offsets.flatten(), awkward.IndexedArray(arg, b))
