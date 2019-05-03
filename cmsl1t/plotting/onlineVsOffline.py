from __future__ import print_function
from cmsl1t.plotting.base import BasePlotter
from cmsl1t.hist.hist_collection import HistogramCollection
import cmsl1t.hist.binning as bn
from cmsl1t.utils.draw import draw2D, label_canvas

from rootpy.context import preserve_current_style
import numpy as np


class OnlineVsOffline(BasePlotter):

    def __init__(self, online_name, offline_name):
        name = ["online_vs_offline", online_name, offline_name]
        super(OnlineVsOffline, self).__init__("__".join(name))
        self.online_name = online_name
        self.offline_name = offline_name

    def create_histograms(
        self, online_title, offline_title, pileup_bins, n_bins, low, high=400.,
    ):
        """ This is not in an init function so that we can by-pass this in the
        case where we reload things from disk """
        self.online_title = online_title
        self.offline_title = offline_title
        self.pileup_bins = bn.Sorted(
            pileup_bins, "pileup",
            use_everything_bin=True,
        )

        nameTokens = [
            "onlineVsOffline", self.online_name,
            self.offline_name, "pu_{pileup}",
        ]
        name = "__".join(nameTokens)
        title = " ".join(
            [
                self.online_name,
                "vs.",
                self.offline_name,
                "in PU bin: {pileup}",
            ]
        )
        title = ";".join([title, self.offline_title, self.online_title])
        if isinstance(low, np.ndarray):
            self.plots = HistogramCollection(
                [self.pileup_bins],
                "Hist2D",
                low,
                low,
                name=name,
                title=title,
            )
        else:
            self.plots = HistogramCollection(
                [self.pileup_bins],
                "Hist2D",
                n_bins,
                low,
                high,
                n_bins,
                low,
                high,
                name=name,
                title=title,
            )
        self.filename_format = name

    def fill(self, pileup, offline, online):
        self.plots[pileup].fill(offline, online)

    def draw(self, with_fits=True):
        for pileup in self.pileup_bins.iter_all():
            plot = self.plots.get_bin_contents([pileup])
            self.__do_draw(self.pileup_bins.get_bin_center(pileup), plot)

    def __do_draw(self, pileup, hist):
        with preserve_current_style():
            # Draw each efficiency (with fit)
            canvas = draw2D(hist, draw_args={"xtitle": self.offline_title,
                                             "ytitle": self.online_title})
            canvas.SetLogz(True)

            # Add labels
            label_canvas()

            # Save canvas to file
            name = self.filename_format.format(pileup=pileup)
            self.save_canvas(canvas, name)

    def _is_consistent(self, new):
        """
        Check the two plotters are the consistent, so same binning and same axis names
        """
        return all([self.pileup_bins.bins == new.pileup_bins.bins,
                    self.online_name == new.online_name,
                    self.offline_name == new.offline_name,
                    ])

    def _merge(self, other):
        """
        Merge another plotter into this one
        """
        self.plots += other.plots
        return self.plots
