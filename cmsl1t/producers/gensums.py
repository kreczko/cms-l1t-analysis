from __future__ import division
import numpy as np
import math
from cmsl1t.energySums import EnergySum, Met
from .base import BaseProducer


class Producer(BaseProducer):

    def __init__(self, inputs, outputs, **kwargs):
        self._expected_input_order = ['jetPt', 'partId', 'partPhi', 'partPt', 'partEta', ]
        super(Producer, self).__init__(inputs, outputs, **kwargs)

    def produce(self, event):
        variables = [event[i] for i in self._inputs]
        prefix = self._outputs[0] + '_'

        jet_pt, part_id, partPhi, partPt, partEta = variables
        setattr(event, prefix + 'HT', EnergySum(np.sum(jet_pt)))

        part_id = np.absolute(part_id)
        partEta = np.absolute(partEta)
        partPhi = np.array(partPhi)
        partPt = np.array(partPt)

        # nu_e, mu, nu_mu, nu_tau
        particleMask = (part_id == 12) | (part_id == 13) | (part_id == 14) | (part_id == 16)
        eta_mask = partEta < 3.0

        genMetHF = self._calculate_met(partPt, partPhi, particleMask)
        setattr(event, prefix + 'MetHF', genMetHF)

        genMetBE = self._calculate_met(partPt, partPhi, particleMask & eta_mask)
        setattr(event, prefix + 'MetBE', genMetBE)

        return True

    def _calculate_met(self, partPt, partPhi, mask):
        met_x = np.dot(partPt[mask], np.cos(partPhi[mask]))
        met_y = np.dot(partPt[mask], np.sin(partPhi[mask]))
        met = np.sqrt(met_x ** 2 + met_y**2)
        met_phi = math.atan(met_y / met_x)
        return Met(met, met_phi)
