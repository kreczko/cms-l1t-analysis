"""
Make plots for the weekly checks
"""

from BaseAnalyzer import BaseAnalyzer
from cmsl1t.plotting.efficiency import EfficiencyPlot
from cmsl1t.plotting.onlineVsOffline import OnlineVsOffline
from cmsl1t.plotting.resolution import ResolutionPlot
from cmsl1t.plotting.resolution_vs_X import ResolutionVsXPlot
import cmsl1t.recalc.met as recalc
from math import pi
import pprint
from collections import namedtuple
from cmsl1t.producers.match import get_matched_l1_jet


sum_types = ["HTT", "MHT", "MET_HF", "MET_noHF"]
Sums = namedtuple("Sums", sum_types)

Sum = namedtuple('Sum', ['et'])
Met = namedtuple('Met', ['et', 'phi'])


def ExtractSums(event):
    offline = dict(
        HTT=Sum(event.Sums_Ht),
        MHT=Met(event.Sums_mHt, event.Sums_mHtPhi),
        MET_HF=Met(event.Sums_caloMet, event.Sums_caloMetPhi),
        MET_noHF=Met(event.Sums_caloMetBE, event.Sums_caloMetPhiBE),
    )
    online = dict(
        HTT=Sum(event.L1Upgrade_sumEt[event.energySumTypes['Htt']]),
        MHT=Met(
            event.L1Upgrade_sumEt[event.energySumTypes['Mht']],
            event.L1Upgrade_sumPhi[event.energySumTypes['Mht']],
        ),
        MET_HF=Met(
            event.L1Upgrade_sumEt[event.energySumTypes['MetHF']],
            event.L1Upgrade_sumPhi[event.energySumTypes['MetHF']],
        ),
        MET_noHF=Met(
            event.L1Upgrade_sumEt[event.energySumTypes['Met']],
            event.L1Upgrade_sumPhi[event.energySumTypes['Met']],
        ),
    )
    return online, offline


class Analyzer(BaseAnalyzer):

    def __init__(self, config, **kwargs):
        super(Analyzer, self).__init__("study_met", config)

        for name in sum_types:
            eff_plot = EfficiencyPlot("online" + name, "offline" + name)
            res_plot = ResolutionPlot(
                "energy", "online" + name, "offline" + name)
            twoD_plot = OnlineVsOffline("online" + name, "offline" + name)
            self.register_plotter(eff_plot)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_eff", eff_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

        for angle in sum_types[1:]:
            name = angle + "_phi"
            res_plot = ResolutionPlot("phi", "online" + name, "offline" + name)
            twoD_plot = OnlineVsOffline("online" + name, "offline" + name)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

        self.res_vs_eta_CentralJets = ResolutionVsXPlot(
            "energy", "onlineJet", "offlineJet", "offlineJet_eta")
        self.register_plotter(self.res_vs_eta_CentralJets)

    def prepare_for_events(self, reader):
        # TODO: Get these from a common place, and / or the config file
        puBins = range(0, 50, 10) + [999]
        thresholds = [70, 90, 110, 130]

        Config = namedtuple("Config", "name off_title on_title off_max on_max")
        HTT_cfg = Config("HTT", "Offline HTT", "Online HTT", 600, 600)
        MHT_cfg = Config("MHT", "Offline MHT", "Online MHT", 600, 600)
        MET_HF_cfg = Config("MET_HF", "Offline MET with HF",
                            "Calo MET with HF", 600, 600)
        MET_noHF_cfg = Config(
            "MET_noHF", "Offline MET no HF", "Calo MET no HF", 600, 600)
        cfgs = [HTT_cfg, MHT_cfg, MET_HF_cfg, MET_noHF_cfg]
        for cfg in cfgs:
            eff_plot = getattr(self, cfg.name + "_eff")
            res_plot = getattr(self, cfg.name + "_res")
            twoD_plot = getattr(self, cfg.name + "_2D")
            eff_plot.build(cfg.on_title + " (GeV)", cfg.off_title + " (GeV)",
                           puBins, thresholds, 50, 0, cfg.off_max)
            twoD_plot.build(cfg.on_title + " (GeV)", cfg.off_title + " (GeV)",
                            puBins, 50, 0, cfg.off_max)
            res_plot.build(cfg.on_title, cfg.off_title,
                           puBins, 50, -10, 10)

            if not hasattr(self, cfg.name + "_phi_res"):
                continue
            res_plot = getattr(self, cfg.name + "_phi_res")
            twoD_plot = getattr(self, cfg.name + "_phi_2D")
            twoD_plot.build(cfg.on_title + " Phi (rad)", cfg.off_title + " Phi (rad)",
                            puBins, 50, -pi, 2 * pi)
            res_plot.build(cfg.on_title + " Phi", cfg.off_title + " Phi",
                           puBins, 50, -2, 2)

        self.res_vs_eta_CentralJets.build("Online Jet energy (GeV)",
                                          "Offline Jet energy (GeV)", "Offline Jet Eta (rad)",
                                          puBins, 50, -10, 10, 30, 0, 6)
        return True

    def fill_histograms(self, entry, event):
        if not event['MetFilters_hbheNoiseFilter']:
            return True

        offline, online = ExtractSums(event)
        pileup = event['Vertex_nVtx']

        for name in sum_types:
            on = online[name]
            if on.et == 0:
                continue
            off = offline[name]
            getattr(self, name + "_eff").fill(pileup, off.et, on.et)
            getattr(self, name + "_res").fill(pileup, off.et, on.et)
            getattr(self, name + "_2D").fill(pileup, off.et, on.et)
            if hasattr(self, name + "_phi_res"):
                getattr(self, name + "_phi_res").fill(pileup, off.phi, on.phi)
                getattr(self, name + "_phi_2D").fill(pileup, off.phi, on.phi)

        l1Jets = event['l1Jets']
        for recoJet in event.goodRecoJets:
            l1Jet = get_matched_l1_jet(recoJet, l1Jets)
            if not l1Jet:
                continue
            self.res_vs_eta_CentralJets.fill(
                pileup, recoJet.eta, recoJet.etCorr, l1Jet.jetEt)

        return True
