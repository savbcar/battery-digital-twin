import json
import sqlite3
import uuid
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any


class SimulationLogger:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        schema = (
            files("battery_twin.database")
            .joinpath("schema.sql")
            .read_text(encoding="utf-8")
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)

    def log_run(
        self,
        config: dict[str, Any],
        metrics: dict[str, float],
        tag: str = "baseline",
    ) -> str:
        run_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO simulation_runs
                (run_id, created_utc, tag, config_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    run_id,
                    timestamp,
                    tag,
                    json.dumps(config, sort_keys=True),
                ),
            )

            conn.executemany(
                """
                INSERT INTO run_metrics
                (run_id, metric_name, metric_value)
                VALUES (?, ?, ?)
                """,
                [
                    (run_id, name, float(value))
                    for name, value in metrics.items()
                ],
            )

        return run_id