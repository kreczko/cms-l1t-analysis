import ROOT

from cmsl1t.energySums import EnergySum, Mex, Mey, Met
from . import _init_values


class Producer(object):
    sumTypes = ROOT.l1t.EtSum
    energySumTypes = {
        sumTypes.kTotalEt: {'name': 'Ett', 'type': EnergySum},
        sumTypes.kTotalEtHF: {'name': 'EttHF', 'type': EnergySum},
        sumTypes.kTotalHt: {'name': 'Htt', 'type': EnergySum},
        sumTypes.kTotalHtHF: {'name': 'HttHF', 'type': Met},
        sumTypes.kMissingEt: {'name': 'Met', 'type': Met},
        sumTypes.kMissingEtHF: {'name': 'MetHF', 'type': Met},
        sumTypes.kMissingHt: {'name': 'Mht', 'type': Met},
        sumTypes.kTotalEtx: {'name': 'Mex', 'type': Mex},
        sumTypes.kTotalEty: {'name': 'Mey', 'type': Mey},
    }

    def __init__(self, inputs, outputs, params):
        self.inputs = inputs
        self.outputs = outputs
        self.params = params
        self.values = {}
        self.outputCollection = self.outputs[0]

    def produce(self, event):
        values = _init_values(self.inputs, event)
        sums = {}
        energySumTypes = Producer.energySumTypes
        prefix = self.outputCollection + '_'

        for sumType, et, phi in zip(values['type'], values['et'], values['phi']):
            if sumType in energySumTypes:
                name = energySumTypes[sumType]['name']
                obj = energySumTypes[sumType]['type']
                if obj == Met:
                    setattr(event, prefix + name, obj(et, phi))
                    sums[prefix + name] = obj(et, phi)
                else:
                    setattr(event, prefix + name, obj(et))

        return True
