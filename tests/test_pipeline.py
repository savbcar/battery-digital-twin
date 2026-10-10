from battery_twin.estimators.ekf_2rc import EKFConfig
from battery_twin.models.ecm_2rc import ECM2RCParameters
from battery_twin.simulation.simulator import (
    SimulationConfig,
    generate_synthetic_data,
    run_ekf,
)
from battery_twin.validation.metrics import calculate_metrics


def test_end_to_end_estimator_reduces_large_initial_soc_error() -> None:
    sim = SimulationConfig(
        duration_s=600,
        initial_soc_true=0.85,
        initial_soc_est=0.65,
        seed=7,
    )
    p = ECM2RCParameters(
        3.0, 0.012, 0.010, 2400.0, 0.006, 20000.0
    )
    data = generate_synthetic_data(sim, p)
    out = run_ekf(data, sim, p, EKFConfig())
    initial_error = abs(out["soc_ekf"].iloc[0] - out["soc_true"].iloc[0])
    final_error = abs(out["soc_ekf"].iloc[-1] - out["soc_true"].iloc[-1])
    assert final_error < initial_error
    metrics = calculate_metrics(out)
    assert metrics["soc_rmse_pct"] < 10.0
