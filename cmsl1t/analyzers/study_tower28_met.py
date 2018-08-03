"""
Study the MET distibutions and various PUS schemes
"""

from BaseAnalyzer import BaseAnalyzer
from cmsl1t.collections import EfficiencyCollection
from functools import partial
import cmsl1t.recalc.met as recalc
from cmsl1t.filters import muonfilter
import numpy as np


class Analyzer(BaseAnalyzer):

    def __init__(self, **kwargs):
        super(Analyzer, self).__init__(**kwargs)
        self.triggerName = self.params['triggerName']

        self.met_calcs = dict(
            RecalcL1EmuMETNot28=dict(
                title="Emulated MET, |ieta|<28",
                calculate=recalc.l1MetNot28),
            RecalcL1EmuMETNot28HF=dict(
                title="Emulated MET, |ieta|!=28",
                calculate=recalc.l1MetNot28HF),
        )

    def prepare_for_events(self, reader):
        bins = np.arange(0, 200, 25)
        thresholds = [70, 90, 110]
        puBins = range(0, 50, 10) + [999]

        self.efficiencies = EfficiencyCollection(pileupBins=puBins)
        add_met_variable = partial(
            self.efficiencies.add_variable,
            bins=bins, thresholds=thresholds)
        map(add_met_variable, self.met_calcs)

        return True

    def reload_histograms(self, input_file):
        # Something like this needs to be implemented still
        # self.efficiencies = EfficiencyCollection.from_root(input_file)
        return True

    def fill_histograms(self, entry, event):
        if self.triggerName == 'SingleMu':
            if not muonfilter(event.muons):
                return True
        pileup = event.nVertex
        if pileup < 5 or not event.passesMETFilter():
            return True

        self.efficiencies.set_pileup(pileup)

        offlineMetBE = event.sums.caloMetBE
        for name, config in self.met_calcs.items():
            onlineMet = config['calculate'](event.caloTowers)
            onlineMet = onlineMet.mag
            self.efficiencies.fill(name, offlineMetBE, onlineMet)
        return True

    def write_histograms(self):
        self.efficiencies.to_root(self.get_histogram_filename())
        return True

    def make_plots(self):
        # Something like this needs to be implemented still
        # self.efficiencies.draw_plots(self.output_folder, "png")
        return True
