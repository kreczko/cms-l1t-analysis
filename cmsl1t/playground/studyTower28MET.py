from __future__ import print_function
import ROOT
import os
import glob
import logging
import numpy as np
from eventreader import EventReader
from cmsl1t.collections import EfficiencyCollection
from functools import partial

logging.getLogger("rootpy.tree.chain").setLevel(logging.WARNING)


FILES = glob.glob('data/*.root')


def main(nEvents, output_folder):
    # range 0-100 in steps of 25
    bins = np.arange(0, 200, 25)
    thresholds = [70, 90, 110]
    # TODO: add control plots
    histograms = EfficiencyCollection(pileupBins=[0, 13, 20, 999])
    # all MET variables have the same bins & thresholds
    add_met_variable = partial(
        histograms.add_variable, bins=bins, thresholds=thresholds)

    map(add_met_variable, [
        'RecalcL1EmuMet',
        # 'RecalcL1EmuMetHF',
        # 'RecalcL1EmuMet28Only',
        # 'RecalcL1EmuMetNot28',
        # 'RecalcL1EmuMetPUS',
        # 'RecalcL1EmuMetPUSHF',
        # 'RecalcL1EmuMetPUS28',
        # 'RecalcL1EmuMetPUSThresh',
        # 'RecalcL1EmuMetPUSThreshHF',
        # 'RecalcL1Met',
        # 'RecalcL1Met28Only',
    ])

    reader = EventReader(FILES, events=nEvents)

    for entry, event in enumerate(reader):
        pileup = event.nVertex
        if pileup < 5 or not event.passesMETFilter():
            continue

        histograms.set_pileup(pileup)

        caloMetBE = event.sums.caloMetBE
        l1Sums = event.l1Sums
        if 'L1Met' not in l1Sums:
            print(l1Sums)
        # l1Met = l1Sums['L1Met'].et

        # l1Met28Only = rmet.l1Met28Only(event.caloTowers)
        # metNot28HF = rmet.l1MetNot28HF(event.caloTowers)
        # metNot28 = rmet.l1MetNot28(event.caloTowers)

        l1EmuMet = l1Sums['L1EmuMet'].et
        # l1EmuMetHF = l1Sums['L1EmuMetHF'].et
        # l1EmuMet28Only = rmet.l1Met28Only(event.emuCaloTowers)
        # l1EmuMetNot28 = rmet.l1MetNot28(event.emuCaloTowers)

        histograms.fill('RecalcL1EmuMet', caloMetBE, l1EmuMet)

        # l1EmuMetPUS =
        # l1EmuMetPUSHF =
        # l1EmuMetPUS28 =
        # l1EmuMetPUSThresh =
        # l1EmuMetPUSThreshHF =
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_file = os.path.join(output_folder, 'studyTower28MET.root')
    histograms.to_root(output_file)

    # plotting should be separate, this is just here as an example
    from rootpy.io import root_open
    with root_open(output_file) as f:
        # our collections are flat, need only the objects
        for _, _, objects in f.walk():
            for name in objects:
                if 'pickle' in name:
                    continue
                # obj = f.get(name)
#                 plot(obj, name, output_folder)
    print('Processed', entry + 1, 'events')


if __name__ == '__main__':
    from datetime import datetime
    TODAY = datetime.now().timetuple()
    ROOT.gSystem.Load('build/L1TAnalysisDataformats.so')
    output_folder = os.path.join(
        'benchmark', 'new',
        '{y}{m:02d}{d:02d}_Data_run-276243_SingleMu_CHUNK0'.format(
            y=TODAY.tm_year, m=TODAY.tm_mon, d=TODAY.tm_mday),
        'Turnons'
    )
    main(10000, output_folder)
