from __future__ import print_function
from cmsl1t.plotting.base import BasePlotter
from cmsl1t.hist.hist_collection import HistogramCollection
import cmsl1t.hist.binning as bn
from cmsl1t.utils.draw import draw2D, label_canvas
from cmsl1t.recalc.resolution import get_resolution_function

from rootpy.context import preserve_current_style
from math import sqrt
from copy import deepcopy


class ResolutionVsXPlot(BasePlotter):

    def __init__(self, resolution_type, online_name, offline_name, versus_name):
        name = ["resolution_vs_" + versus_name, online_name, offline_name]
        super(ResolutionVsXPlot, self).__init__("__".join(name))
        self.online_name = online_name
        self.offline_name = offline_name
        self.versus_name = versus_name
        self.resolution_method = get_resolution_function(resolution_type)

    def create_histograms(
            self, online_title, offline_title, versus_title, pileup_bins,
            res_n_bins, res_low, res_high, vs_n_bins, vs_low, vs_high):
        """ This is not in an init function so that we can by-pass this in the
        case where we reload things from disk """
        self.online_title = online_title
        self.offline_title = offline_title
        self.versus_title = versus_title
        self.ymin = res_low
        self.ymax = res_high
        self.pileup_bins = bn.Sorted(pileup_bins, "pileup",
                                     use_everything_bin=True)

        nameTokens = [
            "resolution_vs", self.versus_name,
            self.online_name, self.offline_name, "pu_{pileup}",
        ]
        name = "__".join(nameTokens)
        title = 'Resolution ({online_name} vs. {offline_name}) '
        title += 'against {versus_name}'
        title = title.format(
            online_name=self.online_name,
            offline_name=self.offline_name,
            versus_name=self.versus_name,
        )
        title += " in PU bin: {pileup}"
        title = ";".join([title, self.offline_title, self.online_title])
        self.plots = HistogramCollection(
            [self.pileup_bins],
            "Hist2D", vs_n_bins, vs_low, vs_high,
            res_n_bins, res_low, res_high,
            name=name, title=title)
        self.filename_format = name

    def fill(self, pileup, versus, offline, online):
        difference = self.resolution_method(online, offline)
        self.plots[pileup].fill(versus, difference)

    def draw(self, with_fits=True):
        for (pileup, ), hist in self.plots.flat_items_all():
            self.__do_draw(pileup, hist)
            profileX = hist.ProfileX()
            projectionX = deepcopy(hist.ProjectionX())

            for i in range(hist.GetNbinsX()):
                pX_i = profileX.GetBinContent(i)
                if pX_i == 0:
                    projectionX.SetBinContent(i, 0.)
                    continue
                pX_i_err = profileX.GetBinError(i)
                projX_i = projectionX.GetBinContent(i)

                newValue = sqrt(projX_i) * pX_i_err / pX_i
                newError = projX_i * pX_i_err

                projectionX.SetBinContent(i, newValue)
                projectionX.SetBinError(i, 0.)
                profileX.SetBinError(i, newError)

            if projectionX.GetMaximum() > 3.:
                projectionX.GetYaxis().SetRangeUser(0., 2.)
            self.__do_draw(pileup, profileX, "_profile2")
            self.__do_draw(pileup, projectionX, "_profile")

    def __do_draw(self, pileup, hist, suffix=""):
        with preserve_current_style():
            # Draw each efficiency (with fit)
            if suffix == "":
                ytitle = "Online Jet Energy / Offline Jet Energy"
            elif suffix == "_profile":
                ytitle = "RMS/Mean (Online Jet Energy/Offline Jet Energy)"
            else:
                ytitle = self.resolution_method.label.format(
                    on=self.online_title,
                    off=self.offline_title,
                )
            canvas = draw2D(
                hist,
                draw_args={"xtitle": self.versus_title, "ytitle": ytitle},
            )

            # Add labels
            label_canvas()

            # Save canvas to file
            name = self.filename_format.format(pileup=pileup)
            self.save_canvas(canvas, name + suffix)

    def _is_consistent(self, new):
        """
            Check the two plotters are the consistent,
            so same binning and same axis names
        """
        return all([
            self.pileup_bins.bins == new.pileup_bins.bins,
            self.resolution_method == new.resolution_method,
            self.versus_name == new.versus_name,
            self.online_name == new.online_name,
            self.offline_name == new.offline_name,
        ])

    def _merge(self, other):
        """
        Merge another plotter into this one
        """
        self.plots += other.plots
        return self.plots
