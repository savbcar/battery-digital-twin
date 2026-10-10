import pytest

from battery_twin.models.ocv import SyntheticOCV


def test_ocv_increases_with_soc() -> None:
    ocv = SyntheticOCV()
    assert ocv.voltage(0.8) > ocv.voltage(0.2)


def test_analytic_derivative_matches_finite_difference() -> None:
    ocv = SyntheticOCV()
    soc = 0.6
    eps = 1e-6
    numeric = (
        ocv.voltage(soc + eps) - ocv.voltage(soc - eps)
    ) / (2.0 * eps)
    assert ocv.derivative(soc) == pytest.approx(numeric, rel=1e-6)
