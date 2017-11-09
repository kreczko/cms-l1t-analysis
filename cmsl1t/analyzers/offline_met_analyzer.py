from BaseAnalyzer import BaseAnalyzer
from cmsl1t.plotting.efficiency import EfficiencyPlot
from cmsl1t.collections import EfficiencyCollection
from cmsl1t.plotting.onlineVsOffline import OnlineVsOffline
from cmsl1t.plotting.resolution import ResolutionPlot
from cmsl1t.plotting.resolution_vs_X import ResolutionVsXPlot
import cmsl1t.recalc.met as recalc
from cmsl1t.playground.eventreader import Met, Sum
from math import pi
import pprint
from collections import namedtuple
import numpy as np


sum_types = [
    "HTT", "MHT", "MET_HF", "MET", "MET_PF", "MET_PF_NoMu", "MET_PF_HF",
    "MET_PF_NoMu_HF",
]
sum_types += [t + '_Emu' for t in sum_types]
jet_types = [
    "jetET_B", "jetET_E", "jetET_BE", "jetET_HF",
]
jet_types += [t + '_Emu' for t in jet_types]

Sums = namedtuple("Sums", sum_types)

# Eta ranges so we can put |\eta| < val as the legend header on the
# efficiency plots.
ETA_RANGES = dict(
    HTT="|\\eta| < 2.5",
    MHT="|\\eta| < 2.5",
    MET_HF="|\\eta| < 5.0",
    MET="|\\eta| < 3.0",
    MET_PF="|\\eta| < 3.0",
    MET_PF_NoMu="|\\eta| < 3.0",
    MET_PF_HF="|\\eta| < 5.0",
    MET_PF_NoMu_HF="|\\eta| < 5.0",
    jetET_B="|\\eta| < 1.479",
    jetET_E="1.479 < |\\eta| < 3.0",
    jetET_BE="|\\eta| < 3.0",
    jetET_HF="3.0 < |\\eta| < 5.0",
)

THRESHOLDS = dict(
    HTT=[160, 220, 280, 340, 400],
    MHT=[40, 60, 80, 100, 120],
    MET=[40, 60, 80, 100, 120],
    jetET_B=[35, 60, 90, 140, 180],
)

HIGH_RANGE_BINS = list(range(0, 100, 5)) + list(range(100, 400, 10))
HIGH_RANGE_BINS += list(range(400, 800, 50)) + list(range(800, 1000, 200))
HIGH_RANGE_BINS += list(range(1000, 2100, 500))
HIGH_RANGE_BINS = np.asarray(HIGH_RANGE_BINS, 'd')

for i in ['HF', 'PF', 'PF_NoMu', 'PF_HF', 'PF_NoMu_HF']:
    THRESHOLDS['MET_' + i] = THRESHOLDS['MET']
for i in ['E', 'BE', 'HF']:
    THRESHOLDS['jetET_' + i] = THRESHOLDS['jetET_B']


def ExtractSums(event):
    offline = dict(
        HTT=Sum(event.sums.Ht),
        MHT=Met(event.sums.mHt, event.sums.mHtPhi),
        MET_HF=Met(event.sums.caloMet, event.sums.caloMetPhi),
        MET=Met(event.sums.caloMetBE, event.sums.caloMetPhiBE),
        MET_PF=Met(event.sums.met, event.sums.metPhi),
        MET_PF_NoMu=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi),
        MET_PF_HF=Met(event.sums.met, event.sums.metPhi),
        MET_PF_NoMu_HF=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi),
        HTT_Emu=Sum(event.sums.Ht),
        MHT_Emu=Met(event.sums.mHt, event.sums.mHtPhi),
        MET_HF_Emu=Met(event.sums.caloMet, event.sums.caloMetPhi),
        MET_Emu=Met(event.sums.caloMetBE, event.sums.caloMetPhiBE),
        MET_PF_Emu=Met(event.sums.met, event.sums.metPhi),
        MET_PF_NoMu_Emu=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi),
        MET_PF_HF_Emu=Met(event.sums.met, event.sums.metPhi),
        MET_PF_NoMu_HF_Emu=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi)
    )
    online = dict(
        HTT=event.l1Sums["L1Htt"],
        MHT=event.l1Sums["L1Mht"],
        MET_HF=event.l1Sums["L1MetHF"],
        MET=event.l1Sums["L1Met"],
        MET_PF=event.l1Sums["L1Met"],
        MET_PF_NoMu=event.l1Sums["L1Met"],
        MET_PF_HF=event.l1Sums["L1MetHF"],
        MET_PF_NoMu_HF=event.l1Sums["L1MetHF"],
        HTT_Emu=event.l1Sums["L1EmuHtt"],
        MHT_Emu=event.l1Sums["L1EmuMht"],
        MET_HF_Emu=event.l1Sums["L1EmuMetHF"],
        MET_Emu=event.l1Sums["L1EmuMet"],
        MET_PF_Emu=event.l1Sums["L1EmuMet"],
        MET_PF_NoMu_Emu=event.l1Sums["L1EmuMet"],
        MET_PF_HF_Emu=event.l1Sums["L1EmuMetHF"],
        MET_PF_NoMu_HF_Emu=event.l1Sums["L1EmuMetHF"]
    )
    return online, offline


