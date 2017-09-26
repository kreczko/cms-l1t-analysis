

def muonfilter(event, columns=['Muon_et', 'Muon_iso', 'Muon_isLooseMuon']):
    passes = False
    mPts = event[columns[0]]
    mIsos = event[columns[1]]
    mIDs = event[columns[2]]
    for (pt, iso, mID) in zip(mPts, mIsos, mIDs):
        if pt > 20 and iso <= 0.1 and bool(mID):
            passes = True
            break
    return passes
