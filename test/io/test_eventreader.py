
from cmsl1t.io.eventreader import EventReader, Event
from collections import namedtuple
from nose2.tools import such

CaloTree = namedtuple('CaloTree', ['CaloTP', 'L1CaloCluster'])
CaloTP = namedtuple('CaloTP', ['ecalTPCaliphi', 'ecalTPcompEt'])
CaloCluster = namedtuple('CaloCluster', ['et', 'eta'])

with such.A('EventReader') as it:
    @it.has_setup
    def setup():
        it.caloTP = CaloTP(ecalTPCaliphi=3.14, ecalTPcompEt=50)
        it.caloCluster = CaloCluster(et=50, eta=0)
        it.caloTree = CaloTree(CaloTP=it.caloTP, L1CaloCluster=it.caloCluster)

    @it.should('map event attributes to tree attributes')
    def test_mapping():

        trees = {
            'l1CaloTowerEmuTree/L1CaloTowerTree': it.caloTree,
        }
        mapping = {
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

        event = Event(trees, mapping)
        observed = event.l1CaloTowerEmuTree_L1CaloTowerTree_CaloTP_ecalTPCaliphi
        expected = it.caloTree.CaloTP.ecalTPCaliphi
        it.assertEqual(observed, expected)
        observed = event.emu_L1CaloTowerTree_CaloTP_ecalTPCaliphi
        it.assertEqual(observed, expected)
        observed = event.emu_CaloTP_ecalTPCaliphi
        it.assertEqual(observed, expected)

it.createTests(globals())
