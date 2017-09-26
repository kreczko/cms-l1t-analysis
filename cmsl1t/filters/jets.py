import cmsl1t.geometry as geo


def jetFilterNoHF(jet):
    '''
        also a lot of potential for simplification
    '''
    isForwardJet = geo.is_in_region('HF', jet.eta)
    innerJet = abs(jet.eta) <= 2.4
    reject_if = [
        jet.muMult != 0,
        isForwardJet,
        jet.nhef >= 0.9,
        jet.pef >= 0.9,
        jet.mef >= 0.8,
        jet.allMult <= 1,
        innerJet and jet.sumMult <= 0,
        innerJet and jet.chef <= 0,
        innerJet and jet.eef >= 0.9,
    ]
    if any(reject_if):
        return False
    return True


def defaultJetFilter(jet):
    return (abs(jet.eta) > 3.0 or jetFilterNoHF(jet)) and jet.etCorr > 30.
