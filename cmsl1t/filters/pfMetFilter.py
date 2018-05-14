

def pfMetFilter(event):
    reject_if = [
        not event.MetFilters_badChCandFilter,
        not event.MetFilters_badPFMuonFilter,
        not event.MetFilters_ecalDeadCellTPFilter,
        not event.MetFilters_eeBadScFilter,
        not event.MetFilters_goodVerticesFilter,
        not event.MetFilters_globalSuperTightHalo2016Filter,
        not event.MetFilters_hbheNoiseFilter,
        not event.MetFilters_hbheNoiseIsoFilter,
    ]
    if any(reject_if):
        return False
    return True
