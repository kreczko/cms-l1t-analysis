import pytest
from cmsl1t.io.mapfile import \
    default_alias, full_path_alias, shorthand_alias


@pytest.fixture
def caloTree():
    return dict(
        path='l1CaloTowerEmuTree/L1CaloTowerTree',
        treeName='L1CaloTowerTree',
        objName='CaloTP.ecalTPCaliphi',
    )


@pytest.fixture
def muonTree():
    return dict(
        path='l1MuonRecoTree/Muon2RecoTree',
        treeName='Muon2RecoTree',
        objName='Muon.isLooseMuon',
    )


def test_emu_prefix(caloTree):
    observed = default_alias(**caloTree)
    expected = 'event.emu_L1CaloTowerTree_CaloTP_ecalTPCaliphi'
    assert observed == expected
    observed = full_path_alias(caloTree['path'], caloTree['objName'])
    expected = 'event.l1CaloTowerEmuTree_L1CaloTowerTree_CaloTP_ecalTPCaliphi'
    assert observed == expected
    observed = shorthand_alias(**caloTree)
    expected = 'event.emu_CaloTP_ecalTPCaliphi'
    assert observed == expected


def test_incorrect_emu_prefix(muonTree):
    observed = default_alias(**muonTree)
    expected = 'event.Muon2RecoTree_Muon_isLooseMuon'
    assert observed == expected
    observed = full_path_alias(muonTree['path'], muonTree['objName'])
    expected = 'event.l1MuonRecoTree_Muon2RecoTree_Muon_isLooseMuon'
    assert observed == expected
    observed = shorthand_alias(**muonTree)
    expected = 'event.Muon_isLooseMuon'
    assert observed == expected
