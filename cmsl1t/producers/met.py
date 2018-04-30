import math
import numpy as np
import logging

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


class Producer(object):

    METHODS = {
        'default': recalcMET,
        'l1Met28Only': l1Met28Only,
        'l1MetNot28': l1MetNot28,
        'l1MetNot28HF': l1MetNot28HF,
    }

    INPUT_ORDER = ['phi', 'eta', 'et']

    def __init__(self, inputs, outputs, params):
        self.inputs = inputs
        self.outputs = outputs
        self.params = params

        self.prefix = self.inputs[0].replace('*', '')
        if params and 'method' in params:
            self.method = Producer.METHODS[params['method']]
        else:
            msg = 'Could not find specified MET method, using default.'
            logger.warn(msg)
            self.method = Producer.METHODS['default']
        self.outputCollection = self.outputs[0]

        if not self._check_inputs():
            logger.error('Unexpected input order.')
            logger.error('Expected order' + ','.join(Producer.INPUT_ORDER))
            logger.error('Got' + ','.join(self.input))

    def _check_inputs(self):
        for o, i in zip(self.INPUT_ORDER, self.inputs):
            if not i.endswith(o):
                return False
        return True

    def produce(self, event):
        if hasattr(event, self.outputCollection):
            return True
        variables = [event[i] for i in self.inputs]
        met = self.method(*variables)
        setattr(event, self.outputCollection, met)
        return True
