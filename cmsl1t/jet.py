class Jet(object):
    __slots__ = ['et', 'eta', 'phi']

    def __init__(self, *args):
        self.et, self.eta, self.phi = args

    def __getitem__(self, name):
        return object.__getattribute__(self, name)


class CaloJet(Jet):
    __slots__ = ['et', 'eta', 'phi', 'etCorr']

    def __init__(self, *args):
        common_args = args[:3]
        super(CaloJet, self).__init__(*common_args)
        self.etCorr = args[-1]


class PFJet(CaloJet):
    __slots__ = ['et', 'eta', 'phi', 'etCorr', 'cemef', 'chef',
                 'cMult', 'mef', 'muMult', 'nemef', 'nhef', 'nMult']

    def __init__(self, *args):
        common_args = args[:4]
        pf_args = args[4:]
        super(PFJet, self).__init__(*common_args)
        self.cemef, self.chef, self.cMult, self.mef = pf_args[:4]
        self.muMult, self.nemef, self.nhef, self.nMult = pf_args[4:]
