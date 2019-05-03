import numpy as np


def jet_match(jetlist1, jetlist2, max_R_to_match=0.5):

    delta_R = _build_dR(jetlist1, jetlist2)
    matched_jets = _run_jet_matching(delta_R, max_R_to_match)
    return matched_jets


def _build_dR(jetlist1, jetlist2):
    n_jet1 = len(jetlist1)
    n_jet2 = len(jetlist2)
    jet1_eta = np.array([jet.eta for jet in jetlist1])
    jet1_phi = np.array([jet.phi for jet in jetlist1])
    jet2_eta = np.array([jet.eta for jet in jetlist2])
    jet2_phi = np.array([jet.phi for jet in jetlist2])

    jet1_eta = np.tile(jet1_eta, (n_jet2, 1))
    jet1_phi = np.tile(jet1_phi, (n_jet2, 1))
    jet2_eta = np.tile(jet2_eta, (n_jet1, 1)).T
    jet2_phi = np.tile(jet2_phi, (n_jet1, 1)).T

    delta_eta = jet1_eta - jet2_eta
    delta_phi = jet1_phi - jet2_phi

    return np.sqrt(delta_eta**2 + delta_phi**2)


def _run_jet_matching(delta_R, max_R_to_match):
    matched_jets = []
    while True:
        index = np.argmin(delta_R)
        index = np.unravel_index(index, delta_R.shape)
        min_dR = delta_R[index[0], index[1]]
        if min_dR > max_R_to_match:
            break
        matched_jets.append(index)
        delta_R[index[0], :] = np.inf
        delta_R[:, index[1]] = np.inf
        # Are there more pairings to test in the matrix?
        if not np.any(np.isfinite(delta_R)):
            break

    return matched_jets
