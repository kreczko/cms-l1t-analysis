# Notes from 24th of March
```python
res[pu]['jetEt'][region].fill(jet.et()) -> res.fill('jetEt', jet.et())
```


```python
hists = MyHistCollection(pileupBins=[0, 13, 20, 999])
hists.add_variable('jetEt')
with Session(events, hists=[...]) as s:
with Session(cfg) as s:
    # expert defined
    s.run()

for event in events:
    # should this be implicit
    # hists.set_pu(pu)
    with Session(event, hists=[hists]) as s:
      s.fill(hists, 'jets[0].et()', ....)
      hists[22][region]['jetEt'].fill(events.jets[0].et())
```
Separate event loop and code to run
user defined function:

```
def myThing(event)
```

```YAML

files:
  - /eos/..../*.root
modifiers:
  recalcMET:
    func: cmsl1t.recalc.recalcMET
    in: event.caloTowers
    out: recalcMET
    kwargs:
      another: 42
      lut_file: /eos/..../myFile.lut
    args:
      - 4234
      - vksdfj

histograms:
  Resolution:
    pile_up_bins: [0, 13, 20, 999]
    variables:
      - jetEt: 'jets[0].et()'
      - jetEtvsEta:
          - 'jets[0].et()'
          - 'jets[0].eta()'
      - recalcMET: recalcMET
    filters:
      MyEventFilter:
        worksOn: event
        requires:
          met: '> 20'
  Efficiency:
    variables:
      - jetEt:
        - reco: 'jets[0].et()'
        - l1: 'l1Jets[0].et()'
        - thresholds: [20, 30, 50, 100, 200]
  Rates:
    pile_up_bins: [0, 13, 20, 999]

```

# Current L1NTuple format
15 separate trees meant to be read as one
 - l1CaloTowerTree/L1CaloTowerTree #<- in use, contains 3 trees
 - l1CaloTowerEmuTree/L1CaloTowerTree  #<- in use
 - l1ElectronRecoTree/ElectronRecoTree
 - l1EventTree/L1EventTree
 - 1JetRecoTree/JetRecoTree # <- in use
 - l1MetFilterRecoTree/MetFilterRecoTree # <- in use
 - l1MuonRecoTree/Muon2RecoTree # <- in use
 - l1RecoTree/RecoTree # <- in use
 - l1TauRecoTree/TauRecoTree
 - l1UpgradeEmuTree/L1UpgradeTree # <- in use
 - l1UpgradeTfMuonEmuTree/L1UpgradeTfMuonTree # contains 4 trees
 - l1UpgradeTfMuonTree/L1UpgradeTfMuonTree # contains 4 trees
 - l1UpgradeTree/L1UpgradeTree # <- in use
 - l1uGTEmuTree/L1uGT
 - l1uGTTree/L1uGT


# Benchmark
http://stefaanlippens.net/python_profiling_with_pstats_interactive_mode/

## DemoAnalyzer
 - regular: 436 seconds
 - vectorized: 9 seconds
