import cmsl1t.utils.fit_efficiency as fit
from rootpy.plotting import F1, Hist, Canvas
from rootpy import asrootpy, ROOT


def test_get_asymmetric_formula():
    formula = fit.get_asymmetric_formula()
    assert "{" not in formula


def test__create_output_dict_sym():
    test_func = F1("[0] + [1]", 0, 10, name="sym")
    test_func.SetParameters(1, 2)
    test_func.SetParError(0, 3)
    test_func.SetParError(1, 4)
    test_func.SetParNames("mu", "sigma_inv")
    success = False

    params = fit._create_output_dict(success, [test_func], "")

    assert not params["success"]
    assert params["mu"] == (1, 3)
    assert params["sigma_inv"] == (2, 4)
    assert params["sigma"][0] == 1. / 2
    assert params["symmetric"].name == "sym"
    assert "asymmetric" not in params


def FakeEff(in_mean, in_sigma):
    in_func = F1("TMath::Gaus(x,{},{},true)".format(in_mean, in_sigma), 0, 100)
    resolution = Hist(50, 0, 100)
    n_events = 20000000
    resolution.FillRandom(in_func.name, n_events)
    resolution.Scale(1. / n_events)
    hist = resolution.GetCumulative()
    return hist


def test_fit_efficiency_symmetric():
    in_mean = 35.
    in_sigma = 10.
    fake_efficiency = FakeEff(in_mean, in_sigma)

    params = fit.fit_efficiency(fake_efficiency, 30, 10, False)

    mu = params["mu"][0]
    sigma = params["sigma"][0]
    mu_ratio = mu / in_mean if mu > in_mean else in_mean / mu
    sigma_ratio = sigma / in_sigma if sigma > in_sigma else in_sigma / sigma
    assert 1.1 > mu_ratio
    assert 1.5 > sigma_ratio
    assert params["success"]


def test_fit_efficiency_asymmetric():
    in_mean = 35.
    in_sigma = 10.
    fake_efficiency = FakeEff(in_mean, in_sigma)

    params = fit.fit_efficiency(fake_efficiency, 30, 10, True)

    mu = params["mu"][0]
    sigma = params["sigma"][0]
    lamda = params["lambda"][0]
    mu_ratio = mu / in_mean if mu > in_mean else in_mean / mu
    sigma_ratio = sigma / in_sigma if sigma > in_sigma else in_sigma / sigma
    assert 1.1 > mu_ratio
    assert 1.5 > sigma_ratio
    assert 0.5 > abs(lamda)
    assert params["success"]
