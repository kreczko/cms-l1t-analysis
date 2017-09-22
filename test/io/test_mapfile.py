from nose2.tools import such
from cmsl1t.io.mapfile import \
    default_alias, full_path_alias, shorthand_alias


with such.A('Mapfile') as it:
    @it.has_setup
    def setup():
        it.set1 = dict(
            path='l1CaloTowerEmuTree/L1CaloTowerTree',
            treeName='L1CaloTowerTree',
            objName='CaloTP.ecalTPCaliphi',
        )
        it.set2 = dict(
            path='l1MuonRecoTree/Muon2RecoTree',
            treeName='Muon2RecoTree',
            objName='Muon.isLooseMuon',
        )

    @it.should('prefix emu_ to emulator variables')
    def test_emu_prefix():
        testSet = it.set1
        observed = default_alias(**testSet)
        expected = 'event.emu_L1CaloTowerTree_CaloTP_ecalTPCaliphi'
        it.assertEqual(observed, expected)

        observed = full_path_alias(testSet['path'], testSet['objName'])
        expected = 'event.l1CaloTowerEmuTree_L1CaloTowerTree_CaloTP_ecalTPCaliphi'
        it.assertEqual(observed, expected)

        observed = shorthand_alias(**testSet)
        expected = 'event.emu_CaloTP_ecalTPCaliphi'
        it.assertEqual(observed, expected)

    @it.should('not prefix emu_ to not emulator variables')
    def test_incorrect_emu_prefix():
        testSet = it.set2
        observed = default_alias(**testSet)
        expected = 'event.Muon2RecoTree_Muon_isLooseMuon'
        it.assertEqual(observed, expected)

        observed = full_path_alias(testSet['path'], testSet['objName'])
        expected = 'event.l1MuonRecoTree_Muon2RecoTree_Muon_isLooseMuon'
        it.assertEqual(observed, expected)

        observed = shorthand_alias(**testSet)
        expected = 'event.Muon_isLooseMuon'
        it.assertEqual(observed, expected)


it.createTests(globals())
