import json
import six
import six.moves.urllib as urllib
import numpy as np

from .. import logger
from ..math import isin_nd


def _load_json(lumi_json):
    input_file = lumi_json
    is_remote = input_file.startswith('http')
    has_local_prefix = input_file.startswith('file://')
    if not is_remote and not has_local_prefix:
        input_file = 'file://' + input_file
    logger.debug('Loading file {} for LuminosityFilter'.format(input_file))
    input_stream = urllib.request.urlopen(input_file)
    data = json.load(input_stream)
    return data


def _expand_lumi_range(lumi_range):
    '''
        Expands lumi range `[1,4]` to `[1,2,3,4]`
    '''
    start, end = lumi_range
    return np.arange(start, end + 1, dtype=np.dtype('>i4'))


def _expand_lumi_ranges(lumi_ranges):
    '''
        Expands `[[1,4], [10,12]` to `[1,2,3,4,10,11,12]`
    '''
    result = list(map(_expand_lumi_range, lumi_ranges))
    return np.concatenate(result).ravel()


class LuminosityFilter(object):

    def __init__(self, lumi_json):
        data = _load_json(lumi_json)
        self.valid_lumi_sections = []
        for run, lumi_ranges in six.iteritems(data):
            lumis = _expand_lumi_ranges(lumi_ranges)
            tuples = map(lambda x: (int(run), x), lumis)
            self.valid_lumi_sections.extend(tuples)
        self.valid_lumi_sections = np.array(self.valid_lumi_sections)

    def __call__(self, event):
        to_test = np.array(list(zip(event.run, event.lumi)))
        mask = isin_nd(to_test, self.valid_lumi_sections)
        return mask
