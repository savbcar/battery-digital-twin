# START HERE — Savio's Click-by-Click Build/Run Guide

This repository is already complete. Your job is to run it, inspect it, understand
it, and then publish it under your own GitHub account.

## Part A — Open it in VS Code on Windows

1. Install Python 3.12 if it is not installed.
2. Install Git.
3. Install VS Code.
4. In VS Code, install the "Python" extension by Microsoft.
5. Extract the repository ZIP somewhere simple, for example:
   `C:\Users\<you>\Documents\battery-digital-twin`
6. Open VS Code.
7. Click **File → Open Folder**.
8. Select `battery-digital-twin`.
9. Click **Terminal → New Terminal**.
10. Make sure the terminal says PowerShell.

## Part B — Create the isolated Python environment

Copy-paste exactly:

```powershell
py -3.12 -m venv .venv
```

Then:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Your prompt should now begin with `(.venv)`.

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the project plus developer tools:

```powershell
pip install -e ".[dev]"
```

## Part C — Prove the code is healthy

Run:

```powershell
pytest
```

Expected: all tests pass.

Then:

```powershell
ruff check src tests
```

Expected: no lint errors.

## Part D — Run the complete project

Run:

```powershell
battery-twin all
```

This performs:

1. synthetic 2-RC truth simulation,
2. noisy current/voltage sensing,
3. 2-RC EKF estimation,
4. Coulomb-counting baseline,
5. quantitative validation,
6. result plots,
7. SQLite logging,
8. all robustness/sensitivity studies.

Open:

```text
results/generated/baseline/
```

Inspect in this order:

1. `01_current_profile.png`
2. `02_soc_estimation.png`
3. `03_voltage_validation.png`
4. `04_innovation.png`
5. `05_polarization_states.png`
6. `metrics.json`
7. `timeseries.csv`

Then open:

```text
results/generated/sensitivity/
```

Inspect every `sensitivity_*.png` and `sensitivity_metrics.csv`.

## Part E — What every baseline plot should mean

### 1. Current profile

Positive current is discharge. Negative current is regenerative charging.

### 2. SOC plot

Truth starts at 85%.
EKF intentionally starts at 70%.
Coulomb counting also starts at 70%.

The EKF should rapidly move toward truth because voltage corrects the hidden state.
The coulomb counter should retain approximately the initial offset because it has
no voltage correction.

### 3. Voltage plot

The model should reproduce:
- immediate R0 drop at current changes,
- slower RC polarization,
- relaxation after load removal,
- OCV evolution with SOC.

### 4. Innovation

Innovation = measured voltage - predicted voltage.

A healthy innovation should fluctuate around approximately zero without a large
persistent bias.

### 5. Polarization states

V1 and V2 represent two characteristic transient time scales.

## Part F — Open the code in the correct learning order

Do NOT read randomly.

1. `src/battery_twin/models/ocv.py`
2. `src/battery_twin/models/ecm_1rc.py`
3. `tests/test_ecm_1rc.py`
4. `src/battery_twin/models/ecm_2rc.py`
5. `src/battery_twin/simulation/profiles.py`
6. `src/battery_twin/simulation/simulator.py`
7. `src/battery_twin/estimators/coulomb_counter.py`
8. `src/battery_twin/estimators/ekf_2rc.py`
9. `src/battery_twin/validation/metrics.py`
10. `src/battery_twin/validation/studies.py`
11. `src/battery_twin/database/sqlite_logger.py`
12. `docs/ENGINEERING_NOTES.md`
13. `docs/RESULTS.md`
14. `docs/INTERVIEW_PREP.md`

## Part G — Inspect the SQL database

The simplest GUI route:

1. In VS Code Extensions, install a SQLite viewer extension.
2. Open `results/battery_runs.db`.
3. Inspect tables:
   - `simulation_runs`
   - `run_metrics`

Or use Python:

```powershell
python -c "import sqlite3; c=sqlite3.connect('results/battery_runs.db'); print(c.execute('SELECT run_id,created_utc,tag FROM simulation_runs ORDER BY created_utc DESC LIMIT 5').fetchall())"
```

## Part H — Docker

Install Docker Desktop.

From the repository root:

```powershell
docker build -t battery-digital-twin .
```

Then:

```powershell
docker run --rm -v "${PWD}/results:/app/results" battery-digital-twin all
```

Alternative:

```powershell
docker compose up --build
```

This proves the Python project can run from a reproducible container instead of
depending on your laptop's global Python environment.

## Part I — MATLAB

Open MATLAB.

Set the Current Folder to:

```text
battery-digital-twin\matlab
```

Run:

```matlab
run_demo
```

Read:
- `battery_params.m`
- `ocv_from_soc.m`
- `simulate_2rc.m`
- `ekf_soc_2rc.m`

Do not claim Python/MATLAB numerical equivalence until you have run both locally
and compared their traces, because their random profile generation is not
identical in this repository.

## Part J — Simulink

From MATLAB in the `matlab` folder run:

```matlab
build_simulink_1rc
```

It creates:

```text
battery_1rc_generated.slx
```

Open the generated model.

Trace the SOC path and V1 path manually. Explain every Gain, Sum and Unit Delay.

The generated artifact is intentionally transparent rather than using a black-box
battery block.

## Part K — Git and GitHub

Create a new empty GitHub repository named:

```text
battery-digital-twin
```

Do NOT initialize it with a README because this project already has one.

Back in VS Code PowerShell:

```powershell
git init
git add .
git commit -m "Initial EV battery digital twin and EKF platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/battery-digital-twin.git
git push -u origin main
```

Open GitHub → Actions.

The CI workflow should install the project, run Ruff, run pytest and execute a
baseline smoke test.

## Part L — What you may truthfully put on your CV after you personally run it

Use the verified repository metrics only for the deterministic synthetic benchmark.
Do not present them as production-cell accuracy.

Suggested bullets are in `docs/RESULTS.md` and the main README.

## Part M — Your defense rule

Before applying with this project, you must be able to derive on paper:

1. dSOC/dt
2. 1-RC V1 ODE
3. exact ZOH V1 discretization
4. 2-RC state vector
5. F and B
6. voltage measurement h(x,u)
7. H Jacobian
8. EKF predict
9. innovation
10. Kalman gain
11. correction
12. Joseph covariance update

Then complete `docs/INTERVIEW_PREP.md` without vague answers.

That is when this becomes YOUR engineering project rather than code you merely own.
