from mock import patch
import unittest
from cmsl1t.filters.luminosity import _load_json, _expand_lumi_range, \
    _expand_lumi_ranges, LuminosityFilter
import json
import numpy as np

EXAMPLE_JSON = {"273158": [[1, 12]], "273302": [[1, 4]]}


class MockResponse(object):

    def __init__(self, resp_data, code=200, msg='OK'):
        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = {'content-type': 'text/plain; charset=utf-8'}

    def read(self):
        return self.resp_data

    def getcode(self):
        return self.code


class TestLumiFilter(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('six.moves.urllib.request.urlopen')
        self.urlopen_mock = self.patcher.start()

    def test_load_json(self):
        self.urlopen_mock.return_value = MockResponse(json.dumps(EXAMPLE_JSON))
        result = _load_json('dummy')
        self.assertEqual(result, EXAMPLE_JSON)

    def test_expand_lumirange(self):
        input_range = np.array([1, 4])
        expected_result = np.array([1, 2, 3, 4])
        result = _expand_lumi_range(input_range)
        self.assertTrue((result == expected_result).all())

    def test_expand_lumiranges(self):
        input_ranges = np.array([[1, 4], [10, 12]])
        expected_result = np.array([1, 2, 3, 4, 10, 11, 12])
        result = _expand_lumi_ranges(input_ranges)
        self.assertTrue((result == expected_result).all())

    def test_lumifilter_init(self):
        self.urlopen_mock.return_value = MockResponse(json.dumps(EXAMPLE_JSON))
        lumiFilter = LuminosityFilter('dummy')
        self.assertEqual(len(lumiFilter.valid_lumi_sections), 16)

    def test_lumifilter(self):
        self.urlopen_mock.return_value = MockResponse(json.dumps(EXAMPLE_JSON))
        lumiFilter = LuminosityFilter('dummy')
        self.assertTrue(lumiFilter(273158, 1))
        self.assertTrue(lumiFilter(273158, 2))
        self.assertTrue(lumiFilter(273158, 3))
        self.assertTrue(lumiFilter(273158, 12))

        self.assertTrue(lumiFilter(273302, 1))
        self.assertTrue(lumiFilter(273302, 2))
        self.assertTrue(lumiFilter(273302, 4))

        self.assertFalse(lumiFilter(273302, 5))

    def tearDown(self):
        self.patcher.stop()
