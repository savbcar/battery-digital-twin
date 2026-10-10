import math

import numpy as np
import pandas as pd


def rmse(error: np.ndarray) -> float:
    return float(np.sqrt(np.mean(error**2)))


def mae(error: np.ndarray) -> float:
    return float(np.mean(np.abs(error)))


def convergence_time(
    time_s: np.ndarray,
    error: np.ndarray,
    threshold: float = 0.02,
    hold_s: float = 60.0,
) -> float:
    if len(time_s) < 2:
        return math.nan

    dt = float(np.median(np.diff(time_s)))
    hold_n = max(1, int(round(hold_s / dt)))
    good = np.abs(error) <= threshold

    for i in range(0, len(good) - hold_n + 1):
        if bool(np.all(good[i : i + hold_n])):
            return float(time_s[i])

    return math.nan


def calculate_metrics(df: pd.DataFrame) -> dict[str, float]:
    soc_error = (
        df["soc_ekf"].to_numpy()
        - df["soc_true"].to_numpy()
    )
    cc_error = (
        df["soc_coulomb"].to_numpy()
        - df["soc_true"].to_numpy()
    )
    voltage_error = (
        df["voltage_est_v"].to_numpy()
        - df["voltage_true_v"].to_numpy()
    )

    tail_n = max(1, int(0.2 * len(df)))

    return {
        "soc_rmse_pct": 100.0 * rmse(soc_error),
        "soc_mae_pct": 100.0 * mae(soc_error),
        "soc_max_abs_error_pct": 100.0 * float(np.max(np.abs(soc_error))),
        "soc_final_error_pct": 100.0 * float(soc_error[-1]),
        "soc_steady_mae_pct": 100.0 * mae(soc_error[-tail_n:]),
        "soc_convergence_time_s": convergence_time(
            df["time_s"].to_numpy(),
            soc_error,
            threshold=0.02,
            hold_s=60.0,
        ),
        "coulomb_soc_rmse_pct": 100.0 * rmse(cc_error),
        "voltage_rmse_mv": 1000.0 * rmse(voltage_error),
        "voltage_mae_mv": 1000.0 * mae(voltage_error),
        "innovation_mean_mv": 1000.0 * float(
            np.mean(df["innovation_v"].to_numpy())
        ),
        "innovation_std_mv": 1000.0 * float(
            np.std(df["innovation_v"].to_numpy())
        ),
    }
