import os

from collections import namedtuple
import pytest

import cmsl1t
from cmsl1t.io.eventreader import Event, EventReader


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


@pytest.fixture
def test_data():
    path = os.path.join(cmsl1t.PROJECT_ROOT, 'test/data/2kmu.root')
    return [path]


@pytest.fixture
def ntuple_map():
    import yaml
    path = os.path.join(cmsl1t.PROJECT_ROOT, 'config/ntuple_content_2kmu.yaml')
    with open(path) as f:
        return yaml.load(f)


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


def test_event_loop(ntuple_map, test_data):
    nevents = 10
    reader = EventReader(input_files=test_data, ntuple_map=ntuple_map, nevents=nevents, vectorized=True)
    events = list(reader)
    assert len(events) == nevents
    for event in events:
        assert event['CaloTP_ecalTPCaliphi'] is not None
        if reader._batch_size > 1:
            # we are dealing with arrays of arrays
            assert len(event['CaloTP_ecalTPCaliphi']) == reader._batch_size
        else:
            # like a simple for-loop
            assert len(event['CaloTP_ecalTPCaliphi']) > 1
