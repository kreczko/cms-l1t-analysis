from __future__ import print_function
from rootpy.tree import TreeChain
import six
import os
import math

from cmsl1t.playground.jetfilters import pfJetFilter
from metfilters import pfMetFilter
from cmsl1t.playground.cache import CachedIndexedTree
from cmsl1t.utils import load_ROOT_library
from cmsl1t.energySums import EnergySum, Mex, Mey, Met
from rootpy import ROOT
from exceptions import RuntimeError
import logging
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.environ.get('PROJECT_ROOT', os.getcwd())
EXTERNAL_PATH = os.path.join(PROJECT_ROOT, 'external')
ROOT.gROOT.ProcessLine('.include {0}'.format(EXTERNAL_PATH))

ALL_TREE = {
    "caloTowers": 'l1CaloTowerTree/L1CaloTowerTree',
    "emuCaloTowers": 'l1CaloTowerEmuTree/L1CaloTowerTree',
    "event": 'l1EventTree/L1EventTree',
    "jetReco": 'l1JetRecoTree/JetRecoTree',
    "metFilterReco": 'l1MetFilterRecoTree/MetFilterRecoTree',
    "muonReco": 'l1MuonRecoTree/Muon2RecoTree',
    "recoTree": 'l1RecoTree/RecoTree',
    "upgrade": 'l1UpgradeTree/L1UpgradeTree',
    "emuUpgrade": 'l1UpgradeEmuTree/L1UpgradeTree',
    "genTree": 'l1GeneratorTree/L1GenTree'
}


def get_trees(load_emu_trees, load_reco_trees, load_vertex_trees, load_gen_trees):
    selected_trees = ['event', 'upgrade']
    if load_emu_trees:
        selected_trees.extend(['emuCaloTowers', 'emuUpgrade'])
    if load_reco_trees:
        selected_trees.extend(['jetReco', 'metFilterReco', 'recoTree'])
    if load_vertex_trees and not load_reco_trees:
        selected_trees.extend(['recoTree'])
    if load_gen_trees:
        selected_trees.extend(['genTree'])
    trees = {}
    for name in selected_trees:
        trees[name] = ALL_TREE[name]
    return trees


def _energySumTypes():
    load_ROOT_library('L1TAnalysisDataformats.so')
    sumTypes = ROOT.l1t.EtSum
    energySumLookup = {
        sumTypes.kTotalEt: {'name': 'Ett', 'type': EnergySum},
        sumTypes.kTotalEtHF: {'name': 'EttHF', 'type': EnergySum},
        sumTypes.kTotalHt: {'name': 'Htt', 'type': EnergySum},
        sumTypes.kTotalHtHF: {'name': 'HttHF', 'type': Met},
        sumTypes.kMissingEt: {'name': 'Met', 'type': Met},
        sumTypes.kMissingEtHF: {'name': 'MetHF', 'type': Met},
        sumTypes.kMissingHt: {'name': 'Mht', 'type': Met},
        sumTypes.kTotalEtx: {'name': 'Mex', 'type': Mex},
        sumTypes.kTotalEty: {'name': 'Mey', 'type': Mey},
    }
    return energySumLookup


