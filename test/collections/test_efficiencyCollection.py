from cmsl1t.collections import EfficiencyCollection
import unittest
import numpy as np


class TestResolutionCollection(unittest.TestCase):

    def test_add_variable(self):
        pileupBins = [0, 10, 15, 20, 30, 999]
        bins = np.concatenate((np.arange(20, 80, 10), np.arange(
            80, 120, 20), np.arange(120, 200, 40)))
        thresholds = [30, 50, 70, 100]
        hists = EfficiencyCollection(pileupBins=pileupBins)
        # this should create 1 entry for every pileup bin and every threshold

        hists.add_variable('jetEt', bins, thresholds)
        expected_len = (len(pileupBins) - 1) * len(thresholds)
        self.assertEqual(len(hists), expected_len)
