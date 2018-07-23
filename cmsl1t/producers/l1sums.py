from __future__ import print_function
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

    def __init__(self, inputs, outputs, params):
        self._expected_input_order = ['sumBx', 'type', 'et', 'phi']
        super(Producer, self).__init__(inputs, outputs, params)

    def produce(self, event):
        variables = [event[i] for i in self._inputs]
        energySumTypes = Producer.energySumTypes
        prefix = self._outputs[0] + '_'

        for sumBx, sumType, et, phi in zip(*variables):
            if sumBx != 0:
                continue
            if sumType in energySumTypes:
                name = energySumTypes[sumType]['name']
                obj = energySumTypes[sumType]['type']
                if obj == Met:
                    setattr(event, prefix + name, obj(et, phi))
                else:
                    setattr(event, prefix + name, obj(et))

        return True