class Event(object):

    def __init__(self, tree_names, trees):
        self._trees = trees
        for name, tree in zip(tree_names, trees):
            setattr(self, "_" + name, tree)
        self._l1Sums = {}

        if 'event' in tree_names:
            self._run = self._event.Event.run
            self._lumi = self._event.Event.lumi
        else:
            self._run, self._lumi = 0, 0

        if "caloTowers" in tree_names:
            self._caloTowers = CachedIndexedTree(
                self._caloTowers.L1CaloTower, 'nTower')

        if "emuCaloTowers" in tree_names:
            self._emuCaloTowers = CachedIndexedTree(
                self._emuCaloTowers.L1CaloTower, 'nTower')

        if "muonReco" in tree_names:
            self.muons = CachedIndexedTree(
                self._muonReco.Muon, 'nMuons'
            )

        if "upgrade" in tree_names:
            self._upgrade = self._upgrade.L1Upgrade
            self._l1Jets = [L1Jet(self._upgrade, i)
                            for i in range(self._upgrade.nJets)
                            if self._upgrade.jetBx[i] == 0]
            self._readUpgradeSums()

        if "emuUpgrade" in tree_names:
            self._emuUpgrade = self._emuUpgrade.L1Upgrade
            self._l1EmuJets = [L1Jet(self._emuUpgrade, i)
                               for i in range(self._emuUpgrade.nJets)
                               if self._emuUpgrade.jetBx[i] == 0]
            self._readEmuUpgradeSums()

        if "jetReco" in tree_names:
            self._jets = []
            for i in range(self._jetReco.Jet.nJets):
                self._jets.append(Jet(self._jetReco.Jet, i))
            self._caloJets = []
            for i in range(self._jetReco.Jet.nCaloJets):
                self._caloJets.append(CaloJet(self._jetReco.Jet, i))

    def _readUpgradeSums(self):
        self._readSums(self._upgrade, prefix='L1')

    def _readEmuUpgradeSums(self):
        self._readSums(self._emuUpgrade, prefix='L1Emu')

    def _readSums(self, tree, prefix='L1'):
        sums = {}
        for i in range(tree.nSums):
            bx = tree.sumBx[i]
            if bx != 0:
                continue

            sumType = tree.sumType[i]
            et = tree.sumEt[i]
            phi = tree.sumPhi[i]
            energySumTypes = _energySumTypes()
            if sumType in energySumTypes:
                name = energySumTypes[sumType]['name']
                obj = energySumTypes[sumType]['type']
                if obj == Met:
                    sums[prefix + name] = obj(et, phi)
                else:
                    sums[prefix + name] = obj(et)
        self._l1Sums.update(sums)

    def test(self):
        # for tree in self._trees:
        #     print(tree)
        print('>>>> nHCALTP', self._caloTowers.CaloTP.nHCALTP)
        print('>>>> nHCALTP (emu)', self._emuCaloTowers.CaloTP.nHCALTP)
        print('>>>> nJets', self._jetReco.Jet.nJets)
        print('>>>> met', self._jetReco.Sums.met)
        print('>>>> metFilter', pfMetFilter(self))
        print('>>>> nMuons', self._muonReco.Muon.nMuons)
        print('>>>> nVtx', self._recoTree.Vertex.nVtx)
        print('>>>> nJets (upgrade)', self._upgrade.nJets)
        print('>>>> nJets (upgrade emu)', self._emuUpgrade.nJets)
        print('>>>> nSums (upgrade)', self._upgrade.nSums)
        print('>>>> nSums (upgrade emu)', self._emuUpgrade.nSums)
        print('>>>> L1 energy sums:')
        for name, value in six.iteritems(self.l1Sums):
            print('>>>>>>>> {0} = {1}'.format(name, value))
        print(self._jets[0].eta)
        leadingJet = self.getLeadingRecoJet()
        if leadingJet:
            print('>>>> Leading reco jet ET', leadingJet.etCorr)
        goodJets = self.goodJets()
        if goodJets:
            print('>>>> Lowest good jet ET', goodJets[-1].etCorr)

        # print(dir(self._jetReco.Jet))
        # members = inspect.getmembers(self._jetReco.Jet)
        # print('>>>> Jet members')
        # for m in members:
        #     print('>' * 6, m[0], ':', m[1])

    def goodJets(self, jetFilter=pfJetFilter, doCalo=False):
        '''
            filters and ET orders the jet collection
        '''
        goodJets = None
        if doCalo:
            goodJets = filter(jetFilter, self._caloJets)
        else:
            goodJets = filter(jetFilter, self._jets)
        sorted_jets = sorted(
            goodJets, key=lambda jet: jet.etCorr, reverse=True)
        return sorted_jets

    def getLeadingRecoJet(self, jetFilter=pfJetFilter, doCalo=False):
        goodJets = self.goodJets(jetFilter, doCalo)
        if not goodJets:
            return None
        leadingRecoJet = goodJets[0]
        if leadingRecoJet.etCorr > 20.0:
            return leadingRecoJet
        return None

    def getMatchedL1Jet(self, recoJet, l1Type='HW'):
        l1Jets = None
        if l1Type == 'HW':
            l1Jets = self._l1Jets
        if l1Type == 'EMU':
            l1Jets = self._l1EmuJets

        if not recoJet:
            return None
        minDeltaR = 0.4
        closestJet = None
        for l1Jet in l1Jets:
            dEta = recoJet.eta - l1Jet.eta
            dPhi = recoJet.phi - l1Jet.phi
            dR = math.sqrt(dEta**2 + dPhi**2)
            if dR < minDeltaR:
                minDeltaR = dR
                closestJet = l1Jet
        return closestJet

    @property
    def nVertex(self):
        return self._recoTree.Vertex.nVtx

    @property
    def caloTowers(self):
        return self._caloTowers

    @property
    def emuCaloTowers(self):
        return self._emuCaloTowers

    @property
    def sums(self):
        return self._jetReco.Sums

    @property
    def l1Sums(self):
        return self._l1Sums


