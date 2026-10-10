from dataclasses import replace
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from battery_twin.estimators.ekf_2rc import EKFConfig
from battery_twin.models.ecm_2rc import ECM2RCParameters
from battery_twin.simulation.simulator import (
    SimulationConfig,
    generate_synthetic_data,
    run_ekf,
)
from battery_twin.validation.metrics import calculate_metrics


def run_sensitivity_studies(
    base_sim: SimulationConfig,
    true_params: ECM2RCParameters,
    est_params: ECM2RCParameters,
    base_ekf: EKFConfig,
    output_dir: Path,
) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []

    def evaluate(
        study: str,
        value: float,
        sim: SimulationConfig = base_sim,
        ep: ECM2RCParameters = est_params,
        ec: EKFConfig = base_ekf,
        true_p: ECM2RCParameters = true_params,
    ) -> None:
        data = generate_synthetic_data(sim, true_p)
        result = run_ekf(data, sim, ep, ec)
        metrics = calculate_metrics(result)
        rows.append({"study": study, "value": value, **metrics})

    # 1) Initial-state error
    for initial_soc in [0.55, 0.65, 0.75, 0.85, 0.95]:
        evaluate(
            "initial_soc_est",
            initial_soc,
            sim=replace(base_sim, initial_soc_est=initial_soc),
        )

    # 2) Process-noise covariance
    for factor in [0.1, 0.3, 1.0, 3.0, 10.0]:
        evaluate(
            "q_scale",
            factor,
            ec=replace(
                base_ekf,
                q_soc=base_ekf.q_soc * factor,
                q_v1=base_ekf.q_v1 * factor,
                q_v2=base_ekf.q_v2 * factor,
            ),
        )

    # 3) Measurement-noise covariance
    for factor in [0.25, 0.5, 1.0, 2.0, 4.0]:
        evaluate(
            "r_scale",
            factor,
            ec=replace(
                base_ekf,
                r_voltage=base_ekf.r_voltage * factor,
            ),
        )

    # 4) ECM mismatch, one parameter at a time
    for name, attr in [
        ("r0_factor", "r0_ohm"),
        ("r1_factor", "r1_ohm"),
        ("c1_factor", "c1_farad"),
        ("r2_factor", "r2_ohm"),
        ("c2_factor", "c2_farad"),
    ]:
        for factor in [0.8, 0.9, 1.0, 1.1, 1.2]:
            kwargs = {attr: getattr(true_params, attr) * factor}
            evaluate(name, factor, ep=replace(est_params, **kwargs))

    # 5) Capacity mismatch
    for factor in [0.8, 0.9, 1.0, 1.1, 1.2]:
        evaluate(
            "capacity_factor",
            factor,
            ep=replace(
                est_params,
                capacity_ah=true_params.capacity_ah * factor,
            ),
        )

    # 6) Voltage sensor noise
    for sigma in [0.002, 0.005, 0.008, 0.015, 0.025]:
        evaluate(
            "voltage_noise_std_v",
            sigma,
            sim=replace(base_sim, voltage_noise_std_v=sigma),
        )

    # 7) Current sensor noise
    for sigma in [0.01, 0.03, 0.05, 0.10, 0.20]:
        evaluate(
            "current_noise_std_a",
            sigma,
            sim=replace(base_sim, current_noise_std_a=sigma),
        )

    # 8) Sampling interval
    for dt_s in [0.5, 1.0, 2.0, 5.0]:
        evaluate(
            "sampling_dt_s",
            dt_s,
            sim=replace(base_sim, dt_s=dt_s),
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(output_dir / "sensitivity_metrics.csv", index=False)

    for study in df["study"].unique():
        subset = df[df["study"] == study]
        plt.figure(figsize=(7, 4.5))
        plt.plot(
            subset["value"],
            subset["soc_rmse_pct"],
            marker="o",
        )
        plt.xlabel(study)
        plt.ylabel("SOC RMSE [%]")
        plt.title(f"Sensitivity: {study}")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            output_dir / f"sensitivity_{study}.png",
            dpi=180,
        )
        plt.close()

    return df
