import numpy as np

from battery_twin.estimators.ekf_2rc import EKF2RC, EKFConfig
from battery_twin.models.ecm_2rc import ECM2RCParameters


def params() -> ECM2RCParameters:
    return ECM2RCParameters(
        3.0, 0.012, 0.010, 2400.0, 0.006, 20000.0
    )


def test_covariance_remains_symmetric_and_positive() -> None:
    ekf = EKF2RC(params(), 1.0, 0.7, EKFConfig())
    for _ in range(20):
        ekf.predict(2.0)
        ekf.update(3.8, 2.0)
    assert np.allclose(ekf.P, ekf.P.T, atol=1e-12)
    assert np.all(np.linalg.eigvalsh(ekf.P) >= -1e-12)


def test_soc_is_bounded() -> None:
    ekf = EKF2RC(params(), 1.0, 0.5, EKFConfig())
    ekf.update(10.0, 0.0)
    assert 0.0 <= ekf.soc <= 1.0
