from importlib import import_module

DEFAULT_ATTRIBUTES = [
    'etCorr', 'muMult', 'eta', 'phi', 'nhef', 'pef', 'mef', 'chMult',
    'elMult', 'nhMult', 'phMult', 'chef', 'eef'
]

L1T_Jet_ATTRIBUTES = [
    'jetEt', 'jetPhi', 'jetEta',
]


class Jet(object):
    '''
        Create a simple python wrapper for
        L1Analysis::L1AnalysisRecoJetDataFormat
    '''

    def __init__(self, event, index, prefix='Jet_'):
        global DEFAULT_ATTRIBUTES
        # this could be simplified with a list of attributes
        read_attributes = []
        if not hasattr(event, prefix + DEFAULT_ATTRIBUTES[0]):
            read_attributes[:] = L1T_Jet_ATTRIBUTES[:]
            self.sortBy = 'jetEt'
        else:
            read_attributes[:] = DEFAULT_ATTRIBUTES[:]
            self.sortBy = 'etCorr'
        for attr in read_attributes:
            setattr(self, attr, getattr(event, prefix + attr)[index])

    def __getitem__(self, name):
        return object.__getattribute__(self, name)

# TODO:
# 1. good reco jets (use jet filters)
# 2. matched L1 jets


class Producer(object):

    def __init__(self, inputs, outputs, params):
        self.inputs = inputs
        self.outputs = outputs
        self.params = params

        self.prefix = self.inputs[0].replace('*', '')
        if params and 'filter' in params:
            self.jetFilter = self._load_filter_module(params['filter'])
        else:
            self.jetFilter = None
        self.outputCollection = self.outputs[0]

    def _load_filter_module(self, filterPath):
        print(filterPath)
        tokens = filterPath.split('.')
        module_path = '.'.join(tokens[:-1])
        function = tokens[-1]
        mod = import_module(module_path)
        return getattr(mod, function)

    def produce(self, event):
        if hasattr(event, self.outputCollection):
            return True
        nJets = event[self.prefix + 'nJets']
        jets = []
        for i in range(nJets):
            jet = Jet(event, i, self.prefix)
            if self.jetFilter:
                if not self.jetFilter(jet):
                    continue
                jet.usedFilter = self.jetFilter.__name__
            jets.append(jet)

        # sort by ET, largest first
        sorted_jets = sorted(
            jets,
            key=lambda jet: jet[jet.sortBy],
            reverse=True,
        )

        setattr(event, self.outputCollection, sorted_jets)
        return True
