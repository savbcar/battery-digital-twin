import pytest

from battery_twin.models.ecm_1rc import (
    ECM1RC,
    ECM1RCParameters,
    ECM1RCState,
)


def model() -> ECM1RC:
    return ECM1RC(
        ECM1RCParameters(
            capacity_ah=3.0,
            r0_ohm=0.015,
            r1_ohm=0.010,
            c1_farad=2400.0,
        ),
        dt_s=1.0,
    )


def test_discharge_decreases_soc() -> None:
    m = model()
    result = m.step(ECM1RCState(0.8, 0.0), 6.0)
    expected = 0.8 - 6.0 / (3.0 * 3600.0)
    assert result.soc == pytest.approx(expected)


def test_charge_increases_soc() -> None:
    m = model()
    result = m.step(ECM1RCState(0.8, 0.0), -6.0)
    assert result.soc > 0.8


def test_polarization_relaxes_exactly() -> None:
    m = model()
    result = m.step(ECM1RCState(0.8, 0.1), 0.0)
    assert result.v1_v == pytest.approx(0.1 * m.alpha1)


def test_long_pulse_converges_to_ir1() -> None:
    m = model()
    state = ECM1RCState(0.8, 0.0)
    current = 6.0
    n = int(10.0 * m.p.tau1_s / m.dt_s)
    for _ in range(n):
        state = m.step(state, current)
    assert state.v1_v == pytest.approx(
        current * m.p.r1_ohm,
        rel=1e-3,
    )