class Jet(object):
    '''
        Create a simple python wrapper for
        L1Analysis::L1AnalysisRecoJetDataFormat
    '''

    def __init__(self, jets, index):
        # this could be simplified with a list of attributes
        read_attributes = [
            'etCorr', 'muMult', 'eta', 'phi', 'nhef', 'pef', 'mef', 'chMult', 'elMult',
            'nhMult', 'phMult', 'chef', 'eef', 'nemef', 'cMult', 'nMult', 'cemef'
        ]
        for attr in read_attributes:
            setattr(self, attr, getattr(jets, attr)[index])


class CaloJet(object):
    '''
        Create a simple python wrapper for
        L1Analysis::L1AnalysisRecoJetDataFormat
    '''

    def __init__(self, jets, index):
        # this could be simplified with a list of attributes
        read_attributes = dict(
            et='caloEt',
            etCorr='caloEtCorr',
            eta='caloEta',
            phi='caloPhi',
        )
        for outattr, attr in read_attributes.items():
            setattr(self, outattr, getattr(jets, attr)[index])


class L1Jet(object):

    def __init__(self, l1Jets, index):
        self.et = l1Jets.jetEt[index]
        self.eta = l1Jets.jetEta[index]
        self.phi = l1Jets.jetPhi[index]
        self.bx = l1Jets.jetBx[index]


class EventReader(object):
    '''
        There are many ways to tune the reader:
        http://rootpy-log.readthedocs.io/en/latest/_modules/rootpy/tree/chain.html
    '''

    def __init__(self, files, events=-1,
                 load_emu_trees=False, load_reco_trees=True, load_vertex_trees=False, load_gen_trees=False):
        from cmsl1t.utils.root_glob import glob
        input_files = []
        for f in files:
            if '*' in f:
                input_files.extend(glob(f))
            else:
                input_files.append(f)
        # this is not efficient
        self._trees = []
        self._names = []
        load_ROOT_library('L1TAnalysisDataformats.so')
        allTrees = get_trees(load_emu_trees, load_reco_trees, load_vertex_trees, load_gen_trees)
        for name, path in allTrees.iteritems():
            try:
                chain = TreeChain(path, input_files, cache=True, events=events)
            except RuntimeError:
                logger.warn("Cannot find tree: {0} in input file".format(path))
                continue
            self._names.append(name)
            self._trees.append(chain)

    def __iter__(self):
        for trees in six.moves.zip(*self._trees):
            yield Event(self._names, trees)


if __name__ == '__main__':
    import glob
    # import ROOT
    # ROOT.gSystem.Load('build/L1TAnalysisDataformats.so')
    files = glob.glob('data/*.root')

    reader = EventReader(files)
    i = 1
    for event in reader:
        print('-' * 80)
        print('>> event', i)
        event.test()
        print('-' * 80)
        i += 1
        if i > 3:
            break
