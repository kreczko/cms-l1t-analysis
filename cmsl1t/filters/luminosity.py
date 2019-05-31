import json
import six
import six.moves.urllib as urllib
import numba
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
        # TODO: wrong way around!
        # need to create a new array from the event.run and event.lumi
        # https://stackoverflow.com/questions/35091879/merge-2-arrays-vertical-to-tuple-numpy
        # https://docs.scipy.org/doc/numpy/reference/generated/numpy.isin.html
        to_test = np.array(list(zip(event.run, event.lumi)))
        # print(np.size(to_test), np.size(self.valid_lumi_sections))
        # print(self.valid_lumi_sections)
        # mask = np.isin(self.valid_lumi_sections, to_test, assume_unique=True)
        mask = filter_lumis(to_test, self.valid_lumi_sections)
        print('Lumi filter', to_test, mask, '({})'.format(np.size(mask)))
        return mask


@numba.jit(nopython=True, parallel=True)
def filter_lumis(ranges_to_test, valid_lumi_sections):
    result = np.zeros(ranges_to_test.shape[0], dtype=np.uint8)
    for i in range(valid_lumi_sections.shape[0]):
        valid_section = valid_lumi_sections[i, :]
        for j in range(ranges_to_test.shape[0]):
            to_test = ranges_to_test[j, :]
            if np.equal(to_test, valid_section).all():
                result[j] = 1
    return result
