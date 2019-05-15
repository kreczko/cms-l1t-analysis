import math
import numpy as np
import logging
from .base import BaseProducer

logger = logging.getLogger(__name__)


class MET(object):

    def __init__(self, metx, mety):
        self.x = metx
        self.y = mety

    @property
    def mag(self):
        return np.linalg.norm([self.x, self.y], axis=0)


def recalcMET(caloTowerIphis, caloTowerIetas, caloTowerIets, mask=None):
    validTowers = [True] * len(caloTowerIphis)
    if mask is not None:
        validTowers = mask

    ets = 0.5 * caloTowerIets[validTowers]
    phis = (math.pi / 36.0) * caloTowerIphis[validTowers]
    e_x = np.multiply(ets, np.cos(phis))
    e_y = np.multiply(ets, np.sin(phis))
    metx = -e_x.sum()
    mety = -e_y.sum()
    # TODO: this can be done better with and uproot_methods.TVector2
    return MET(metx, mety)


def l1Met28Only(caloTowerIphis, caloTowerIetas, caloTowerIets):
    return recalcMET(
        caloTowerIphis,
        caloTowerIetas,
        caloTowerIets,
        mask=abs(caloTowerIetas) == 28
    )


def l1MetNot28(caloTowerIphis, caloTowerIetas, caloTowerIets):
    return recalcMET(
        caloTowerIphis,
        caloTowerIetas,
        caloTowerIets,
        mask=abs(caloTowerIetas) >= 28,
    )


def l1MetNot28HF(caloTowerIphis, caloTowerIetas, caloTowerIets):
    return recalcMET(
        caloTowerIphis,
        caloTowerIetas,
        caloTowerIets,
        mask=abs(caloTowerIetas) != 28,
    )


class Producer(BaseProducer):

    METHODS = {
        'default': recalcMET,
        'l1Met28Only': l1Met28Only,
        'l1MetNot28': l1MetNot28,
        'l1MetNot28HF': l1MetNot28HF,
    }

    INPUT_ORDER = ['phi', 'eta', 'et']

    def __init__(self, inputs, outputs, **kwargs):
        self._expected_input_order = ['phi', 'eta', 'et']
        super(Producer, self).__init__(inputs, outputs, **kwargs)

        params = self._params
        if params and 'method' in params:
            self._method = Producer.METHODS[params['method']]
        else:
            msg = 'Could not find specified MET method, using default.'
            logger.warn(msg)
            self._method = Producer.METHODS['default']

    def produce(self, event):
        variables = [event[i] for i in self._inputs]
        met = self._method(*variables)
        setattr(event, self._outputs[0], met)
        return True
