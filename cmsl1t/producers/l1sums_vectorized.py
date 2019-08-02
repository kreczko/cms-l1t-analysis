import ROOT

from cmsl1t.energySums import EnergySum, Mex, Mey, Met
from .base import BaseProducer


class Producer(BaseProducer):
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

    def __init__(self, inputs, outputs, **kwargs):
        self._expected_input_order = ['sumBx', 'type', 'et', 'phi']
        super(Producer, self).__init__(inputs, outputs, **kwargs)

    def produce(self, event):
        variables = [event[i] for i in self._inputs]
        energySumTypes = Producer.energySumTypes
        prefix = self._outputs[0] + '_'

        for sumBx, sumType, et, phi in zip(*variables):
            bx_mask = sumBx == 0
            for energyType in energySumTypes:
                type_mask = sumType == energyType
                if not any(type_mask):
                    continue
                name = energySumTypes[energyType]['name']
                obj = energySumTypes[energyType]['type']
                if obj == Met:
                    setattr(event, prefix + name, obj(et[bx_mask], phi[bx_mask]))
                else:
                    setattr(event, prefix + name, obj(et[bx_mask]))

        return True
