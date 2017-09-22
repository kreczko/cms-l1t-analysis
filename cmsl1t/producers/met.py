import math
import numpy as np


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
