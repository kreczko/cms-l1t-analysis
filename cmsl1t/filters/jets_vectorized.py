import numpy as np


def _pfJetID(jet):
    abs_eta = np.absolute(jet.eta)
    isInnerJet = abs_eta <= 2.4
    isCentralJet = abs_eta <= 2.7
    isForwardCentralJet = (abs_eta > 2.7) & (abs_eta <= 3.0)
    isForwardJet = abs_eta > 3.0
    reject_if = \
        (jet.muMult != 0) | \
        (isCentralJet & (jet.nhef >= 0.9)) | \
        (isCentralJet & (jet.nemef >= 0.9)) | \
        (isCentralJet & ((jet.cMult + jet.nMult) <= 1)) | \
        (isCentralJet & (jet.mef >= 0.8)) | \
        (isInnerJet & (jet.chef <= 0)) | \
        (isInnerJet & (jet.cMult <= 0)) | \
        (isInnerJet & (jet.cemef >= 0.9)) | \
        (isForwardCentralJet & (jet.nhef >= 0.98)) | \
        (isForwardCentralJet & (jet.nemef <= 0.01)) | \
        (isForwardCentralJet & (jet.nMult <= 2)) | \
        (isForwardJet & (jet.nemef >= 0.9)) | \
        (isForwardJet & (jet.nMult <= 10))
    return jet[~reject_if]


def pfJetFilter(jets):
    return _pfJetID(jets)
