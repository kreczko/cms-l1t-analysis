import numbda

from . import BaseHistCollection


@numba.jit(nopython=True)
def extend(arr1, starts, stops):
    repeat = stops - starts
    return np.repeat(arr1, repeat, axis=0)


class VectorizedHistCollection(object):

    def __init__(self, innerBins):
        self._innerBins = innerBins
        self._innerHist = Hist(100, 0, 100, name='inner')

    def _get_inner_indices(self, values):
        '''
            Returns the pileup bin corresponding to the provided pileup value.
             - bin 0 is underflow
             - bin len(innerBins) is overflow

            :Example:
                >>> hists = VectorizedHistCollection(innerBins=[0,10,15,20,30,999])
                >>> hists._get_inner_indices([1, 11, 1111]) # returns [0, 1, 5]
        '''
        return np.digitize(values, self._innerBins)
