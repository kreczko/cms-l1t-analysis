"""
Study the MET distibutions and various PUS schemes
"""

import math
import ROOT
import os
import numpy as np
from functools import partial

from cmsl1t.analyzers.BaseAnalyzer import BaseAnalyzer
from cmsl1t.collections import EfficiencyCollection
from cmsl1t.filters import muonfilter
from cmsl1t.geometry import is_in_region
from cmsl1t.producers.match import get_matched_l1_jet


class Analyzer(BaseAnalyzer):

    def __init__(self, config, **kwargs):
        super(Analyzer, self).__init__(__name__, config)
        self.triggerName = self.config.get('input', 'trigger')['name']

    def prepare_for_events(self, reader):
        bins = list(np.arange(0, 100, 2))
        bins.extend(np.arange(100, 200, 5))
        bins.extend(np.arange(200, 300, 10))
        bins.extend(np.arange(300, 400, 20))
        bins.extend(np.arange(400, 500, 25))
        print(bins)

        thresholds = [36., 68., 128., 200.]
        puBins = range(0, 50, 10) + [999]

        self.efficiencies = EfficiencyCollection(pileupBins=puBins)
        self.efficiencies.add_variable(
            'JetEt', bins=bins, thresholds=thresholds)
        add_jet_variable = partial(
            self.efficiencies.add_variable,
            bins=bins, thresholds=thresholds)
        map(add_jet_variable, ['JetEtBarrel',
                               'JetEtCentral', 'JetEtEndcap', 'JetEtHF'])

        return True

    def reload_histograms(self, input_file):
        # Something like this needs to be implemented still
        # self.efficiencies = EfficiencyCollection.from_root(input_file)
        return True

    def fill_histograms(self, entry, event):
        if self.triggerName == 'SingleMu':
            if not muonfilter(event):
                return True
        pileup = event['Vertex_nVtx']

        recoJets = event['goodRecoJets']
        if not recoJets:
            return True
        leadingRecoJet = recoJets[0]
        l1Jets = event['l1Jets']
        # TODO, this will be replaced by a proper producer
        matchedL1Jet = get_matched_l1_jet(leadingRecoJet, l1Jets)

        if not leadingRecoJet or not matchedL1Jet:
            return True

        recoEt = leadingRecoJet.etCorr
        recoEta = leadingRecoJet.eta

        l1Et = matchedL1Jet['jetEt']

        self.efficiencies.set_pileup(pileup)
        if is_in_region('B', recoEta):
            self.efficiencies.fill('JetEtBarrel', recoEt, l1Et)
        elif is_in_region('BE', recoEta):
            self.efficiencies.fill('JetEtCentral', recoEt, l1Et)
        elif is_in_region('E', recoEta):
            self.efficiencies.fill('JetEtEndcap', recoEt, l1Et)
        else:
            self.efficiencies.fill('JetEtHF', recoEt, l1Et)

        return True

    def write_histograms(self):
        self.efficiencies.to_root(self.get_histogram_filename())
        return True

    def make_plots(self):
        from rootpy.io import root_open
        with root_open(self.get_histogram_filename()) as f:
            # our collections are flat, need only the objects
            for _, _, objects in f.walk():
                for name in objects:
                    if 'pickle' in name:
                        continue
                    obj = f.get(name)
                    plot(obj, name, self.output_folder)
        return True


def plot(hist, name, output_folder):
    pu = ''
    if '_pu' in name:
        pu = name.split('_')[-1]
        name = name.replace('_' + pu, '')
    file_name = 'turnon_SingleMu_reco{name}'.format(name=name)
    if 'nVertex' in name:
        file_name = 'nVertex'
    if pu:
        file_name += '_' + pu
    canvas_name = file_name.replace('SingleMu', 'Energy')
    if 'JetEta' in name or 'JetPhi' in name:
        canvas_name.replace('Energy', 'Position')
    c = ROOT.TCanvas(canvas_name)
    hist.Draw()
    c.SaveAs(os.path.join(output_folder, file_name + '.pdf'))


def foldPhi(phi):
    return min([abs(phi), abs(2 * math.pi - phi)])
