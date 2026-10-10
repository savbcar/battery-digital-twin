from dataclasses import dataclass

import numpy as np
import pandas as pd

from battery_twin.estimators.coulomb_counter import CoulombCounter
from battery_twin.estimators.ekf_2rc import EKF2RC, EKFConfig
from battery_twin.models.ecm_2rc import ECM2RC, ECM2RCParameters, ECM2RCState
from battery_twin.models.ocv import SyntheticOCV
from battery_twin.simulation.profiles import dynamic_current_profile


@dataclass(frozen=True)
class SimulationConfig:
    dt_s: float = 1.0
    duration_s: int = 1800
    seed: int = 42
    initial_soc_true: float = 0.85
    initial_soc_est: float = 0.70
    voltage_noise_std_v: float = 0.008
    current_noise_std_a: float = 0.05


def generate_synthetic_data(
    config: SimulationConfig,
    true_params: ECM2RCParameters,
) -> pd.DataFrame:
    rng = np.random.default_rng(config.seed)
    ocv = SyntheticOCV()
    model = ECM2RC(true_params, config.dt_s, ocv)

    current_true = dynamic_current_profile(
        config.duration_s,
        config.dt_s,
        config.seed,
    )
    n = len(current_true)

    current_measured = current_true + rng.normal(
        0.0, config.current_noise_std_a, size=n
    )

    state = ECM2RCState(config.initial_soc_true, 0.0, 0.0)

    soc_true = np.empty(n)
    v1_true = np.empty(n)
    v2_true = np.empty(n)
    voltage_true = np.empty(n)

    for k in range(n):
        soc_true[k] = state.soc
        v1_true[k] = state.v1_v
        v2_true[k] = state.v2_v
        voltage_true[k] = model.terminal_voltage(state, current_true[k])
        if k < n - 1:
            state = model.step(state, current_true[k])

    voltage_measured = voltage_true + rng.normal(
        0.0, config.voltage_noise_std_v, size=n
    )

    return pd.DataFrame(
        {
            "time_s": np.arange(n, dtype=float) * config.dt_s,
            "current_true_a": current_true,
            "current_measured_a": current_measured,
            "soc_true": soc_true,
            "v1_true_v": v1_true,
            "v2_true_v": v2_true,
            "voltage_true_v": voltage_true,
            "voltage_measured_v": voltage_measured,
        }
    )


def run_ekf(
    data: pd.DataFrame,
    config: SimulationConfig,
    estimator_params: ECM2RCParameters,
    ekf_config: EKFConfig,
) -> pd.DataFrame:
    ekf = EKF2RC(
        estimator_params,
        config.dt_s,
        config.initial_soc_est,
        ekf_config,
    )

    cc = CoulombCounter(
        estimator_params.capacity_ah,
        config.dt_s,
        config.initial_soc_est,
    )

    n = len(data)
    soc_ekf = np.empty(n)
    soc_cc = np.empty(n)
    v1_est = np.empty(n)
    v2_est = np.empty(n)
    voltage_est = np.empty(n)
    innovation = np.empty(n)
    innovation_var = np.empty(n)

    current = data["current_measured_a"].to_numpy()
    voltage = data["voltage_measured_v"].to_numpy()

    for k in range(n):
        if k > 0:
            ekf.predict(float(current[k - 1]))
            cc.step(float(current[k - 1]))

        innov, s = ekf.update(float(voltage[k]), float(current[k]))

        soc_ekf[k] = ekf.x[0]
        v1_est[k] = ekf.x[1]
        v2_est[k] = ekf.x[2]
        soc_cc[k] = cc.soc
        voltage_est[k] = ekf.measurement_function(float(current[k]))
        innovation[k] = innov
        innovation_var[k] = s

    out = data.copy()
    out["soc_ekf"] = soc_ekf
    out["soc_coulomb"] = soc_cc
    out["v1_est_v"] = v1_est
    out["v2_est_v"] = v2_est
    out["voltage_est_v"] = voltage_est
    out["innovation_v"] = innovation
    out["innovation_var"] = innovation_var
    return out
