import argparse
import json
from pathlib import Path

from battery_twin.config import parse_config
from battery_twin.database.sqlite_logger import SimulationLogger
from battery_twin.simulation.simulator import generate_synthetic_data, run_ekf
from battery_twin.validation.metrics import calculate_metrics
from battery_twin.validation.plots import create_baseline_plots
from battery_twin.validation.studies import run_sensitivity_studies


def run_baseline(config_path: Path, output_root: Path) -> dict[str, float]:
    sim, true_p, est_p, ekf_cfg, raw = parse_config(config_path)

    baseline_dir = output_root / "generated" / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)

    data = generate_synthetic_data(sim, true_p)
    result = run_ekf(data, sim, est_p, ekf_cfg)
    metrics = calculate_metrics(result)

    result.to_csv(baseline_dir / "timeseries.csv", index=False)
    (baseline_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )
    create_baseline_plots(result, baseline_dir)

    logger = SimulationLogger(output_root / "battery_runs.db")
    run_id = logger.log_run(raw, metrics, tag="baseline")

    print(f"Baseline run ID: {run_id}")
    print(json.dumps(metrics, indent=2))
    return metrics


def run_studies(config_path: Path, output_root: Path) -> None:
    sim, true_p, est_p, ekf_cfg, _ = parse_config(config_path)
    study_dir = output_root / "generated" / "sensitivity"
    study_df = run_sensitivity_studies(
        sim,
        true_p,
        est_p,
        ekf_cfg,
        study_dir,
    )
    print(f"Completed {len(study_df)} sensitivity runs.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="EV Battery Digital Twin & SOC Estimation Platform"
    )
    parser.add_argument(
        "command",
        choices=["baseline", "studies", "all"],
        nargs="?",
        default="all",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/default.yaml"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
    )
    args = parser.parse_args()

    if args.command in {"baseline", "all"}:
        run_baseline(args.config, args.output)
    if args.command in {"studies", "all"}:
        run_studies(args.config, args.output)


if __name__ == "__main__":
    main()
