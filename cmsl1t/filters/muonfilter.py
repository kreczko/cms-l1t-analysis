import numpy as np


def muonfilter(event):
    passes = False
    pt, iso, isLoose = event.Muon_pt, event.Muon_iso, event.Muon_isLooseMuon
    pt, iso, isLoose = np.array(pt), np.array(iso), np.array(isLoose, dtype=np.dtype(bool))
    mask = [(pt > 20) & (iso <= 0.1) & (isLoose)]
    return len(pt[mask]) > 0
