import numpy as np
import pandas as pd

from .base import BaseProducer
from .. import logger


def _load_csv(csv_file):
    return pd.read_csv(csv_file, names=['entry', 'run', 'lumi', 'pileup'], index_col=['run', 'lumi'])


class Producer(BaseProducer):

    def __init__(self, inputs, outputs, **kwargs):
        self._expected_input_order = ['run', 'lumi']
        self._run_lumi_file = kwargs.pop('csv_file')
        super(Producer, self).__init__(inputs, outputs, **kwargs)

        self._data = _load_csv(self._run_lumi_file)

    def produce(self, event):
        variables = [event[i] for i in self._inputs]
        pileup = np.zeros(np.size(variables[0]))
        # TODO:
        """
          /software/miniconda/envs/hep_py3/lib/python3.6/site-packages/pandas/core/indexing.py:969: FutureWarning:
          Passing list-likes to .loc or [] with any missing label will raise
          KeyError in the future, you can use .reindex() as an alternative.

          See the documentation here:
          https://pandas.pydata.org/pandas-docs/stable/indexing.html#deprecate-loc-reindex-listlike
          return self._getitem_nested_tuple(tup)

          -- Docs: https://docs.pytest.org/en/latest/warnings.html
        """
        try:
            pileup = self._data.loc[list(zip(*variables)), 'pileup'].fillna(0).to_numpy()
        except KeyError:
            logger.warning('Could not find any (run, lum) combination in {}'.format(self._run_lumi_file))
        setattr(event, self._outputs[0], pileup)

        return True
