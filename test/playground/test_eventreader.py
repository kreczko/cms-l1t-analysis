import unittest
from cmsl1t.playground.eventreader import get_trees


class TestEventReader(unittest.TestCase):

    def test_get_trees(self):
        load_emu = False
        load_reco = False
        load_vertex = False
        load_gen = False

        trees = get_trees(load_emu, load_reco, load_vertex, load_gen).values()
        self.assertTrue(len(trees) > 0)
        for name in trees:
            self.assertTrue('emu' not in name)
            self.assertTrue('Emu' not in name)
            self.assertTrue('reco' not in name)
            self.assertTrue('Reco' not in name)
            self.assertTrue('gen' not in name)

        load_emu = True
        trees = get_trees(load_emu, load_reco, load_vertex, load_gen).values()
        self.assertTrue(len(trees) > 0)
        emu_trees = 0
        for name in trees:
            if 'emu' in name or 'Emu' in name:
                emu_trees += 1
            self.assertTrue('reco' not in name)
            self.assertTrue('Reco' not in name)
            self.assertTrue('gen' not in name)
        self.assertTrue(emu_trees > 0)

        load_reco = True
        emu_trees = 0
        reco_trees = 0
        trees = get_trees(load_emu, load_reco, load_vertex, load_gen).values()
        self.assertTrue(len(trees) > 0)
        for name in trees:
            if 'emu' in name or 'Emu' in name:
                emu_trees += 1
            if 'reco' in name or 'Reco' in name:
                reco_trees += 1
            self.assertTrue('gen' not in name)
        self.assertTrue(emu_trees > 0)
        self.assertTrue(reco_trees > 0)

        load_reco = True
        load_vertex = True
        emu_trees = 0
        reco_trees = 0
        trees = get_trees(load_emu, load_reco, load_vertex, load_gen).values()
        self.assertTrue(len(trees) > 0)
        for name in trees:
            if 'emu' in name or 'Emu' in name:
                emu_trees += 1
            if 'reco' in name or 'Reco' in name:
                reco_trees += 1
            self.assertTrue('gen' not in name)
        self.assertTrue(emu_trees > 0)
        self.assertTrue(reco_trees > 0)

        load_gen = True
        emu_trees = 0
        reco_trees = 0
        gen_trees = 0
        trees = get_trees(load_emu, load_reco, load_vertex, load_gen).values()
        self.assertTrue(len(trees) > 0)
        for name in trees:
            if 'emu' in name or 'Emu' in name:
                emu_trees += 1
            if 'reco' in name or 'Reco' in name:
                reco_trees += 1
            if 'gen' in name or 'Gen' in name:
                gen_trees += 1
        self.assertTrue(emu_trees > 0)
        self.assertTrue(reco_trees > 0)
        self.assertTrue(gen_trees > 0)
