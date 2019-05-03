import pytest
from cmsl1t.io.eventreader import Event
from collections import namedtuple


@pytest.fixture
def caloTree():
    CaloTree = namedtuple('CaloTree', ['CaloTP', 'L1CaloCluster'])
    CaloTP = namedtuple('CaloTP', ['ecalTPCaliphi', 'ecalTPcompEt'])
    CaloCluster = namedtuple('CaloCluster', ['et', 'eta'])
    caloTP = CaloTP(ecalTPCaliphi=3.14, ecalTPcompEt=50)
    caloCluster = CaloCluster(et=50, eta=0)
    caloTree = CaloTree(CaloTP=caloTP, L1CaloCluster=caloCluster)
    return caloTree


@pytest.fixture
def mapping():
    return {
        'l1CaloTowerEmuTree_L1CaloTowerTree_CaloTP_ecalTPCaliphi': (
            'l1CaloTowerEmuTree/L1CaloTowerTree',
            'CaloTP.ecalTPCaliphi'
        ),
        'emu_L1CaloTowerTree_CaloTP_ecalTPCaliphi': (
            'l1CaloTowerEmuTree/L1CaloTowerTree',
            'CaloTP.ecalTPCaliphi'
        ),
        'emu_CaloTP_ecalTPCaliphi': (
            'l1CaloTowerEmuTree/L1CaloTowerTree',
            'CaloTP.ecalTPCaliphi'
        ),
    }


def test_mapping(caloTree, mapping):
    trees = {
        'l1CaloTowerEmuTree/L1CaloTowerTree': caloTree,
    }
    event = Event(trees, mapping)
    observed = event.l1CaloTowerEmuTree_L1CaloTowerTree_CaloTP_ecalTPCaliphi
    expected = caloTree.CaloTP.ecalTPCaliphi
    assert observed == expected
    observed = event.emu_L1CaloTowerTree_CaloTP_ecalTPCaliphi
    assert observed == expected
    observed = event.emu_CaloTP_ecalTPCaliphi
    assert observed == expected
