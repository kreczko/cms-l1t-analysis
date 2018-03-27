from nose.tools import (raises, assert_equal, assert_almost_equal,
                        assert_raises, assert_true, assert_false)
from nose.plugins.attrib import attr


import pyfakefs.fake_filesystem as fake_fs
import pyfakefs.fake_filesystem_glob as fake_glob

try:
    from unittest.mock import patch  # In Python 3, mock is built-in
except ImportError:
    from mock import patch

from cmsl1t.utils.root_glob import glob as root_glob
import pytest

# Create a faked file system
fs = fake_fs.FakeFilesystem()

# Do some setup on the faked file system
fs.CreateFile('/tmp/l1t/L1Ntuple_1.root')
fs.CreateFile('/tmp/l1t/L1Ntuple_2.root')
fs.CreateFile('/tmp/l1t/L1Ntuple_3.root')

glob = fake_glob.FakeGlobModule(fs)


def test_glob_local_single():
    with patch('glob.glob', glob.glob):
        filename = "/tmp/l1t/L1Ntuple_3.root"
        assert_equal(root_glob(filename), [filename])


def test_glob_local_wildcard():
    with patch('glob.glob', glob.glob):
        filename = "/tmp/l1t/*.root"
        from glob import glob as py_glob
        assert_equal(root_glob(filename), py_glob(filename))


def test_glob_local_multiple_wildcards():
    with patch('glob.glob', glob.glob):
        filename = "/tmp/l*/*.root"
        from glob import glob as py_glob
        assert_equal(root_glob(filename), py_glob(filename))


@pytest.mark.xrootdtest
def test_glob_xrootd_single():
    filename = "root://lcgse01.phy.bris.ac.uk///cms/store/PhEDEx_LoadTest07/"\
        "LoadTest07_Debug_T2_UK_SGrid_Bristol/LoadTest07_SouthGrid_Bristol_3B"
    assert_equal(root_glob(filename), [filename])


@pytest.mark.xrootdtest
def test_glob_xrootd_wildcard():
    filename = "root://lcgse01.phy.bris.ac.uk///cms/store/PhEDEx_LoadTest07/"\
        "LoadTest07_Debug_T2_UK_SGrid_Bristol/*"
    assert_equal(len(root_glob(filename)), 256)
