from pathlib import Path
from typing import Any

import yaml

from battery_twin.estimators.ekf_2rc import EKFConfig
from battery_twin.models.ecm_2rc import ECM2RCParameters
from battery_twin.simulation.simulator import SimulationConfig


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_config(
    path: Path,
) -> tuple[
    SimulationConfig,
    ECM2RCParameters,
    ECM2RCParameters,
    EKFConfig,
    dict[str, Any],
]:
    raw = load_config(path)
    sim = SimulationConfig(**raw["simulation"])
    true_model = ECM2RCParameters(**raw["true_model"])
    estimator_model = ECM2RCParameters(**raw["estimator_model"])
    ekf = EKFConfig(**raw["ekf"])
    return sim, true_model, estimator_model, ekf, raw
