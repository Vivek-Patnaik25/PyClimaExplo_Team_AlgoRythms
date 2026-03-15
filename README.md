# Demo Video
Demo Video Link: https://youtu.be/vLLbw-rlnKg

# Live Deployment
Streamlit App: https://vivek-patnaik25-pyclimaexplo-team-algorythms-app-pfxhjy.streamlit.app/

# Data
You can download the climate NetCDF Files from the Repo.


# PyClima Explorer+
Intelligent Climate Analytics Platform for NetCDF datasets.

PyClima Explorer+ is a Streamlit app for interactive climate-data exploration with spatial maps, temporal analysis, ML-assisted insights, comparison workflows, story-style narration, and 3D visualization.

## Team
- Vivek Patnaik [TX262852]
- Ritesh Kumar Gouda [TX262851]
- Anurag Panigrahi [TX262846]

## What the app includes (from `app.py`)
- Student / Researcher entry views with workflow-specific defaults.
- Robust NetCDF loading (`scipy`, `netcdf4`, `h5netcdf` fallback strategy).
- Multi-file upload support for cross-dataset comparison.
- Global **Time Range** filter applied across time-based analysis.
- `Map Atlas`: animated spatial heatmaps, click-to-analyze location behavior.
- `Time Studio`: aggregated time-series, rolling averages, trend lines, anomaly markers.
- `ML Insights`:
  - Event Detector
  - Insight Layer (narrative summaries)
  - Model Comparison (forecast evaluation)
- `Compare Lab`: file-vs-file and time-step-vs-time-step comparison modes.
- `Story Mode`: guided anomaly/trend tour.
- `3D Orbit`: Plotly globe + 3D terrain surface controls.
- `Dataset Intel`: metadata, variable structure, coordinate details, raw xarray preview.

## Tech Stack
- UI: Streamlit
- Data: Xarray, NumPy, Pandas
- Visualization: Plotly
- Modeling: scikit-learn
- NetCDF engines: scipy, netCDF4, h5netcdf

## Supported Input Files
- `.nc`
- `.nc4`
- `.netcdf`
- `.cdf`

## Run Locally
### 1) Create and activate a virtual environment (recommended)
```bash
python -m venv .venv
```

Windows (PowerShell):
```bash
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Start the app
```bash
streamlit run app.py
```

Open the URL shown in terminal (usually `http://localhost:8501`).

