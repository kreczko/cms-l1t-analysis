import unittest
import numpy as np
from cmsl1t.playground.cache import CachedIndexedTree


class DummyTree(object):
    def __init__(self, size):
        self.pt = np.random.rand(size)
        self.eta = np.random.rand(size)
        self.size = size


class DummyEvent(object):
    def __init__(self):
        self._tree = CachedIndexedTree(DummyTree(3), 'size')

    @property
    def tree(self):
        return self._tree


class TestCachedIndexedTree(unittest.TestCase):

    def test_access(self):
        event = DummyEvent()
        self.assertEqual(event.tree[0].pt, event.tree.pt[0])

        for t in event.tree:
            print(t.pt)
