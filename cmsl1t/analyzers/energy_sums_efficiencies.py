"""
Study the efficiencies of L1 energy sums
"""

import math
import os
import numpy as np
from functools import partial

import ROOT

from cmsl1t.analyzers.BaseAnalyzer import BaseAnalyzer
from cmsl1t.collections import EfficiencyCollection
from cmsl1t.filters import muonfilter
from cmsl1t.geometry import is_in_region


class Analyzer(BaseAnalyzer):

    def __init__(self, config, **kwargs):
        super(Analyzer, self).__init__(__name__, config)
        self.triggerName = self.config.get('input', 'trigger')['name']

    def prepare_for_events(self, reader):
        met_bins = list(np.arange(0, 40, 2))
        met_bins.extend(np.arange(40, 80, 5))
        met_bins.extend(np.arange(80, 120, 10))
        met_bins.extend(np.arange(120, 300, 20))

        mht_bins = list(np.arange(30, 50, 1))
        mht_bins.extend(np.arange(50, 80, 5))
        mht_bins.extend(np.arange(80, 140, 10))
        mht_bins.extend(np.arange(140, 200, 15))
        mht_bins.extend(np.arange(200, 300, 20))
        mht_bins.extend(np.arange(300, 400, 25))

        ett_bins = list(np.arange(0, 30, 30))
        ett_bins.extend(np.arange(30, 50, 10))
        ett_bins.extend(np.arange(50, 90, 5))
        ett_bins.extend(np.arange(90, 140, 2))

        htt_bins = list(np.arange(0, 100, 20))
        htt_bins.extend(np.arange(100, 200, 10))
        htt_bins.extend(np.arange(200, 400, 20))
        htt_bins.extend(np.arange(400, 500, 50))
        htt_bins.extend(np.arange(500, 800, 100))
        htt_bins.extend(np.arange(800, 1400, 200))
        htt_bins.extend(np.arange(1400, 2000, 600))

        thresholds = [0, 70, 90, 110]
        puBins = range(0, 50, 10) + [999]

        self.efficiencies = EfficiencyCollection(pileupBins=puBins)
        add_met_variable = partial(
            self.efficiencies.add_variable,
            bins=met_bins, thresholds=thresholds)
        map(add_met_variable, ['metBE',
                               'metBERecalc', 'metBEEmu', 'metBERecalcEmu'])
        self.efficiencies.add_variable(
            'htt', bins=htt_bins, thresholds=thresholds)

        return True

    def reload_histograms(self, input_file):
        # Something like this needs to be implemented still
        # self.efficiencies = EfficiencyCollection.from_root(input_file)
        return True

    def fill_histograms(self, entry, event):
        if self.triggerName == 'SingleMu':
            if not muonfilter(event):
                return True
        if not event['MetFilters_hbheNoiseFilter']:
            return True

        pileup = event['Vertex_nVtx']
        self.efficiencies.set_pileup(pileup)

        l1MetBE = event.L1Upgrade_sumEt[event.energySumTypes['Met']]
        l1MetBERecalc = event['l1MetBERecalc']
        l1MetBERecalc = l1MetBERecalc.mag

        l1MetBEEmu = event.emu_L1Upgrade_sumEt[event.energySumTypes['Met']]
        l1MetBERecalcEmu = event['l1MetBERecalcEmu']
        l1MetBERecalcEmu = l1MetBERecalcEmu.mag

        l1Htt = event.L1Upgrade_sumEt[event.energySumTypes['Htt']]

        offlineMetBE = event.Sums_caloMetBE
        recoHtt = event.Sums_Ht

        self.efficiencies.fill('metBE', offlineMetBE, l1MetBE)
        self.efficiencies.fill('metBERecalc', offlineMetBE, l1MetBERecalc)
        self.efficiencies.fill('metBEEmu', offlineMetBE, l1MetBEEmu)
        self.efficiencies.fill(
            'metBERecalcEmu', offlineMetBE, l1MetBERecalcEmu)

        self.efficiencies.fill('htt', recoHtt, l1Htt)

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
    c = ROOT.TCanvas(canvas_name)
    hist.Draw()
    c.SaveAs(os.path.join(output_folder, file_name + '.pdf'))


def foldPhi(phi):
    return min([abs(phi), abs(2 * math.pi - phi)])
