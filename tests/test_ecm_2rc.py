import pytest

from battery_twin.models.ecm_2rc import (
    ECM2RC,
    ECM2RCParameters,
    ECM2RCState,
)


def test_two_time_constants_are_respected() -> None:
    p = ECM2RCParameters(
        3.0, 0.01, 0.01, 1000.0, 0.02, 5000.0
    )
    m = ECM2RC(p, 1.0)
    state = ECM2RCState(0.8, 0.1, 0.1)
    nxt = m.step(state, 0.0)
    assert nxt.v1_v == pytest.approx(0.1 * m.alpha1)
    assert nxt.v2_v == pytest.approx(0.1 * m.alpha2)
    assert nxt.v2_v > nxt.v1_v