class Analyzer(BaseAnalyzer):

    def __init__(self, config, **kwargs):
        super(Analyzer, self).__init__("weekly_analyzer", config)

        for name in sum_types:
            eff_plot = EfficiencyPlot("L1", "offline_" + name)
            res_plot = ResolutionPlot("energy", "L1", "offline_" + name)
            twoD_plot = OnlineVsOffline("L1", "offline_" + name)
            self.register_plotter(eff_plot)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_eff", eff_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

            eff_plot_HR = EfficiencyPlot("L1", "offline_" + name + "_HiRange")
            twoD_plot_HR = OnlineVsOffline(
                "L1", "offline_" + name + "_HiRange")
            self.register_plotter(eff_plot_HR)
            self.register_plotter(twoD_plot_HR)
            setattr(self, name + "_eff_HR", eff_plot_HR)
            setattr(self, name + "_2D_HR", twoD_plot_HR)

        for angle in sum_types:
            if 'HTT' in angle:
                continue
            name = angle + "_phi"
            res_plot = ResolutionPlot("phi", "L1", "offline_" + name)
            twoD_plot = OnlineVsOffline("L1", "offline_" + name)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

        for name in jet_types:
            eff_plot = EfficiencyPlot("L1", "offline_" + name)
            res_plot = ResolutionPlot("energy", "L1", "offline_" + name)
            twoD_plot = OnlineVsOffline("L1", "offline_" + name)
            self.register_plotter(eff_plot)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_eff", eff_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

            eff_plot_HR = EfficiencyPlot("L1", "offline_" + name + "_HiRange")
            twoD_plot_HR = OnlineVsOffline(
                "L1", "offline_" + name + "_HiRange")
            self.register_plotter(eff_plot_HR)
            self.register_plotter(twoD_plot_HR)
            setattr(self, name + "_eff_HR", eff_plot_HR)
            setattr(self, name + "_2D_HR", twoD_plot_HR)

        self.res_vs_eta_CentralJets = ResolutionVsXPlot(
            "energy", "onlineJet", "offlineJet", "offlineJet_eta")
        self.register_plotter(self.res_vs_eta_CentralJets)

    def prepare_for_events(self, reader):
        puBins = self.puBins
        puBins_HR = [0, 999]

        Config = namedtuple(
            "Config",
            "name off_title on_title min max",
        )
        cfgs = [
            Config("HTT", "Offline HTT", "L1 HTT", 30, 600),
            Config("MHT", "Offline MHT", "L1 MHT", 0, 400),
            Config("MET_HF", "Offline MET with HF", "L1 MET", 0, 400),
            Config("MET", "Offline MET no HF", "L1 MET", 0, 400),
            Config("MET_PF", "Offline PF MET", "L1 MET", 0, 400),
            Config("MET_PF_NoMu", "Offline PF MET without Muons",
                   "L1 MET", 0, 400),
            Config(
                "MET_PF_HF", "Offline PF MET with HF", "L1 MET", 0, 400,
            ),
            Config(
                "MET_PF_NoMu_HF", "Offline PF MET with HF without Muons",
                "L1 MET", 0, 400,
            ),

        ]
        self._plots_from_cfgs(cfgs, puBins)
        self._plots_from_cfgs(cfgs, puBins, emulator=True)
        self._plots_from_cfgs(cfgs, puBins_HR, high_range=True)
        self._plots_from_cfgs(cfgs, puBins_HR, emulator=True, high_range=True)

        self.res_vs_eta_CentralJets.build(
            "Online Jet energy (GeV)",
            "Offline Jet energy (GeV)",
            "Offline Jet Eta (rad)",
            puBins,
            50, -0.5, 3.5, 50, -5.0, 5.0,
        )
        return True

    def _plots_from_cfgs(self, cfgs, puBins, emulator=False, high_range=False):
        suffix = ""
        prefix = ""
        if high_range:
            suffix = '_HR'
        if emulator:
            prefix = '_Emu'
        for cfg in cfgs:
            eff_plot = getattr(self, cfg.name + prefix + "_eff" + suffix)

            twoD_plot = getattr(self, cfg.name + prefix + "_2D" + suffix)
            thresholds = THRESHOLDS.get(cfg.name)
            params = [
                cfg.on_title, cfg.off_title + " (GeV)", puBins, thresholds,
                50, cfg.min, cfg.max,
            ]
            if high_range:
                params = [
                    cfg.on_title, cfg.off_title + " (GeV)", puBins, thresholds,
                    HIGH_RANGE_BINS.size - 1, HIGH_RANGE_BINS,
                ]

            eff_plot.build(*params, legend_title=ETA_RANGES.get(cfg.name, ""))
            params.remove(thresholds)
            twoD_plot.build(*params)

            if high_range:
                continue
            res_plot = getattr(self, cfg.name + prefix + "_res" + suffix)
            res_plot.build(cfg.on_title, cfg.off_title,
                           puBins, 50, -10, 10)

            if not hasattr(self, cfg.name + "_phi_res"):
                continue
            res_plot = getattr(self, cfg.name + "_phi_res")
            twoD_plot = getattr(self, cfg.name + "_phi_2D")
            twoD_plot.build(
                cfg.on_title + " Phi (rad)",
                cfg.off_title + " Phi (rad)",
                puBins, 50,
                -pi,
                2 * pi,
            )
            res_plot.build(
                cfg.on_title + " Phi",
                cfg.off_title + " Phi",
                puBins,
                50,
                -2,
                2,
            )

    def fill_histograms(self, entry, event):
        if not event.passesMETFilter():
            return True

        offline, online = ExtractSums(event)
        pileup = event.nVertex

        for name in sum_types:
            on = online[name]
            if on.et == 0:
                continue
            off = offline[name]
            for suffix in ['_eff', '_res', '_2D', '_eff_HR', '_2D_HR']:
                getattr(self, name + suffix).fill(pileup, off.et, on.et)
            if hasattr(self, name + "_phi_res"):
                getattr(self, name + "_phi_res").fill(pileup, off.phi, on.phi)
                getattr(self, name + "_phi_2D").fill(pileup, off.phi, on.phi)

        goodJets = event.goodJets()

        for recoJet in goodJets:
            l1Jet = event.getMatchedL1Jet(recoJet, l1Type='EMU')
            if not l1Jet:
                continue
            if recoJet.etCorr > 30.:
                self.res_vs_eta_CentralJets.fill(
                    pileup, recoJet.eta, recoJet.etCorr, l1Jet.et)

        leadingRecoJet = event.getLeadingRecoJet()
        if not leadingRecoJet:
            return True

        l1EmuJet = event.getMatchedL1Jet(leadingRecoJet, l1Type='EMU')
        if not l1EmuJet:
            return True

        fillRegions = []
        if abs(leadingRecoJet.eta) < 1.479:
            fillRegions = ['B', 'BE']
        elif abs(leadingRecoJet.eta) < 3.0:
            fillRegions = ['E', 'BE']
        else:
            fillRegions = ['HF']
        for region in fillRegions:
            for suffix in ['_eff', '_res', '_2D', '_eff_HR', '_2D_HR']:
                name = 'jetET_{0}_Emu{1}'.format(region, suffix)
                getattr(self, name).fill(
                    pileup, leadingRecoJet.etCorr, l1EmuJet.et,
                )

        l1Jet = event.getMatchedL1Jet(leadingRecoJet, l1Type='HW')
        if not l1Jet:
            return True

        for region in fillRegions:
            for suffix in ['_eff', '_res', '_2D', '_eff_HR', '_2D_HR']:
                name = 'jetET_{0}{1}'.format(region, suffix)
                getattr(self, name).fill(
                    pileup, leadingRecoJet.etCorr, l1Jet.et,
                )

        return True
