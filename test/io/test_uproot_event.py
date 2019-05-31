import numpy as np
import pytest

from cmsl1t.io.eventreader import UprootEvent


@pytest.fixture
def data_and_mapping():
    data = dict(
        exampleTree=dict(
            a=np.array([1, 3, 5]),
        )
    )
    m = {
        'a': ('exampleTree', 'a'),
    }
    return data, m


@pytest.fixture
def event(data_and_mapping):
    data, mapping = data_and_mapping
    return UprootEvent(data, mapping, batch_size=3)


@pytest.mark.parametrize(
    "mask",
    [
        ([True, True, True]),
        ([True, False, True]),
        ([False, False, False]),
    ])
def test_mask(event, data_and_mapping, mask):
    data, mapping = data_and_mapping

    expected = data['exampleTree']['a'][mask].tolist()
    result = event.mask(mask).a.tolist()

    assert result == expected


def test_invalid_mask(event, data_and_mapping):
    data, mapping = data_and_mapping
    with pytest.raises(ValueError):
        event.mask(True)

    with pytest.raises(ValueError):
        event.mask([True])
