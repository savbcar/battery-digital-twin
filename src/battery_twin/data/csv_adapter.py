from pathlib import Path

import pandas as pd


def load_timeseries_csv(
    path: str | Path,
    time_column: str,
    current_column: str,
    voltage_column: str,
) -> pd.DataFrame:
    """
    Normalize an external battery time-series CSV to the project's core schema.

    Use this adapter after converting a public dataset's native format to CSV.
    No dataset-specific sign convention is assumed: verify and convert current
    polarity before estimation.
    """
    raw = pd.read_csv(path)
    required = [time_column, current_column, voltage_column]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = pd.DataFrame(
        {
            "time_s": raw[time_column].astype(float),
            "current_measured_a": raw[current_column].astype(float),
            "voltage_measured_v": raw[voltage_column].astype(float),
        }
    )
    return out
