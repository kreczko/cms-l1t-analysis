import pytest
import six.moves.urllib as urllib

from cmsl1t.io import RemoteFile


@pytest.fixture(params=['local_file', 'remote_file'])
def file_url(request):
    if request.param == 'local_file':
        return 'run_lumi.csv'
    if request.param == 'remote_file':
        return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17' + \
            '/13TeV/PromptReco/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'


def test_access(file_url):
    with RemoteFile(file_url) as f:
        assert len(f.readlines()) > 0


def test_invalid_file_local():
    with pytest.raises(IOError) as e:
        with RemoteFile("sdfbksdjhflksdj") as _:
            pass
        assert "No such file" in str(e.value)


def test_invalid_file_remote():
    with pytest.raises(urllib.error.URLError) as e:
        with RemoteFile("http://sdfbksdjhflksdj") as _:
            pass
        assert "No such file" in str(e.value)
