from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def create_baseline_plots(df: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    t = df["time_s"]

    plt.figure(figsize=(10, 4.5))
    plt.plot(t, df["current_true_a"], label="True current")
    plt.xlabel("Time [s]")
    plt.ylabel("Current [A]")
    plt.title("Dynamic current profile (positive = discharge)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    _save(output_dir / "01_current_profile.png")

    plt.figure(figsize=(10, 4.5))
    plt.plot(t, 100.0 * df["soc_true"], label="True SOC")
    plt.plot(t, 100.0 * df["soc_ekf"], label="EKF SOC")
    plt.plot(t, 100.0 * df["soc_coulomb"], label="Coulomb-counted SOC")
    plt.xlabel("Time [s]")
    plt.ylabel("SOC [%]")
    plt.title("SOC estimation and initial-error convergence")
    plt.grid(True, alpha=0.3)
    plt.legend()
    _save(output_dir / "02_soc_estimation.png")

    plt.figure(figsize=(10, 4.5))
    plt.plot(t, df["voltage_measured_v"], label="Measured voltage", alpha=0.55)
    plt.plot(t, df["voltage_true_v"], label="True voltage")
    plt.plot(t, df["voltage_est_v"], label="EKF reconstructed voltage")
    plt.xlabel("Time [s]")
    plt.ylabel("Voltage [V]")
    plt.title("Terminal-voltage validation")
    plt.grid(True, alpha=0.3)
    plt.legend()
    _save(output_dir / "03_voltage_validation.png")

    plt.figure(figsize=(10, 4.5))
    plt.plot(t, 1000.0 * df["innovation_v"])
    plt.axhline(0.0, linewidth=1.0)
    plt.xlabel("Time [s]")
    plt.ylabel("Innovation [mV]")
    plt.title("EKF voltage innovation")
    plt.grid(True, alpha=0.3)
    _save(output_dir / "04_innovation.png")

    plt.figure(figsize=(10, 4.5))
    plt.plot(t, 1000.0 * df["v1_true_v"], label="True V1")
    plt.plot(t, 1000.0 * df["v1_est_v"], label="Estimated V1")
    plt.plot(t, 1000.0 * df["v2_true_v"], label="True V2")
    plt.plot(t, 1000.0 * df["v2_est_v"], label="Estimated V2")
    plt.xlabel("Time [s]")
    plt.ylabel("Polarization voltage [mV]")
    plt.title("Fast and slow polarization states")
    plt.grid(True, alpha=0.3)
    plt.legend()
    _save(output_dir / "05_polarization_states.png")
