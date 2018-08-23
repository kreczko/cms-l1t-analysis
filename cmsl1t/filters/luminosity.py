import json
import six
import six.moves.urllib as urllib
import numpy as np


def _load_json(lumi_json):
    input_file = lumi_json
    is_remote = input_file.startswith('http')
    has_local_prefix = input_file.startswith('file://')
    if not is_remote and not has_local_prefix:
        input_file = 'file://' + input_file
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
    result = np.array(map(_expand_lumi_range, lumi_ranges))
    return np.concatenate(result).ravel()


class LuminosityFilter(object):

    def __init__(self, lumi_json):
        data = _load_json(lumi_json)
        self.valid_lumi_sections = []
        for run, lumi_ranges in six.iteritems(data):
            lumis = _expand_lumi_ranges(lumi_ranges)
            tuples = map(lambda x: (int(run), x), lumis)
            self.valid_lumi_sections.extend(tuples)
        self.valid_lumi_sections = set(self.valid_lumi_sections)

    def __call__(self, run, lumi):
        return (run, lumi) in self.valid_lumi_sections
