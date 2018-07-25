from cmsl1t.recalc.met import l1MetNot28HF, l1MetNot28
from cmsl1t.utils.module import load_L1TNTupleLibrary
from cmsl1t.playground.jetfilters import pfJetFilter

load_L1TNTupleLibrary()


class EventMap(object):

    def __init__(self, event):
        self.event = event
        self._cache = {}
        self._map = {
            'Vertex_nVtx': lambda ev: ev.nRecoVertex,
            'MetFilters_badChCandFilter': lambda ev: ev._metFilterReco.MetFilters.badChCandFilter,
            'MetFilters_badPFMuonFilter': lambda ev: ev._metFilterReco.MetFilters.badPFMuonFilter,
            'MetFilters_ecalDeadCellTPFilter': lambda ev: ev._metFilterReco.MetFilters.ecalDeadCellTPFilter,
            'MetFilters_eeBadScFilter': lambda ev: ev._metFilterReco.MetFilters.eeBadScFilter,
            'MetFilters_goodVerticesFilter': lambda ev: ev._metFilterReco.MetFilters.goodVerticesFilter,
            'MetFilters_globalSuperTightHalo2016Filter':
            lambda ev: ev._metFilterReco.MetFilters.globalSuperTightHalo2016Filter,
            'MetFilters_hbheNoiseFilter': lambda ev: ev._metFilterReco.MetFilters.hbheNoiseFilter,
            'MetFilters_hbheNoiseIsoFilter': lambda ev: ev._metFilterReco.MetFilters.hbheNoiseIsoFilter,
            'Sums_caloMetBE': lambda ev: ev.sums.caloMetBE,
            'l1MetNot28HF': lambda ev: l1MetNot28HF(ev.caloTowers),
            'l1MetNot28': lambda ev: l1MetNot28(ev.caloTowers),
            'run': lambda ev: ev._run,
            'lumi': lambda ev: ev._lumi,
            'Sums_caloHt': lambda ev: ev.sums.caloHt,
            'Sums_Ht': lambda ev: ev.sums.Ht,
            'Sums_caloMetPhiBE': lambda ev: ev.sums.caloMetPhiBE,
            'Sums_caloMet': lambda ev: ev.sums.caloMet,
            'Sums_caloMetPhi': lambda ev: ev.sums.caloMetPhi,
            'Sums_pfMetNoMu': lambda ev: ev.sums.pfMetNoMu,
            'Sums_pfMetNoMuPhi': lambda ev: ev.sums.pfMetNoMuPhi,
            'l1Sums_EmuHtt': lambda ev: ev.l1Sums["L1EmuHtt"],
            'l1Sums_EmuMet': lambda ev: ev.l1Sums["L1EmuMet"],
            'l1Sums_EmuMetHF': lambda ev: ev.l1Sums["L1EmuMetHF"],
            'l1Sums_Htt': lambda ev: ev.l1Sums["L1Htt"],
            'l1Sums_Met': lambda ev: ev.l1Sums["L1Met"],
            'l1Sums_MetHF': lambda ev: ev.l1Sums["L1MetHF"],
            'goodPFJets': lambda ev: ev.goodJets(jetFilter=pfJetFilter, jetType="pf"),
            'caloJets': lambda ev: ev._caloJets,
            'l1EmuJets': lambda ev: ev._l1EmuJets,
            'l1Jets': lambda ev: ev._l1Jets,
            # '_genSums': lambda ev: ev._genSums,
        }

    def __getattr__(self, name):
        if name in object.__getattribute__(self, '_cache'):
            return object.__getattribute__(self, '_cache')[name]
        if name not in object.__getattribute__(self, '_map'):
            return self.event.__getattribute__(name)

        mapping = object.__getattribute__(self, '_map')[name]
        return mapping(self.event)

    def __getitem__(self, name):
        return object.__getattribute__(self, '__getattr__')(name)
