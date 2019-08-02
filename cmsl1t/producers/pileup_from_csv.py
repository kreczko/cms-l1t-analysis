import numpy as np
import pandas as pd

from .base import BaseProducer


def _load_csv(csv_file):
    lumiMuDict = dict()
    df = pd.read_csv(csv_file, names=['entry', 'run', 'lumi', 'pileup'], index_col=['run', 'lumi'])
    return df


class Producer(BaseProducer):

    def __init__(self, inputs, outputs, **kwargs):
        self._expected_input_order = ['run', 'lumi']
        self._run_lumi_file = kwargs.pop('csv_file')
        super(Producer, self).__init__(inputs, outputs, **kwargs)

        self._data = _load_csv(self._run_lumi_file)

    def produce(self, event):
        variables = [event[i] for i in self._inputs]

        setattr(event, self._outputs[0], self._data.loc[list(zip(*variables)), 'pileup'].fillna(0).to_numpy())
