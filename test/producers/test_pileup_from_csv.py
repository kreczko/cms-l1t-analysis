import numpy as np
import os
import pytest


import cmsl1t
from cmsl1t.producers.pileup_from_csv import Producer

from .. import DummyEvent


@pytest.fixture(params=['events', 'events_not_in_csv'])
def data(request):
    if request.param == 'events':
        return DummyEvent(
            run=[324980, 324980, 324980, 324980, 324878, 324878, 324878, 1],
            lumi=[40, 41, 42, 43, 620, 621, 622, 42],
        ), [6.4, 15.6, 36.1, 51.7, 33.4, 33.4, 33.4, 0]
    if request.param == 'events_not_in_csv':
        return DummyEvent(
            run=np.zeros(10),
            lumi=np.zeros(10),
        ), [0] * 10


def test_pileup_from_csv(data):
    events, expected = data
    run_lumi_csv = os.path.join(cmsl1t.PROJECT_ROOT, 'run_lumi.csv')
    p = Producer(inputs=['run', 'lumi'], outputs=['pileup_from_csv'], csv_file=run_lumi_csv)
    p.produce(events)
    assert hasattr(events, 'pileup_from_csv')
    assert events.pileup_from_csv.tolist() == expected
