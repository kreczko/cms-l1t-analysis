from __future__ import print_function
from cmsl1t.plotting.efficiency import EfficiencyPlot
import cmsl1t.hist.binning as bn
from rootpy.io import root_open
import numpy as np


def prepare_fake_eff_plots():
    on_vs_off_efficiency = EfficiencyPlot("online", "offline")
    off_vs_off_efficiency = EfficiencyPlot("offline", "offline")
    on_vs_on_efficiency = EfficiencyPlot("online", "online")
    plotters = {"on_v_off": on_vs_off_efficiency,
                "off_v_off": off_vs_off_efficiency,
                "on_v_on": on_vs_on_efficiency}
    return plotters


def fake_efficiency_plots(prefix, n_points=10000, online_offset=10, online_resolution=10,
                          puBins=[0, 999], thresholds=[50], pileup=3):
    offline_data = np.random.uniform(0, 100, n_points)
    online_data = offline_data + np.random.normal(online_offset, online_resolution, n_points)

    plotters = prepare_fake_eff_plots()
    plotters["on_v_off"].build("Test online", "Test offline", puBins, thresholds, 50, 0, 300)
    plotters["off_v_off"].build("Test offline", "Test offline", puBins, thresholds, 50, 0, 300)
    plotters["on_v_on"].build("Test online", "Test online", puBins, thresholds, 50, 0, 300)

    for name, plotter in plotters.items():
        plotter.set_plot_output_cfg("tests/outputs", "png")

    for on, off in zip(online_data, offline_data):
        plotters["on_v_off"].fill(pileup, on, off)
        plotters["on_v_on"].fill(pileup, on, on)
        plotters["off_v_off"].fill(pileup, off, off)

    return plotters


def test_EffiencyPlot_noPU_oneThreshold():
    plotters = fake_efficiency_plots("", 10000, thresholds=[53])

    # with root_open("test/outputs/plotting-test_efficiency.root", "w") as out_file:
    #     for name, plotter in plotters.items():
    #         plotter.to_root(out_file.mkdir(plotter.directory_name))

    for plotter in plotters.values():
        if not isinstance(plotter, EfficiencyPlot):
            continue
        for pu_bin in [0, bn.Base.everything]:
            above_50 = plotter.efficiencies.get_bin_contents([pu_bin, 0])
            non_integral = [eff for eff in above_50 if eff != int(eff)]
            setattr(plotter, "n_non_integral_" + str(pu_bin), len(non_integral))

    # There should only be 1 non-integer bin: that which contains the actual threshold
    assert 1 == plotters["on_v_on"].n_non_integral_0
    assert 1 == plotters["off_v_off"].n_non_integral_0
    assert 1 == plotters["on_v_on"].n_non_integral_everything
    assert 1 == plotters["off_v_off"].n_non_integral_everything


def test_EffiencyPlot_merge():
    threshold = 50
    plotters_1 = fake_efficiency_plots("merge_1", n_points=10000, online_offset=0, thresholds=[threshold])
    plotters_2 = fake_efficiency_plots("merge_2", n_points=10000, online_offset=0, thresholds=[threshold])
    plotters_merged = prepare_fake_eff_plots()

    for plot_name, merged in plotters_merged.items():
        merged.merge_in(plotters_1[plot_name])
        merged.merge_in(plotters_2[plot_name])

    for name, plotter in plotters_merged.items():
        if not isinstance(plotter, EfficiencyPlot):
            continue
        above_threshold = plotter.efficiencies.get_bin_contents([bn.Base.everything, 0])
        axis = above_threshold.total
        zeroes = [(eff, axis.x(i), axis.yerrh(i)) for i, eff in enumerate(above_threshold)]
        zeroes = [(eff == 0, x > threshold, yerr > 0) for eff, x, yerr in zeroes]
        zeroes = [zero_eff and over and yerr for zero_eff, over, yerr in zeroes]
        plotter.zeroes_over_thresh = zeroes

    assert not any(plotters_merged["on_v_on"].zeroes_over_thresh)
    assert not any(plotters_merged["off_v_off"].zeroes_over_thresh)
    assert not any(plotters_merged["on_v_off"].zeroes_over_thresh)
