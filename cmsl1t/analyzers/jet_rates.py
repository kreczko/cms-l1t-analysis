"""
Study the MET distibutions and various PUS schemes
"""
import numpy as np
import six
import ROOT
import os
from cmsl1t.analyzers.BaseAnalyzer import BaseAnalyzer
from cmsl1t.collections import HistogramsByPileUpCollection


class Analyzer(BaseAnalyzer):

    def __init__(self, config, **kwargs):
        super(Analyzer, self).__init__("jet_rates", config)
        self.triggerName = self.config.get('input', 'trigger')['name']

    def prepare_for_events(self, reader):
        bins = np.arange(0.0, 300.0, 1.0)
        # thresholds = [70, 90, 110]
        puBins = range(0, 50, 10) + [999]

        self.rates = HistogramsByPileUpCollection(
            pileupBins=puBins, dimensions=2)
        self.rates.add('singlel1JetEt', bins)
        self.rates.add('doublel1JetEt', bins)
        self.rates.add('triplel1JetEt', bins)
        self.rates.add('quadl1JetEt', bins)

        return True

    def reload_histograms(self, input_file):
        # Something like this needs to be implemented still
        # self.rates = ResolutionCollection.from_root(input_file)
        return True

    def fill_histograms(self, entry, event):
        pileup = event['Vertex_nVtx']
        self.rates.set_pileup(pileup)

        l1JetEts = [jet['jetEt'] for jet in event.l1Jets]
        nJets = len(l1JetEts)
        if nJets == 0:
            return True
        maxL1JetEt = max(l1JetEts)

        if nJets >= 1:
            self.rates.fill('singlel1JetEt', maxL1JetEt)
        if nJets >= 2:
            self.rates.fill('doublel1JetEt', maxL1JetEt)
        if nJets >= 3:
            self.rates.fill('triplel1JetEt', maxL1JetEt)
        if nJets >= 4:
            self.rates.fill('quadl1JetEt', maxL1JetEt)

        return True

    def write_histograms(self):
        # calculate cumulative histograms
        cumul_hists = {}
        for puBin, histograms in six.iteritems(self.rates):
            cumul_hists[puBin] = {}
            for hist_name, hist in six.iteritems(histograms):
                h = get_cumulative_hist(hist)
                cumul_hists[puBin][h.name] = h
            self.rates[puBin].update(cumul_hists)

        # add them to self.rates

        self.rates.to_root(self.get_histogram_filename())
        return True

    def make_plots(self):
        # TODO: implement this in BaseAnalyzer
        # make_plots -> make_plots(plot_func)
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


def _reverse(a):
    return np.array(np.flipud(a))


def get_cumulative_hist(hist):
    h = hist.clone(hist.name + '_cumul')
    arr = np.cumsum(_reverse([bin.value for bin in hist]))
    h.set_content(_reverse(arr))
    errors_sq = np.cumsum(_reverse([bin.error**2 for bin in hist]))
    h.set_error(_reverse(np.sqrt(errors_sq)))

    # now scale
    bin1 = h.get_bin_content(1)
    if bin1 != 0:
        h.GetSumw2()
        h.Scale(4.0e7 / bin1)
    return h


def plot(hist, name, output_folder):
    pu = ''
    if '_pu' in name:
        pu = name.split('_')[-1]
        name = name.replace('_' + pu, '')
    file_name = 'rates_{name}'.format(name=name)
    if 'nVertex' in name:
        file_name = 'nVertex'
    if pu:
        file_name += '_' + pu
    canvas_name = file_name.replace('SingleMu', 'Rates')
    c = ROOT.TCanvas(canvas_name)
    if 'nVertex' not in name:
        c.SetLogy()
    hist.set_y_title('Rate (Hz)')
    hist.Draw()
    c.SaveAs(os.path.join(output_folder, file_name + '.pdf'))
