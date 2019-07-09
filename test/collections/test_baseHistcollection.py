from collections import defaultdict
import pytest
import unittest

from cmsl1t.collections import BaseHistCollection


class TestBaseHistCollection(unittest.TestCase):

    def test_dimensions(self):
        dimensions = 4
        initial_value = 0
        hists = BaseHistCollection(dimensions, initial_value)
        self.assertEqual(len(hists), 0)
        self.assertIs(type(hists[1]), defaultdict)
        self.assertIs(type(hists[1][2][3][4]), type(initial_value))
        self.assertEqual(hists[1][2][3][4], initial_value)
        hists['a']['b']['c']['d'] = 5
        self.assertEqual(hists['a']['b']['c']['d'], 5)
        # access to hists[1][2][3][4] create 1 entry
        # access to hists['a']['b']['c']['d'] creates 1 entry
        self.assertEqual(len(hists), 2)
        # for multi-dim bug
        hists['a']['b']['c']['e'] = 42
        self.assertEqual(len(hists), 3)

        # length_from_iterator = len(list(six.itervalues(hists)))
        # self.assertEqual(length_from_iterator, 3)


@pytest.mark.parametrize("dimensions", [1, 2, 3])
def test_empty(dimensions):
    c = BaseHistCollection(dimensions)
    assert len(c) == 0
