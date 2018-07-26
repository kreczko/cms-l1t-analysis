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
        return np.linalg.norm([self.x, self.y])


def recalcMET(caloTowerIphis, caloTowerIetas, caloTowerIets, exclude=None):
    validTowers = [1] * len(caloTowerIphis)
    if exclude is not None:
        validTowers = map(exclude, caloTowerIetas)

    ets = 0.5 * np.array(caloTowerIets)[validTowers]
    phis = (math.pi / 36.0) * np.array(caloTowerIphis)[validTowers]
    metx = -sum(ets * np.cos(phis))
    mety = -sum(ets * np.sin(phis))
    return MET(metx, mety)


def l1Met28Only(caloTowerIphis, caloTowerIetas, caloTowerIets):
    return recalcMET(
        caloTowerIphis,
        caloTowerIetas,
        caloTowerIets,
        exclude=lambda towerIeta: not abs(towerIeta) == 28
    )


def l1MetNot28(caloTowerIphis, caloTowerIetas, caloTowerIets):
    return recalcMET(
        caloTowerIphis,
        caloTowerIetas,
        caloTowerIets,
        exclude=lambda towerIeta: abs(towerIeta) >= 28
    )


def l1MetNot28HF(caloTowerIphis, caloTowerIetas, caloTowerIets):
    return recalcMET(
        caloTowerIphis,
        caloTowerIetas,
        caloTowerIets,
        exclude=lambda towerIeta: abs(towerIeta) == 28
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
