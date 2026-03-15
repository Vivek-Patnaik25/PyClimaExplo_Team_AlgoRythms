import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import xarray as xr
import io
import os
from datetime import datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PyClima Explorer +",
    page_icon="🌏🌏🌏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  — dark, crisp, scientific theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700;800&display=swap');
:root {
  --bg-0: #050814;
  --bg-1: #0b1021;
  --bg-2: #121a31;
  --glass: rgba(13, 19, 36, 0.70);
  --glass-2: rgba(21, 31, 56, 0.72);
  --line: rgba(116, 159, 255, 0.24);
  --line-strong: rgba(116, 212, 255, 0.45);
  --text: #e9f2ff;
  --muted: #8fa4c7;
  --electric: #55a6ff;
  --cyan: #2dd4bf;
  --amber: #f59e0b;
  --lime: #22c55e;
  --rose: #f43f5e;
}
html, body, [class*="css"] {
  color: var(--text) !important;
  font-family: 'Sora', sans-serif !important;
}
h1, h2, h3 {
  font-family: 'Space Mono', monospace !important;
  letter-spacing: 0.01em;
}
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1200px 600px at 85% -5%, rgba(59, 130, 246, 0.17), transparent 70%),
    radial-gradient(900px 500px at -10% 18%, rgba(45, 212, 191, 0.10), transparent 65%),
    linear-gradient(160deg, var(--bg-0) 0%, var(--bg-1) 46%, #0c1429 100%) !important;
  background-attachment: fixed !important;
}
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(500px 220px at 18% 88%, rgba(34, 197, 94, 0.08), transparent 72%),
    radial-gradient(420px 200px at 88% 78%, rgba(245, 158, 11, 0.06), transparent 72%);
  mix-blend-mode: screen;
  animation: drift 16s ease-in-out infinite alternate;
  z-index: 0;
}
@keyframes drift {
  from { transform: translateY(0px) scale(1); opacity: 0.72; }
  to   { transform: translateY(-16px) scale(1.02); opacity: 1; }
}
section.main > div {
  position: relative;
  z-index: 1;
}
.block-container {
  padding-top: 1.4rem !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(12, 18, 34, 0.95), rgba(10, 14, 28, 0.94)) !important;
  border-right: 1px solid rgba(114, 154, 255, 0.20);
  box-shadow: 10px 0 45px rgba(2, 6, 18, 0.50);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stFileUploader"] {
  background: linear-gradient(180deg, rgba(19, 30, 55, 0.78), rgba(14, 22, 40, 0.82)) !important;
  border: 1.5px dashed rgba(82, 163, 255, 0.58) !important;
  border-radius: 14px !important;
}
[data-testid="metric-container"] {
  background: linear-gradient(160deg, rgba(18, 28, 51, 0.84), rgba(14, 22, 42, 0.76)) !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  padding: 1rem !important;
  box-shadow: 0 14px 30px rgba(5, 11, 27, 0.34), inset 0 0 0 1px rgba(255, 255, 255, 0.03);
  transition: transform 0.2s ease, border-color 0.2s ease;
}
[data-testid="metric-container"]:hover {
  transform: translateY(-2px);
  border-color: var(--line-strong) !important;
}
.stButton > button {
  border: 1px solid rgba(124, 184, 255, 0.44) !important;
  border-radius: 11px !important;
  background: linear-gradient(135deg, #2d6be6, #1d4ed8) !important;
  color: #eef4ff !important;
  font-weight: 700 !important;
  letter-spacing: 0.01em;
  box-shadow: 0 10px 30px rgba(28, 78, 216, 0.34);
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  transform: translateY(-1px) scale(1.01);
  box-shadow: 0 16px 32px rgba(37, 99, 235, 0.45);
  filter: saturate(1.08);
}
.stSelectbox > div > div,
.stSlider > div,
div[data-baseweb="select"] > div {
  background: rgba(20, 30, 54, 0.88) !important;
  border-color: rgba(112, 154, 255, 0.28) !important;
  color: var(--text) !important;
  border-radius: 11px !important;
}
.stTabs [data-baseweb="tab-list"] {
  background: rgba(11, 18, 35, 0.58) !important;
  border: 1px solid rgba(118, 170, 255, 0.19) !important;
  border-radius: 14px !important;
  padding: 0.28rem !important;
  gap: 0.25rem;
  backdrop-filter: blur(8px);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 10px !important;
  padding: 0.52rem 0.86rem !important;
  color: var(--muted) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 0.77rem !important;
  border: 1px solid transparent !important;
  transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: #c3dcff !important;
  background: rgba(42, 65, 108, 0.35) !important;
}
.stTabs [aria-selected="true"] {
  color: #edf5ff !important;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.48), rgba(6, 182, 212, 0.35)) !important;
  border: 1px solid rgba(117, 197, 255, 0.52) !important;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.10), 0 8px 24px rgba(9, 30, 78, 0.42);
}
.stAlert {
  border-radius: 12px !important;
  border: 1px solid rgba(114, 169, 255, 0.24) !important;
  background: rgba(15, 22, 41, 0.88) !important;
}
[data-testid="stPlotlyChart"],
[data-testid="stDeckGlJsonChart"] {
  background: linear-gradient(180deg, rgba(14, 21, 40, 0.86), rgba(11, 17, 32, 0.78)) !important;
  border: 1px solid rgba(102, 153, 255, 0.22) !important;
  border-radius: 18px !important;
  padding: 0.3rem !important;
  box-shadow: 0 18px 36px rgba(4, 9, 21, 0.42);
}
[data-testid="stPlotlyChart"] > div,
[data-testid="stDeckGlJsonChart"] > div {
  border-radius: 14px !important;
  overflow: hidden !important;
}
.card {
  background: linear-gradient(160deg, rgba(17, 27, 50, 0.90), rgba(13, 21, 39, 0.82));
  border: 1px solid rgba(116, 167, 255, 0.18);
  border-radius: 14px;
  padding: 1.1rem 1.25rem;
  margin-bottom: 0.95rem;
  box-shadow: 0 14px 28px rgba(4, 10, 23, 0.36);
  transition: transform 0.18s ease, border-color 0.2s ease;
}
.card:hover {
  transform: translateY(-2px);
  border-color: rgba(119, 199, 255, 0.36);
}
[data-testid="metric-container"],
[data-testid="stPlotlyChart"],
[data-testid="stDeckGlJsonChart"],
.hero,
.card {
  animation: riseIn 420ms cubic-bezier(.22, .61, .36, 1) both;
}
@keyframes riseIn {
  from { opacity: 0; transform: translateY(8px) scale(0.99); }
  to   { opacity: 1; transform: translateY(0px) scale(1); }
}
.card-accent { border-left: 3px solid var(--electric); }
.card-warn   { border-left: 3px solid var(--amber); }
.card-success{ border-left: 3px solid var(--lime); }
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  backdrop-filter: blur(6px);
}
.badge-blue  { background: rgba(59,130,246,.15); color: #9fcbff; border: 1px solid rgba(59,130,246,.35); }
.badge-cyan  { background: rgba(6,182,212,.14); color: #82f5ff; border: 1px solid rgba(6,182,212,.34); }
.badge-green { background: rgba(16,185,129,.14); color: #8cf6bd; border: 1px solid rgba(16,185,129,.32); }
.badge-amber { background: rgba(245,158,11,.16); color: #ffd782; border: 1px solid rgba(245,158,11,.35); }
.badge-red   { background: rgba(239,68,68,.15); color: #ffb0ba; border: 1px solid rgba(239,68,68,.32); }
.insight-box {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(45, 212, 191, 0.09));
  border: 1px solid rgba(103, 184, 255, 0.35);
  border-radius: 13px;
  padding: 0.95rem 1.15rem;
  margin: 0.6rem 0;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
}
.hero {
  background:
    linear-gradient(140deg, rgba(9, 20, 44, 0.94) 0%, rgba(18, 45, 83, 0.82) 46%, rgba(9, 28, 39, 0.90) 100%),
    radial-gradient(380px 180px at 15% 12%, rgba(45, 212, 191, 0.16), transparent 75%);
  border: 1px solid rgba(114, 172, 255, 0.26);
  border-radius: 18px;
  padding: 2rem 2.4rem;
  margin-bottom: 1.15rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 24px 48px rgba(5, 11, 26, 0.48);
  isolation: isolate;
}
.hero::before {
  content: "";
  position: absolute;
  top: -45%;
  right: -12%;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(85, 166, 255, 0.18) 0%, transparent 67%);
  animation: pulse 6.8s ease-in-out infinite;
  z-index: -1;
}
.hero::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 18px;
  background: linear-gradient(115deg, transparent 20%, rgba(255,255,255,0.08) 38%, transparent 56%);
  transform: translateX(-120%);
  animation: sheen 7s ease-in-out infinite;
  pointer-events: none;
}
.hero-kicker {
  display: inline-flex;
  align-items: center;
  gap: 0.42rem;
  padding: 0.22rem 0.56rem;
  border-radius: 999px;
  border: 1px solid rgba(120, 196, 255, 0.35);
  background: rgba(14, 29, 54, 0.52);
  color: #b8d9ff;
  text-transform: uppercase;
  letter-spacing: 0.11em;
  font-size: 0.64rem;
  font-family: 'Space Mono', monospace;
  margin-bottom: 0.8rem;
}
.hero-title {
  font-family: 'Space Mono', monospace;
  font-size: clamp(1.35rem, 2.6vw, 2.15rem);
  line-height: 1.18;
  font-weight: 700;
  margin: 0 0 0.46rem 0;
  color: #f5f9ff;
}
.hero-title-accent {
  background: linear-gradient(90deg, #7cbcff, #63e7d6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-copy {
  color: #a8bedf;
  margin: 0;
  font-size: 0.95rem;
  max-width: 860px;
}
.hero-rail {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
  gap: 0.55rem;
}
.hero-node {
  border: 1px solid rgba(112, 171, 255, 0.26);
  border-radius: 12px;
  background: rgba(12, 22, 43, 0.58);
  padding: 0.58rem 0.72rem;
}
.hero-node-label {
  display: block;
  font-size: 0.63rem;
  text-transform: uppercase;
  letter-spacing: 0.10em;
  color: #89a4c8;
  margin-bottom: 0.25rem;
}
.hero-node-value {
  display: block;
  font-size: 0.95rem;
  font-weight: 700;
  color: #e7f1ff;
}
@keyframes pulse {
  0%, 100% { opacity: 0.7; transform: scale(1); }
  50%      { opacity: 1; transform: scale(1.08); }
}
@keyframes sheen {
  0%, 24%   { transform: translateX(-120%); }
  54%, 100% { transform: translateX(120%); }
}
.stRadio [role="radiogroup"] {
  background: rgba(18, 28, 52, 0.52);
  border: 1px solid rgba(117, 176, 255, 0.26);
  border-radius: 12px;
  padding: 0.42rem 0.52rem;
}
.stRadio label {
  border-radius: 9px;
  padding: 0.25rem 0.45rem;
}
[data-testid="stDataFrame"] {
  border: 1px solid rgba(112, 164, 255, 0.26);
  border-radius: 12px;
  overflow: hidden;
}
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
::-webkit-scrollbar-track {
  background: rgba(8, 13, 24, 0.75);
}
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(89, 149, 255, 0.7), rgba(45, 212, 191, 0.58));
  border-radius: 999px;
  border: 1px solid rgba(184, 220, 255, 0.16);
}
@media (max-width: 900px) {
  .hero { padding: 1.35rem 1.1rem; }
  .stTabs [data-baseweb="tab"] { font-size: 0.72rem !important; padding: 0.46rem 0.62rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_netcdf(file_bytes: bytes, filename: str) -> xr.Dataset:
    """
    Universal NetCDF loader — handles:
      • NetCDF3 / NetCDF4 / HDF5 (tries scipy → netcdf4 → h5netcdf)
      • Non-standard / cftime calendars (360-day, all_leap, julian…)
      • Files where time decode fails (falls back to decode_times=False)
      • Windows file-lock issue (writes to temp file, closes before unlink)
    """
    import tempfile, os
    suffix = os.path.splitext(filename)[-1] or ".nc"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp_path = tmp.name
    try:
        tmp.write(file_bytes)
        tmp.close()

        last_err = None
        # Try every engine × decode_times combination
        attempts = [
            (engine, decode)
            for engine in ["scipy", "netcdf4", "h5netcdf"]
            for decode in [True, False]          # False = cftime/exotic calendar fallback
        ]
        for engine, decode_times in attempts:
            try:
                open_kw = dict(engine=engine, decode_times=decode_times)
                if not decode_times:
                    # Also mask & scale so values are still numeric
                    open_kw["mask_and_scale"] = True
                with xr.open_dataset(tmp_path, **open_kw) as ds:
                    # Convert cftime coords to pandas-compatible numeric where possible
                    if not decode_times:
                        for coord in list(ds.coords):
                            try:
                                ds[coord] = ds[coord].astype("float64")
                            except Exception:
                                pass
                    ds.load()
                    ds_mem = ds.copy(deep=True)
                return ds_mem
            except Exception as exc:
                last_err = exc
                continue

        raise ValueError(
            f"Could not open '{filename}' with any engine or time-decode strategy. "
            f"Last error: {last_err}"
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def list_climate_vars(ds: xr.Dataset) -> list[str]:
    """Return data variables (skip coordinate-only vars)."""
    skip = {"time_bnds","lat_bnds","lon_bnds","area"}
    return [v for v in ds.data_vars if v not in skip]


def detect_lat_lon(ds: xr.Dataset):
    """Heuristic lat/lon coord detection."""
    lat_candidates = ["lat","latitude","LAT","LATITUDE","y"]
    lon_candidates = ["lon","longitude","LON","LONGITUDE","x"]
    lat = next((c for c in lat_candidates if c in ds.coords), None)
    lon = next((c for c in lon_candidates if c in ds.coords), None)
    return lat, lon


def detect_time(ds: xr.Dataset):
    time_candidates = ["time","TIME","t"]
    return next((c for c in time_candidates if c in ds.coords), None)


def slice_dataset_time(ds_in: xr.Dataset, start_idx: int, end_idx: int) -> xr.Dataset:
    """Safely slice dataset along detected time coordinate, if present."""
    tdim = detect_time(ds_in)
    if not tdim or tdim not in ds_in.coords:
        return ds_in
    tlen = len(ds_in[tdim])
    if tlen <= 1:
        return ds_in
    s = max(0, min(int(start_idx), tlen - 1))
    e = max(s, min(int(end_idx), tlen - 1))
    return ds_in.isel({tdim: slice(s, e + 1)})


def get_2d_slice(da: xr.DataArray, lat_dim: str, lon_dim: str) -> xr.DataArray:
    """Collapse everything except lat/lon by taking mean."""
    dims_to_avg = [d for d in da.dims if d not in (lat_dim, lon_dim)]
    if dims_to_avg:
        da = da.mean(dim=dims_to_avg)
    return da


def anomaly_detection(series: np.ndarray, threshold: float = 2.0):
    """Z-score based anomaly detection."""
    mean, std = np.nanmean(series), np.nanstd(series)
    if std == 0:
        return np.zeros_like(series, dtype=bool)
    z = np.abs((series - mean) / std)
    return z > threshold


def trend_analysis(series: np.ndarray):
    """Linear regression trend."""
    x = np.arange(len(series))
    mask = ~np.isnan(series)
    if mask.sum() < 2:
        return 0, 0
    coeffs = np.polyfit(x[mask], series[mask], 1)
    return coeffs[0], coeffs[1]   # slope, intercept


def plotly_dark_layout(title="", height=420):
    return dict(
        title=title,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.6)",
        font=dict(color="#e2e8f0", family="DM Sans"),
        xaxis=dict(gridcolor="#1e2d45", zerolinecolor="#1e2d45"),
        yaxis=dict(gridcolor="#1e2d45", zerolinecolor="#1e2d45"),
        margin=dict(l=50, r=30, t=50, b=40),
    )


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
if "entry_selected_view" not in st.session_state:
    st.session_state.entry_selected_view = "Student"
if "selected_view" not in st.session_state:
    st.session_state.selected_view = st.session_state.entry_selected_view
if "view_gate_passed" not in st.session_state:
    st.session_state.view_gate_passed = False
if not st.session_state.view_gate_passed:
    st.markdown("""
    <div class="hero">
      <span class="hero-kicker">Launch Console</span>
      <h1 class="hero-title">Choose Your Lens:
        <span class="hero-title-accent">Student</span> or
        <span class="hero-title-accent">Researcher</span>
      </h1>
      <p class='hero-copy'>
        Choose your experience before entering the platform.
      </p>
      <div class="hero-rail">
        <div class="hero-node"><span class="hero-node-label">Data Native</span><span class="hero-node-value">NetCDF + Xarray</span></div>
        <div class="hero-node"><span class="hero-node-label">Visual Stack</span><span class="hero-node-value">2D + 3D + Globe</span></div>
        <div class="hero-node"><span class="hero-node-label">Core Engine</span><span class="hero-node-value">Insight + ML</span></div>
        <div class="hero-node"><span class="hero-node-label">Mode Switch</span><span class="hero-node-value">Instant Toggle</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    vcol1, vcol2 = st.columns(2)
    with vcol1:
        st.markdown("""
        <div class="card card-accent">
          <div style='font-size:1.7rem; margin-bottom:.45rem;'>Student View</div>
          <div style='color:#94a3b8; font-size:.86rem; line-height:1.6;'>
            Learn climate data exploration with guided context while keeping all tools available.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with vcol2:
        st.markdown("""
        <div class="card card-success">
          <div style='font-size:1.7rem; margin-bottom:.45rem;'>Researcher View</div>
          <div style='color:#94a3b8; font-size:.86rem; line-height:1.6;'>
            Jump into full analysis workflows with research-focused messaging and controls.
          </div>
        </div>
        """, unsafe_allow_html=True)
    selected_entry_view = st.radio(
        "Select a view to continue",
        ["Student", "Researcher"],
        horizontal=True,
        key="entry_selected_view",
    )
    bcol1, bcol2, bcol3 = st.columns([1, 1.1, 1])
    with bcol2:
        if st.button("Proceed to Dashboard", use_container_width=True, type="primary"):
            st.session_state.selected_view = selected_entry_view
            st.session_state.view_gate_passed = True
            st.rerun()
    st.stop()
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.45rem 0;'>
      <span style='display:inline-block; padding:4px 10px; border:1px solid rgba(112,170,255,.35);
                   border-radius:999px; font-size:.62rem; letter-spacing:.12em; text-transform:uppercase;
                   color:#9ac6ff; background:rgba(14,26,52,.55); margin-bottom:.45rem;'>
        Climate Console
      </span><br>
      <span style='font-family:Space Mono,monospace; font-size:1.28rem; font-weight:700;
                   background:linear-gradient(90deg,#7bbcff,#63e7d6); -webkit-background-clip:text;
                   -webkit-text-fill-color:transparent;'>
        PyClima Explorer+
      </span><br>
      <span style='font-size:0.69rem; color:#7f96ba; letter-spacing:.1em; text-transform:uppercase;'>
        Visual Analytics Lab
      </span>
    </div>
    <hr style='border-color:rgba(116,168,255,.24); margin:0.72rem 0;'>
    """, unsafe_allow_html=True)

    active_view = st.session_state.get("selected_view", "Student")
    view_badge = "badge-cyan" if active_view == "Student" else "badge-green"
    st.markdown(
        f"<div style='margin-bottom:.6rem;'><span class='badge {view_badge}'>{active_view} View</span></div>",
        unsafe_allow_html=True,
    )
    if st.button("Switch View", use_container_width=True, key="switch_view_btn"):
        st.session_state.view_gate_passed = False
        st.rerun()

    st.markdown("### 📂 Data Input")
    uploaded_files = st.file_uploader(
        "Upload NetCDF file(s)",
        type=["nc", "nc4", "netcdf", "cdf"],
        accept_multiple_files=True,
        help="Drag & drop one or more .nc / .nc4 NetCDF climate files"
    )

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    if active_view == "Student":
        st.caption("Student mode: guided defaults and simplified control ranges.")
        anomaly_thresh = st.slider(
            "Anomaly Z-score threshold",
            1.0, 4.0, 2.4, 0.2,
            key="anomaly_thresh_student",
            help="Higher values flag fewer anomalies. Student mode uses wider step sizes.",
        )
        colorscale = st.selectbox(
            "Heatmap colorscale",
            ["RdYlBu_r", "Viridis", "Plasma"],
            index=0,
            key="colorscale_student",
        )
        show_grid = st.checkbox("Show map grid lines", value=False, key="show_grid_student")
        with st.expander("Student quick start", expanded=True):
            st.write("1) Upload one sample file.")
            st.write("2) Explore Spatial Map, then Temporal Analysis.")
            st.write("3) Use ML Insights to interpret anomalies.")
    else:
        st.caption("Researcher mode: wider parameter ranges and analysis-first defaults.")
        anomaly_thresh = st.slider(
            "Anomaly Z-score threshold",
            0.5, 6.0, 2.0, 0.1,
            key="anomaly_thresh_researcher",
            help="Lower values are more sensitive. Researcher mode supports a wider range.",
        )
        colorscale = st.selectbox(
            "Heatmap colorscale",
            ["RdYlBu_r", "Plasma", "Viridis", "Thermal", "Jet", "Turbo", "Cividis", "Inferno", "Magma"],
            index=0,
            key="colorscale_researcher",
        )
        show_grid = st.checkbox("Show map grid lines", value=True, key="show_grid_researcher")
        with st.expander("Research workflow", expanded=False):
            st.write("Use Comparison for multi-dataset checks.")
            st.write("Use ML Insights and Story Mode for event narratives.")
            st.write("Use 3D View for spatial diagnostics.")

    st.markdown("---")
    st.markdown("### 🗂️ Sample NetCDF Files")
    st.markdown("""
    <div style='font-size:0.8rem; color:#94a3b8; margin-bottom:.5rem;'>
      Click any link to download directly — no login required.
    </div>
    """, unsafe_allow_html=True)

    nc_files = [
        ("🌡️ Air Temp (NCEP)", "air.mon.mean.nc", "~30 MB · monthly · global",
         "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/surface/air.mon.mean.nc"),
        ("🌊 Sea Surface Temp", "sst.mnmean.nc", "~30 MB · monthly · 1854–now",
         "https://downloads.psl.noaa.gov/Datasets/noaa.ersst.v5/sst.mnmean.nc"),
        ("🌧️ Precipitation", "precip.mon.mean.nc", "~10 MB · monthly · global",
         "https://downloads.psl.noaa.gov/Datasets/cmap/enh/precip.mon.mean.nc"),
        ("💨 U-Wind 850hPa", "uwnd.mon.mean.nc", "~25 MB · monthly · winds",
         "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/pressure/uwnd.mon.mean.nc"),
        ("📊 Xarray example", "air_temperature.nc", "~2 MB · tiny · great for testing",
         "https://github.com/pydata/xarray/raw/main/ci/requirements/air_temperature.nc"),
    ]

    for icon_name, fname, desc, url in nc_files:
        st.markdown(
            f"""<div style='background:#111827; border:1px solid #1e2d45; border-radius:8px;
                       padding:.55rem .8rem; margin-bottom:.4rem;'>
              <a href='{url}' target='_blank'
                 style='color:#60a5fa; font-weight:600; font-size:.82rem;
                        text-decoration:none;'>
                ⬇ {icon_name}
              </a><br>
              <span style='color:#475569; font-size:.72rem;'>{fname} · {desc}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#64748b; line-height:1.7;'>
      <b style='color:#94a3b8;'>Team Algorythms</b><br>
      Vivek Patnaik · Ritesh Kumar Gouda · Anurag Panigrahi<br><br>
      HACK-IT OUT · TECHNEX FEST<br>
      IIT (BHU) Varanasi · 2026
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN AREA — HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <span class="hero-kicker">PyClima Explorer+</span>
  <h2 class="hero-title">Climate Intelligence,
    <span class="hero-title-accent">Reimagined</span>
  </h2>
  <p class="hero-copy">
    Transform raw NetCDF signals into decision-ready climate intelligence:
    spatial diagnostics, temporal drift analysis, anomaly mining, comparison workflows, and immersive 3D context.
  </p>
  <div style='margin-top:1rem; display:flex; gap:.5rem; flex-wrap:wrap;'>
    <span class="badge badge-blue">NetCDF Native</span>
    <span class="badge badge-cyan">3D Visualisation</span>
    <span class="badge badge-green">ML Insights</span>
    <span class="badge badge-amber">Story Mode</span>
    <span class="badge badge-red">Anomaly Detector</span>
  </div>
  <div class="hero-rail">
    <div class="hero-node"><span class="hero-node-label">Spatial Domain</span><span class="hero-node-value">Global Grid Analysis</span></div>
    <div class="hero-node"><span class="hero-node-label">Temporal Domain</span><span class="hero-node-value">Trend + Event Timeline</span></div>
    <div class="hero-node"><span class="hero-node-label">ML Layer</span><span class="hero-node-value">Detection + Forecast</span></div>
    <div class="hero-node"><span class="hero-node-label">Visual Layer</span><span class="hero-node-value">2D Maps + 3D Surface</span></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  NO FILE UPLOADED — landing state
# ─────────────────────────────────────────────
active_view = st.session_state.get("selected_view", "Student")
if active_view == "Student":
    st.info("Student View active. Guided defaults are enabled, with all features still available.")
else:
    st.info("Researcher View active. Advanced control ranges are enabled, with all features available.")
if not uploaded_files:
    if active_view == "Student":
        st.markdown("##### Suggested start: Spatial Map -> Temporal Analysis -> ML Insights")
    else:
        st.markdown("##### Suggested start: Comparison -> ML Insights -> 3D View")
    col1, col2, col3 = st.columns(3)
    cards = [
        ("🗺️", "Spatial Visualization", "Global heatmaps of temperature, precipitation, and anomaly distributions.", "badge-blue"),
        ("📈", "Temporal Analysis", "Time-series graphs for any location with ML-powered trend lines.", "badge-cyan"),
        ("🤖", "ML Pattern Detection", "Automatic Z-score anomaly detection and long-term trend analysis.", "badge-green"),
    ]
    for col, (icon, title, desc, badge) in zip([col1,col2,col3], cards):
        with col:
            st.markdown(f"""
            <div class="card card-accent">
              <div style='font-size:1.8rem; margin-bottom:.5rem;'>{icon}</div>
              <div style='font-weight:700; font-size:1rem; margin-bottom:.4rem;'>{title}</div>
              <div style='color:#94a3b8; font-size:.85rem; line-height:1.6;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    cards2 = [
        ("🕹️", "Story Mode", "Guided narrative exploration of key climate patterns and events.", "badge-amber"),
        ("⚖️", "Comparison Mode", "Side-by-side dataset comparison across years or variables.", "badge-blue"),
        ("🌐", "3D Globe", "Interactive Plotly-based 3-D climate exploration.", "badge-cyan"),
    ]
    for col, (icon, title, desc, badge) in zip([col1,col2,col3], cards2):
        with col:
            st.markdown(f"""
            <div class="card">
              <div style='font-size:1.8rem; margin-bottom:.5rem;'>{icon}</div>
              <div style='font-weight:700; font-size:1rem; margin-bottom:.4rem;'>{title}</div>
              <div style='color:#94a3b8; font-size:.85rem; line-height:1.6;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.info("⬅️  Upload one or more NetCDF (.nc / .nc4) files using the sidebar to begin.")
    st.stop()


# ─────────────────────────────────────────────
#  LOAD DATASETS
# ─────────────────────────────────────────────
datasets: dict[str, xr.Dataset] = {}
load_errors = []

with st.spinner("🔄 Loading NetCDF datasets…"):
    for f in uploaded_files:
        try:
            raw_bytes = bytes(f.read())
            ds = load_netcdf(raw_bytes, f.name)
            datasets[f.name] = ds
        except Exception as e:
            load_errors.append((f.name, str(e)))

if load_errors:
    for fname, err in load_errors:
        st.error(f"❌ Could not load **{fname}**: {err}")

if not datasets:
    st.stop()

# Dataset selector (if multiple)
ds_name = st.selectbox("Active dataset", list(datasets.keys()), key="ds_sel") if len(datasets) > 1 else list(datasets.keys())[0]
ds_raw = datasets[ds_name]

# Global time range filter (applies to all time-based plots)
time_filter_enabled = False
time_filter_start_idx = 0
time_filter_end_idx = 0

time_dim_raw = detect_time(ds_raw)
if time_dim_raw and time_dim_raw in ds_raw.coords and len(ds_raw[time_dim_raw]) > 1:
    t_all_vals = ds_raw[time_dim_raw].values
    t_len_all = len(t_all_vals)
    try:
        t_all_labels = [str(pd.Timestamp(v).date()) for v in t_all_vals]
    except Exception:
        t_all_labels = [f"Step {i}" for i in range(t_len_all)]

    with st.sidebar:
        st.markdown("---")
        st.markdown("### Time Range")
        tf_on_key = f"time_filter_on::{ds_name}"
        tf_range_key = f"time_filter_range::{ds_name}"
        time_filter_enabled = st.checkbox(
            "Apply time range to all plots",
            value=False,
            key=tf_on_key,
            help="Limits all time-based Plotly charts to the selected start/end window.",
        )
        if time_filter_enabled:
            time_filter_start_idx, time_filter_end_idx = st.slider(
                "Window",
                0,
                t_len_all - 1,
                value=(0, t_len_all - 1),
                key=tf_range_key,
            )
            st.caption(
                f"{t_all_labels[time_filter_start_idx]} -> {t_all_labels[time_filter_end_idx]}"
            )
        else:
            time_filter_start_idx, time_filter_end_idx = 0, t_len_all - 1

ds = (
    slice_dataset_time(ds_raw, time_filter_start_idx, time_filter_end_idx)
    if time_filter_enabled
    else ds_raw
)

lat_dim, lon_dim = detect_lat_lon(ds)
time_dim = detect_time(ds)
variables = list_climate_vars(ds)

if time_dim and time_dim in ds.coords:
    max_t_idx = max(0, len(ds[time_dim]) - 1)
    for idx_key in ["map_frame", "globe_frame", "cmp_ta", "cmp_tb"]:
        if idx_key in st.session_state:
            st.session_state[idx_key] = int(min(max(st.session_state[idx_key], 0), max_t_idx))

if time_filter_enabled and time_dim and time_dim in ds.coords:
    t_vals_f = ds[time_dim].values
    try:
        t_start_lbl = str(pd.Timestamp(t_vals_f[0]).date())
        t_end_lbl = str(pd.Timestamp(t_vals_f[-1]).date())
    except Exception:
        t_start_lbl = "start"
        t_end_lbl = "end"
    st.info(f"Time filter active: {t_start_lbl} -> {t_end_lbl} ({len(t_vals_f)} steps).")

# ─── Dataset overview metrics ───────────────
st.markdown("### 📋 Dataset Overview")
m_cols = st.columns(5)
with m_cols[0]:
    st.metric("Variables", len(variables))
with m_cols[1]:
    lat_n = len(ds[lat_dim]) if lat_dim else "—"
    st.metric("Lat points", lat_n)
with m_cols[2]:
    lon_n = len(ds[lon_dim]) if lon_dim else "—"
    st.metric("Lon points", lon_n)
with m_cols[3]:
    if time_dim and time_dim in ds.coords:
        t_arr = ds[time_dim].values
        st.metric("Time steps", len(t_arr))
    else:
        st.metric("Time steps", "—")
with m_cols[4]:
    size_mb = sum(ds[v].nbytes for v in variables) / 1e6
    st.metric("Data size", f"{size_mb:.1f} MB")

# ─────────────────────────────────────────────
#  VARIABLE SELECTOR (shared)
# ─────────────────────────────────────────────
if not variables:
    st.warning("No data variables found in this dataset.")
    st.stop()

sel_var = st.selectbox("🔬 Climate variable", variables, key="var_sel")
da_raw = ds[sel_var]

if active_view == "Student":
    st.markdown(
        "<div class='insight-box'><b>Student workflow:</b> Start with Spatial Map, "
        "click a location, then verify the trend in Temporal Analysis.</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div class='insight-box'><b>Researcher workflow:</b> Start with Comparison + ML Insights, "
        "then inspect high-signal regions in 3D View.</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
if active_view == "Student":
    tab_labels = [
        "Map Atlas",
        "Time Studio",
        "ML Insights (Guided)",
        "Compare Lab",
        "Story Mode",
        "3D Orbit",
        "Dataset Intel",
    ]
else:
    tab_labels = [
        "Map Atlas",
        "Time Studio",
        "ML Insights (Advanced)",
        "Compare Lab (Research)",
        "Story Mode",
        "3D Orbit",
        "Dataset Intel",
    ]
tabs = st.tabs(tab_labels)

# ══════════════════════════════════════════════
#  TAB 1 — SPATIAL MAP  (Time Slider + Play + Click-to-Analyze)
# ══════════════════════════════════════════════
with tabs[0]:
    if lat_dim is None or lon_dim is None:
        st.warning("Could not detect latitude/longitude coordinates.")
    else:
        lats = ds[lat_dim].values
        lons = ds[lon_dim].values
        has_time = bool(time_dim and time_dim in da_raw.dims)
        t_len_map = len(ds[time_dim]) if has_time else 1

        # ── Try to format time labels nicely ───────────────────────────
        if has_time:
            t_raw_vals = ds[time_dim].values
            try:
                t_fmt = [str(pd.Timestamp(v).date()) for v in t_raw_vals]
            except Exception:
                t_fmt = [str(i) for i in range(t_len_map)]
        else:
            t_fmt = ["(no time)"]

        # ── Session state: current frame & play state ───────────────────
        if "map_frame"   not in st.session_state: st.session_state.map_frame   = 0
        if "map_playing" not in st.session_state: st.session_state.map_playing = False

        # ── Controls row ────────────────────────────────────────────────
        ctrl_l, ctrl_mid, ctrl_r = st.columns([2, 6, 2])

        with ctrl_l:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            play_label = "⏹ Stop" if st.session_state.map_playing else "▶ Play"
            if st.button(play_label, key="play_btn", width='stretch'):
                st.session_state.map_playing = not st.session_state.map_playing
                st.rerun()

        with ctrl_mid:
            if has_time:
                # Always display slider at current frame position.
                # When playing, the slider is display-only (user drag is ignored).
                frame_choice = st.slider(
                    "🕐 Time", 0, t_len_map - 1,
                    value=int(st.session_state.map_frame),
                    format="%d",
                    help="Drag to jump to a time step · Press ▶ Play to animate",
                    disabled=st.session_state.map_playing,
                )
                # Only update from slider when not playing (play loop owns frame)
                if not st.session_state.map_playing:
                    st.session_state.map_frame = int(frame_choice)
            else:
                st.session_state.map_frame = 0
                frame_choice = 0

        with ctrl_r:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            anim_speed = st.selectbox("Speed", ["Slow", "Normal", "Fast"],
                                      index=1, key="anim_spd", label_visibility="collapsed")
        speed_map = {"Slow": 0.6, "Normal": 0.28, "Fast": 0.08}
        frame_delay = speed_map[anim_speed]

        # ── Current label ───────────────────────────────────────────────
        cur_label = t_fmt[st.session_state.map_frame] if has_time else ""
        st.markdown(
            f"<div style='text-align:center; font-family:Space Mono,monospace; "
            f"font-size:1.05rem; color:#3b82f6; margin:-6px 0 6px 0;'>"
            f"📅 {cur_label} &nbsp;|&nbsp; Step {st.session_state.map_frame+1} / {t_len_map}"
            f"</div>", unsafe_allow_html=True
        )

        # ── Get 2-D slice for current frame ─────────────────────────────
        def get_frame(frame_idx):
            if has_time:
                da_f = da_raw.isel({time_dim: frame_idx})
                return get_2d_slice(da_f, lat_dim, lon_dim).values.astype(float)
            return get_2d_slice(da_raw, lat_dim, lon_dim).values.astype(float)

        # Compute global color range once (so colours don't jump during animation)
        @st.cache_data(show_spinner=False)
        def get_global_range(ds_name_key, var_key, t_start_idx, t_end_idx):
            sample_indices = np.linspace(0, t_len_map-1, min(t_len_map, 12), dtype=int)
            samples = [get_frame(i) for i in sample_indices]
            arr = np.concatenate([s.flatten() for s in samples])
            arr = arr[~np.isnan(arr)]
            return float(np.percentile(arr, 2)), float(np.percentile(arr, 98))

        vmin_global, vmax_global = get_global_range(
            ds_name,
            sel_var,
            time_filter_start_idx,
            time_filter_end_idx,
        )

        z = get_frame(st.session_state.map_frame)

        # ── Main layout: map + sidebar panel ────────────────────────────
        col_map, col_side = st.columns([3, 1])

        with col_map:
            map_placeholder = st.empty()

            def render_map(z_data, title_suffix=""):
                fig_m = go.Figure(go.Heatmap(
                    z=z_data, x=lons, y=lats,
                    colorscale=colorscale,
                    zmin=vmin_global, zmax=vmax_global,
                    colorbar=dict(
                        title=dict(text=f"{sel_var} ({da_raw.attrs.get('units','?')})",
                                   side="right"),
                        tickfont=dict(color="#e2e8f0"),
                        thickness=14,
                    ),
                    hovertemplate=(
                        "<b>Lat:</b> %{y:.2f}°  <b>Lon:</b> %{x:.2f}°<br>"
                        "<b>Value:</b> %{z:.3f}<br>"
                        "<i>Click to analyse this location</i>"
                        "<extra></extra>"
                    ),
                ))
                fig_m.update_layout(
                    **plotly_dark_layout(
                        f"🌍 {sel_var}{title_suffix}",
                        height=440
                    ),
                    xaxis_title="Longitude",
                    yaxis_title="Latitude",
                    xaxis_showgrid=show_grid,
                    yaxis_showgrid=show_grid,
                    clickmode="event",
                )
                return fig_m

            # Render map — capture click events
            click_data = map_placeholder.plotly_chart(
                render_map(z, f" — {cur_label}"),
                width='stretch',
                on_select="rerun",
                key="main_heatmap",
            )

        with col_side:
            flat = z[~np.isnan(z)].flatten()
            fig_hist = go.Figure(go.Histogram(
                x=flat, nbinsx=35,
                marker_color="#3b82f6",
                marker_line=dict(color="#0f172a", width=0.4),
            ))
            _hist_layout = plotly_dark_layout("", height=200)
            _hist_layout["margin"] = dict(l=30, r=10, t=20, b=30)
            fig_hist.update_layout(**_hist_layout, showlegend=False, bargap=0.04)
            st.plotly_chart(fig_hist, width='stretch')

            st.markdown(f"""
            <div class="card" style='padding:.75rem 1rem; font-size:.82rem; margin-top:0;'>
              <b style='color:#94a3b8;'>Frame stats</b><br>
              <span style='color:#e2e8f0;'>Min</span>
              <span style='float:right; color:#60a5fa;'>{np.nanmin(flat):.3f}</span><br>
              <span style='color:#e2e8f0;'>Max</span>
              <span style='float:right; color:#f87171;'>{np.nanmax(flat):.3f}</span><br>
              <span style='color:#e2e8f0;'>Mean</span>
              <span style='float:right;'>{np.nanmean(flat):.3f}</span><br>
              <span style='color:#e2e8f0;'>Std</span>
              <span style='float:right;'>{np.nanstd(flat):.3f}</span>
            </div>
            """, unsafe_allow_html=True)

            # Anomaly overlay
            if st.checkbox("Anomaly overlay", key="anom_spatial"):
                mean_z, std_z = np.nanmean(z), np.nanstd(z)
                anom_z = np.where(np.abs(z - mean_z) > anomaly_thresh * std_z, z, np.nan)
                fig_anom = go.Figure(go.Heatmap(
                    z=anom_z, x=lons, y=lats,
                    colorscale="Reds", showscale=False,
                ))
                _anom_layout = plotly_dark_layout("Anomalies", 200)
                _anom_layout["margin"] = dict(l=20, r=10, t=30, b=20)
                fig_anom.update_layout(**_anom_layout)
                st.plotly_chart(fig_anom, width='stretch')
                n_anom = int(np.sum(~np.isnan(anom_z)))
                st.markdown(
                    f"<div class='insight-box' style='font-size:.8rem;'>"
                    f"🔴 <b>{n_anom:,}</b> anomalous cells "
                    f"({100*n_anom/z.size:.1f}%)</div>",
                    unsafe_allow_html=True
                )

        # ════════════════════════════════════════
        #  📍 CLICK-TO-ANALYZE
        # ════════════════════════════════════════
        clicked_lat, clicked_lon = None, None

        # on_select="rerun" returns a dict with "selection" key
        if click_data and hasattr(click_data, "selection"):
            sel = click_data.selection
            pts = sel.get("points", []) if isinstance(sel, dict) else []
            if pts:
                clicked_lat = pts[0].get("y")
                clicked_lon = pts[0].get("x")

        if clicked_lat is not None and clicked_lon is not None:
            st.session_state["clicked_lat"] = float(clicked_lat)
            st.session_state["clicked_lon"] = float(clicked_lon)

        if "clicked_lat" in st.session_state and has_time:
            c_lat = st.session_state["clicked_lat"]
            c_lon = st.session_state["clicked_lon"]

            st.markdown("---")
            st.markdown(
                f"<div style='font-family:Space Mono,monospace; font-size:1rem; "
                f"color:#06b6d4; margin-bottom:.5rem;'>"
                f"📍 Climate Impact Explorer — "
                f"<b>{c_lat:.2f}°{'N' if c_lat>=0 else 'S'}, "
                f"{c_lon:.2f}°{'E' if c_lon>=0 else 'W'}</b></div>",
                unsafe_allow_html=True,
            )

            # Extract nearest grid point time series
            point_da = da_raw.sel(
                {lat_dim: c_lat, lon_dim: c_lon}, method="nearest"
            )
            ts_local = point_da.values.astype(float).flatten()
            actual_lat = float(ds[lat_dim].sel({lat_dim: c_lat}, method="nearest").values)
            actual_lon = float(ds[lon_dim].sel({lon_dim: c_lon}, method="nearest").values)

            t_vals_l = ds[time_dim].values
            try:
                t_axis_l = pd.to_datetime(t_vals_l)
            except Exception:
                t_axis_l = np.arange(len(ts_local))

            slope_l, intercept_l = trend_analysis(ts_local)
            anom_l = anomaly_detection(ts_local, anomaly_thresh)
            trend_l = slope_l * np.arange(len(ts_local)) + intercept_l
            units_l = da_raw.attrs.get("units", "")

            # ── Metric cards ─────────────────────────────────────────
            mc1, mc2, mc3, mc4, mc5 = st.columns(5)
            mc1.metric("📍 Grid lat",    f"{actual_lat:.2f}°")
            mc2.metric("📍 Grid lon",    f"{actual_lon:.2f}°")
            mc3.metric("Trend",
                       "↑ Rising" if slope_l > 0 else "↓ Falling",
                       f"{slope_l:+.4f}/step")
            mc4.metric("Total change",  f"{slope_l*len(ts_local):+.3f} {units_l}")
            mc5.metric("Anomalies",     f"{int(anom_l.sum())}",
                       f"{100*anom_l.mean():.1f}% of record")

            # ── Local time series chart ───────────────────────────────
            fig_local = go.Figure()
            fig_local.add_trace(go.Scatter(
                x=t_axis_l, y=ts_local,
                mode="lines", name=f"{sel_var} @ ({actual_lat:.1f}°,{actual_lon:.1f}°)",
                line=dict(color="#06b6d4", width=2),
            ))
            fig_local.add_trace(go.Scatter(
                x=t_axis_l, y=trend_l,
                mode="lines", name="Trend",
                line=dict(color="#f59e0b", dash="dash", width=2),
            ))
            # Anomaly markers
            anom_x_l = [t_axis_l[i] for i in range(len(ts_local)) if anom_l[i]]
            anom_y_l = [ts_local[i] for i in range(len(ts_local)) if anom_l[i]]
            if anom_x_l:
                fig_local.add_trace(go.Scatter(
                    x=anom_x_l, y=anom_y_l,
                    mode="markers", name="Anomaly",
                    marker=dict(color="#ef4444", size=9,
                                symbol="circle-open", line=dict(width=2)),
                ))
            # Mark current time step
            cur_val = ts_local[st.session_state.map_frame]
            fig_local.add_trace(go.Scatter(
                x=[t_axis_l[st.session_state.map_frame]],
                y=[cur_val],
                mode="markers", name="Current frame",
                marker=dict(color="#10b981", size=12, symbol="diamond"),
            ))
            fig_local.add_hline(
                y=float(np.nanmean(ts_local)),
                line_dash="dot", line_color="#64748b",
                annotation_text="mean",
                annotation_font_color="#64748b",
            )
            fig_local.update_layout(
                **plotly_dark_layout(
                    f"Local Climate Trend — "
                    f"({actual_lat:.2f}°, {actual_lon:.2f}°)", 320
                ),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")),
            )
            st.plotly_chart(fig_local, width='stretch')

            # ── 30-step forecast ──────────────────────────────────────
            with st.expander("🔮 Local Forecast (+30 steps)", expanded=False):
                n_fc = 30
                fut_x = np.arange(len(ts_local), len(ts_local) + n_fc)
                fut_y = slope_l * fut_x + intercept_l
                res_std = np.nanstd(ts_local - trend_l)

                fig_fc = go.Figure()
                fig_fc.add_trace(go.Scatter(
                    x=np.arange(len(ts_local)), y=ts_local,
                    mode="lines", name="Historical",
                    line=dict(color="#06b6d4", width=1.5),
                ))
                fig_fc.add_trace(go.Scatter(
                    x=fut_x, y=fut_y, mode="lines", name="Forecast",
                    line=dict(color="#10b981", dash="dash", width=2.5),
                ))
                fig_fc.add_trace(go.Scatter(
                    x=list(fut_x) + list(reversed(fut_x.tolist())),
                    y=list(fut_y + 1.96*res_std) + list(reversed((fut_y - 1.96*res_std).tolist())),
                    fill="toself", fillcolor="rgba(16,185,129,0.1)",
                    line=dict(color="rgba(0,0,0,0)"), name="95% CI",
                ))
                fig_fc.update_layout(
                    **plotly_dark_layout("Local Forecast", 280),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")),
                )
                st.plotly_chart(fig_fc, width='stretch')
                proj = slope_l * (len(ts_local) + n_fc) + intercept_l
                st.markdown(
                    f"<div class='insight-box'>🔮 Projected value in {n_fc} steps: "
                    f"<b>{proj:.4f} {units_l}</b></div>",
                    unsafe_allow_html=True,
                )

            if st.button("✖ Clear selection", key="clear_click"):
                del st.session_state["clicked_lat"]
                del st.session_state["clicked_lon"]
                st.rerun()

        elif has_time:
            st.markdown(
                "<div class='insight-box' style='text-align:center; color:#64748b;'>"
                "👆 Click any point on the map to run a local climate analysis</div>",
                unsafe_allow_html=True,
            )

        # ════════════════════════════════════════
        #  ⏳ PLAY ANIMATION LOOP
        # ════════════════════════════════════════
        if st.session_state.map_playing and has_time:
            import time as _time
            current = int(st.session_state.map_frame)
            next_frame = current + 1
            if next_frame >= t_len_map:
                # Reached the last frame — stop and stay on last frame
                st.session_state.map_playing = False
                st.session_state.map_frame = t_len_map - 1
                st.rerun()
            else:
                st.session_state.map_frame = next_frame
                _time.sleep(frame_delay)
                st.rerun()



# ══════════════════════════════════════════════
#  TAB 2 — TEMPORAL ANALYSIS
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown("#### 📈 Temporal Analysis & Trend Detection")

    if time_dim is None or time_dim not in da_raw.dims:
        st.info("No time dimension found in this variable. Showing spatial mean only.")
        flat = da_raw.values.flatten()
        fig = go.Figure(go.Bar(x=np.arange(len(flat[:200])), y=flat[:200], marker_color="#3b82f6"))
        fig.update_layout(**plotly_dark_layout("Variable values (first 200 points)", 350))
        st.plotly_chart(fig, width='stretch')
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            agg_method = st.selectbox("Spatial aggregation", ["Global Mean","Global Max","Global Min","Global Std"], key="agg")
        with col_b:
            rolling_win = st.slider("Rolling average window", 1, 24, 1, key="roll")

        # Compute time series
        spatial_dims = [d for d in da_raw.dims if d != time_dim]
        if agg_method == "Global Mean":
            ts = da_raw.mean(dim=spatial_dims).values
        elif agg_method == "Global Max":
            ts = da_raw.max(dim=spatial_dims).values
        elif agg_method == "Global Min":
            ts = da_raw.min(dim=spatial_dims).values
        else:
            ts = da_raw.std(dim=spatial_dims).values

        t_vals = ds[time_dim].values
        try:
            t_labels = pd.to_datetime(t_vals)
        except Exception:
            t_labels = np.arange(len(ts))

        ts_series = pd.Series(ts)
        ts_rolling = ts_series.rolling(rolling_win, center=True).mean()

        # Trend
        slope, intercept = trend_analysis(ts)
        trend_line = slope * np.arange(len(ts)) + intercept

        # Anomalies
        anomalies = anomaly_detection(ts, anomaly_thresh)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t_labels, y=ts,
            mode="lines", name=agg_method,
            line=dict(color="#3b82f6", width=1.5),
            opacity=0.6,
        ))
        if rolling_win > 1:
            fig.add_trace(go.Scatter(
                x=t_labels, y=ts_rolling,
                mode="lines", name=f"Rolling avg ({rolling_win})",
                line=dict(color="#06b6d4", width=2.5),
            ))
        fig.add_trace(go.Scatter(
            x=t_labels, y=trend_line,
            mode="lines", name="Trend",
            line=dict(color="#f59e0b", width=1.5, dash="dash"),
        ))
        # Anomaly markers
        anom_x = [t_labels[i] for i in range(len(ts)) if anomalies[i]]
        anom_y = [ts[i] for i in range(len(ts)) if anomalies[i]]
        if anom_x:
            fig.add_trace(go.Scatter(
                x=anom_x, y=anom_y,
                mode="markers", name="Anomalies",
                marker=dict(color="#ef4444", size=8, symbol="circle-open", line=dict(width=2)),
            ))
        fig.update_layout(
            **plotly_dark_layout(f"{sel_var} — Time Series ({agg_method})", 420),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")),
        )
        st.plotly_chart(fig, width='stretch')

        # Insight cards
        direction = "📈 increasing" if slope > 0 else "📉 decreasing"
        rate_per_step = abs(slope)
        total_change = slope * len(ts)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Trend direction", "↑" if slope>0 else "↓", f"{slope:+.4f}/step")
        with c2:
            st.metric("Total change", f"{total_change:+.3f}")
        with c3:
            st.metric("Anomalies detected", int(anomalies.sum()))
        with c4:
            st.metric("% time anomalous", f"{100*anomalies.mean():.1f}%")

        # Seasonal decomp (if enough steps)
        if len(ts) >= 24:
            st.markdown("##### Seasonal Breakdown")
            if hasattr(t_labels, 'month'):
                months = t_labels.month
                monthly_mean = [np.nanmean(ts[months==m]) for m in range(1,13)]
                month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                fig_seas = go.Figure(go.Bar(
                    x=month_names, y=monthly_mean,
                    marker_color=px.colors.sequential.Blues[3:],
                ))
                fig_seas.update_layout(**plotly_dark_layout("Monthly Mean", 280))
                st.plotly_chart(fig_seas, width='stretch')


# ══════════════════════════════════════════════
#  TAB 3 — ML INSIGHTS  (Event Detector + Insight Layer + Model Comparison)
# ══════════════════════════════════════════════
with tabs[2]:
    st.markdown("#### 🤖 ML Intelligence — Event Detector · Insight Layer · Model Comparison")

    if not (time_dim and time_dim in da_raw.dims):
        st.info("ML features require a time dimension.")
    else:
        spatial_dims_ml = [d for d in da_raw.dims if d != time_dim]
        ts_ml = da_raw.mean(dim=spatial_dims_ml).values.astype(float)
        n_ml  = len(ts_ml)
        t_vals_ml = ds[time_dim].values
        try:
            t_axis_ml = pd.to_datetime(t_vals_ml)
            t_strs    = [str(pd.Timestamp(t).date()) for t in t_vals_ml]
        except Exception:
            t_axis_ml = np.arange(n_ml)
            t_strs    = [str(i) for i in range(n_ml)]

        mean_ml = np.nanmean(ts_ml)
        std_ml  = np.nanstd(ts_ml)
        z_ml    = (ts_ml - mean_ml) / (std_ml + 1e-9)
        slope_ml, intercept_ml = trend_analysis(ts_ml)
        trend_ml = slope_ml * np.arange(n_ml) + intercept_ml
        units_ml = da_raw.attrs.get("units", "")
        long_ml  = da_raw.attrs.get("long_name", sel_var)

        ml_tabs = st.tabs([
            "ðŸš¨ Event Detector",
            "ðŸ’¡ Insight Layer",
            "ðŸ“Š Model Comparison",
        ])

        # ══════════════════════════
        #  SUB-TAB A: EVENT DETECTOR
        # ══════════════════════════
        with ml_tabs[0]:
            st.markdown("##### 🚨 Climate Event Detector")
            st.markdown(
                "<div class='card card-accent' style='font-size:.88rem;'>"
                "Automatically identifies and catalogues significant climate events: "
                "extreme anomalies, rapid shifts, prolonged cold/warm spells, and record-breaking values."
                "</div>", unsafe_allow_html=True
            )

            det_col1, det_col2 = st.columns(2)
            with det_col1:
                evt_thresh = st.slider("Anomaly threshold (σ)", 1.0, 4.0,
                                       float(anomaly_thresh), 0.1, key="evt_thresh")
            with det_col2:
                spell_len = st.slider("Min spell length (steps)", 2, 10, 3, key="spell_len")

            # ── Detect events ──────────────────────────────────────────
            events = []

            # 1. Extreme point anomalies
            for i in range(n_ml):
                z = float(z_ml[i])
                if abs(z) > evt_thresh:
                    kind = "🔴 Extreme High" if z > 0 else "🔵 Extreme Low"
                    events.append({
                        "Step": i, "Date": t_strs[i],
                        "Type": kind,
                        "Value": f"{ts_ml[i]:.4f} {units_ml}",
                        "Z-score": f"{z:+.2f}σ",
                        "Severity": "Critical" if abs(z) > evt_thresh*1.5 else "Significant",
                    })

            # 2. Prolonged warm spells
            in_spell = False
            spell_start = 0
            for i in range(n_ml):
                if z_ml[i] > evt_thresh * 0.6:
                    if not in_spell:
                        in_spell = True
                        spell_start = i
                else:
                    if in_spell and (i - spell_start) >= spell_len:
                        events.append({
                            "Step": spell_start,
                            "Date": f"{t_strs[spell_start]} → {t_strs[i-1]}",
                            "Type": "🟠 Warm Spell",
                            "Value": f"Duration: {i-spell_start} steps",
                            "Z-score": f"{np.mean(z_ml[spell_start:i]):+.2f}σ avg",
                            "Severity": "Prolonged" if (i-spell_start)>spell_len*2 else "Notable",
                        })
                    in_spell = False

            # 3. Rapid shifts (large step-to-step change)
            diffs = np.diff(ts_ml)
            diff_thresh = np.nanstd(diffs) * 2.0
            for i in range(len(diffs)):
                if abs(diffs[i]) > diff_thresh:
                    direction = "📈 Rapid Rise" if diffs[i] > 0 else "📉 Rapid Drop"
                    events.append({
                        "Step": i+1, "Date": t_strs[i+1],
                        "Type": direction,
                        "Value": f"Δ {diffs[i]:+.4f} {units_ml}",
                        "Z-score": f"{z_ml[i+1]:+.2f}σ",
                        "Severity": "Sharp",
                    })

            # 4. All-time records
            running_max = np.maximum.accumulate(ts_ml)
            running_min = np.minimum.accumulate(ts_ml)
            for i in range(1, n_ml):
                if ts_ml[i] > running_max[i-1]:
                    events.append({
                        "Step": i, "Date": t_strs[i],
                        "Type": "🏆 Record High",
                        "Value": f"{ts_ml[i]:.4f} {units_ml}",
                        "Z-score": f"{z_ml[i]:+.2f}σ",
                        "Severity": "Record",
                    })
                elif ts_ml[i] < running_min[i-1]:
                    events.append({
                        "Step": i, "Date": t_strs[i],
                        "Type": "❄️ Record Low",
                        "Value": f"{ts_ml[i]:.4f} {units_ml}",
                        "Z-score": f"{z_ml[i]:+.2f}σ",
                        "Severity": "Record",
                    })

            # Sort by step
            events.sort(key=lambda x: x["Step"])

            # ── Summary metrics ────────────────────────────────────────
            type_counts = {}
            for e in events:
                t = e["Type"]
                type_counts[t] = type_counts.get(t, 0) + 1

            ev_c1, ev_c2, ev_c3, ev_c4 = st.columns(4)
            ev_c1.metric("Total events",    len(events))
            ev_c2.metric("Extreme anomalies",
                         sum(1 for e in events if "Extreme" in e["Type"]))
            ev_c3.metric("Record breaks",
                         sum(1 for e in events if "Record" in e["Type"]))
            ev_c4.metric("Rapid shifts",
                         sum(1 for e in events if "Rapid" in e["Type"]))

            # ── Timeline chart with event markers ─────────────────────
            fig_ev = go.Figure()
            fig_ev.add_trace(go.Scatter(
                x=t_axis_ml, y=ts_ml,
                mode="lines", name=long_ml,
                line=dict(color="#3b82f6", width=1.5), opacity=0.7,
            ))
            fig_ev.add_trace(go.Scatter(
                x=t_axis_ml, y=trend_ml,
                mode="lines", name="Trend",
                line=dict(color="#f59e0b", dash="dash", width=1.5),
            ))

            # Colour-coded event markers
            ev_color_map = {
                "🔴 Extreme High": "#ef4444",
                "🔵 Extreme Low":  "#3b82f6",
                "🟠 Warm Spell":   "#f97316",
                "📈 Rapid Rise":   "#10b981",
                "📉 Rapid Drop":   "#a78bfa",
                "🏆 Record High":  "#fbbf24",
                "❄️ Record Low":   "#67e8f9",
            }
            for ev_type, ev_color in ev_color_map.items():
                ev_pts = [e for e in events if e["Type"] == ev_type]
                if ev_pts:
                    ev_x = [t_axis_ml[e["Step"]] for e in ev_pts
                            if e["Step"] < n_ml]
                    ev_y = [ts_ml[e["Step"]] for e in ev_pts
                            if e["Step"] < n_ml]
                    fig_ev.add_trace(go.Scatter(
                        x=ev_x, y=ev_y,
                        mode="markers",
                        name=ev_type,
                        marker=dict(color=ev_color, size=9,
                                    symbol="circle", line=dict(width=1.5,
                                    color="white")),
                        hovertemplate=f"{ev_type}<br>%{{x}}<br>%{{y:.3f}}<extra></extra>",
                    ))

            fig_ev.update_layout(
                **plotly_dark_layout(f"Climate Event Timeline — {long_ml}", 420),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"),
                            orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_ev, width='stretch')

            # ── Event catalogue table ──────────────────────────────────
            if events:
                st.markdown("##### 📋 Event Catalogue")
                df_ev = pd.DataFrame(events)[["Date","Type","Value","Z-score","Severity"]]
                st.dataframe(df_ev, width='stretch', hide_index=True)
            else:
                st.success("✅ No significant climate events detected at this threshold.")

        # ══════════════════════════
        #  SUB-TAB B: INSIGHT LAYER
        # ══════════════════════════
        with ml_tabs[1]:
            st.markdown("##### 💡 Climate Insight Layer")
            st.markdown(
                "<div class='card card-accent' style='font-size:.88rem;'>"
                "Converts raw statistics into plain-English, actionable climate intelligence — "
                "the kind of analysis a climate scientist would write."
                "</div>", unsafe_allow_html=True
            )

            # ── Compute all stats ──────────────────────────────────────
            total_change   = slope_ml * n_ml
            pct_anom       = 100 * (np.abs(z_ml) > anomaly_thresh).mean()
            pct_warm       = 100 * (z_ml > anomaly_thresh).mean()
            pct_cold       = 100 * (z_ml < -anomaly_thresh).mean()
            max_val        = np.nanmax(ts_ml)
            min_val        = np.nanmin(ts_ml)
            max_idx        = int(np.nanargmax(ts_ml))
            min_idx        = int(np.nanargmin(ts_ml))
            recent_n       = min(12, n_ml // 4)
            recent_mean    = np.nanmean(ts_ml[-recent_n:])
            historic_mean  = np.nanmean(ts_ml[:-recent_n]) if n_ml > recent_n else mean_ml
            recent_delta   = recent_mean - historic_mean
            acceleration   = 0.0
            if n_ml > 20:
                half = n_ml // 2
                slope_first, _ = trend_analysis(ts_ml[:half])
                slope_second,_ = trend_analysis(ts_ml[half:])
                acceleration = slope_second - slope_first

            # ── Insight cards ──────────────────────────────────────────
            def ins_card(icon, title, body, card_cls="card-accent"):
                st.markdown(
                    f"<div class='card {card_cls}' style='margin-bottom:.6rem;'>"
                    f"<div style='font-size:.95rem; font-weight:700; margin-bottom:.3rem;'>"
                    f"{icon} {title}</div>"
                    f"<div style='color:#cbd5e1; font-size:.88rem; line-height:1.7;'>{body}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            # 1. Trend insight
            dir_word = "rising" if slope_ml > 0 else "falling"
            sig_word = ("strongly" if abs(total_change)/std_ml > 1.0
                        else "moderately" if abs(total_change)/std_ml > 0.5
                        else "weakly")
            ins_card("📈", "Long-Term Trend",
                f"<b>{long_ml}</b> is <b>{sig_word} {dir_word}</b> over the record. "
                f"The total change is <b>{total_change:+.4f} {units_ml}</b> "
                f"({slope_ml:+.5f} {units_ml}/step), "
                f"equivalent to <b>{abs(total_change/std_ml):.2f}×</b> the natural variability.")

            # 2. Anomaly insight
            severity = ("alarming" if pct_anom > 20 else
                        "elevated" if pct_anom > 10 else "normal")
            ins_card("🚨", "Anomaly Frequency",
                f"<b>{pct_anom:.1f}%</b> of time steps are anomalous "
                f"(>{anomaly_thresh}σ) — this rate is <b>{severity}</b>. "
                f"Warm extremes: <b>{pct_warm:.1f}%</b> · "
                f"Cold extremes: <b>{pct_cold:.1f}%</b>.",
                "card-warn" if pct_anom > 15 else "card-accent")

            # 3. Recent vs historical
            delta_sign = "warmer/higher" if recent_delta > 0 else "cooler/lower"
            ins_card("🕐", "Recent Period",
                f"The most recent <b>{recent_n}</b> steps average "
                f"<b>{recent_mean:.4f}</b> vs historical mean <b>{historic_mean:.4f}</b> — "
                f"<b>{abs(recent_delta):.4f} {units_ml} {delta_sign}</b> than the long-term baseline.",
                "card-warn" if abs(recent_delta) > 0.5*std_ml else "card-accent")

            # 4. Acceleration
            if n_ml > 20:
                acc_word = "accelerating" if acceleration > 0 else "decelerating"
                ins_card("⚡", "Trend Acceleration",
                    f"The rate of change is <b>{acc_word}</b>. "
                    f"First-half slope: <b>{slope_first:+.5f}</b> · "
                    f"Second-half slope: <b>{slope_second:+.5f}</b> · "
                    f"Acceleration: <b>{acceleration:+.5f}</b>/step².")

            # 5. Extremes
            ins_card("🏆", "Record Values",
                f"All-time high: <b>{max_val:.4f} {units_ml}</b> on <b>{t_strs[max_idx]}</b> "
                f"(Z={z_ml[max_idx]:+.2f}σ)<br>"
                f"All-time low:  <b>{min_val:.4f} {units_ml}</b> on <b>{t_strs[min_idx]}</b> "
                f"(Z={z_ml[min_idx]:+.2f}σ)")

            # 6. Variability
            cv = std_ml / abs(mean_ml) * 100 if abs(mean_ml) > 1e-9 else 0
            ins_card("📐", "Variability",
                f"Standard deviation: <b>{std_ml:.4f} {units_ml}</b> "
                f"(coefficient of variation: <b>{cv:.1f}%</b>). "
                f"{'High variability suggests unstable or oscillating climate conditions.' if cv > 20 else 'Moderate variability is consistent with a stable climate regime.'}")

            # ── Downloadable summary ───────────────────────────────────
            summary_txt = f"""PyClima Explorer+ — Climate Insight Report
Variable : {long_ml} ({sel_var})
Dataset  : {ds_name}
Units    : {units_ml}
Period   : {t_strs[0]} → {t_strs[-1]}
Steps    : {n_ml}

TREND
  Direction   : {"Rising" if slope_ml > 0 else "Falling"}
  Slope       : {slope_ml:+.6f} {units_ml}/step
  Total change: {total_change:+.4f} {units_ml}
  Significance: {sig_word}

ANOMALIES (threshold = {anomaly_thresh}σ)
  Anomalous steps : {pct_anom:.1f}%
  Warm extremes   : {pct_warm:.1f}%
  Cold extremes   : {pct_cold:.1f}%

RECENT vs HISTORICAL
  Recent mean ({recent_n} steps): {recent_mean:.4f}
  Historical mean             : {historic_mean:.4f}
  Delta                       : {recent_delta:+.4f} {units_ml}

RECORDS
  All-time high : {max_val:.4f} {units_ml} on {t_strs[max_idx]}
  All-time low  : {min_val:.4f} {units_ml} on {t_strs[min_idx]}

VARIABILITY
  Std dev : {std_ml:.4f} {units_ml}
  CV      : {cv:.1f}%
"""
            st.download_button(
                "⬇ Download Insight Report (.txt)",
                data=summary_txt,
                file_name=f"climate_insight_{sel_var}.txt",
                mime="text/plain",
            )

        # ══════════════════════════════
        #  SUB-TAB C: MODEL COMPARISON
        # ══════════════════════════════
        with ml_tabs[2]:
            st.markdown("##### 📊 ML Model Comparison for Predictions")
            st.markdown(
                "<div class='card card-accent' style='font-size:.88rem;'>"
                "Runs 4 forecasting models side-by-side and ranks them by RMSE on a "
                "held-out test set — so you can see which model fits your climate data best."
                "</div>", unsafe_allow_html=True
            )

            mc_col1, mc_col2 = st.columns(2)
            with mc_col1:
                n_test  = st.slider("Test set size (steps)", 5, min(60, n_ml//3),
                                    min(20, n_ml//5), key="mc_test")
            with mc_col2:
                n_fore  = st.slider("Forecast horizon (steps)", 5, 60, 20, key="mc_fore")

            from sklearn.linear_model      import LinearRegression, Ridge
            from sklearn.preprocessing     import PolynomialFeatures
            from sklearn.pipeline          import Pipeline
            from sklearn.metrics           import mean_squared_error

            # Train / test split
            ts_clean = ts_ml.copy()
            nan_mask = np.isnan(ts_clean)
            ts_clean[nan_mask] = np.interp(
                np.where(nan_mask)[0],
                np.where(~nan_mask)[0],
                ts_clean[~nan_mask]
            )

            n_train  = n_ml - n_test
            X_all    = np.arange(n_ml).reshape(-1, 1)
            X_train  = X_all[:n_train]
            X_test   = X_all[n_train:]
            y_train  = ts_clean[:n_train]
            y_test   = ts_clean[n_train:]
            X_future = np.arange(n_ml, n_ml + n_fore).reshape(-1, 1)

            # ── Define 4 models ──────────────────────────────────────
            models = {
                "Linear Regression": LinearRegression(),
                "Ridge Regression":  Ridge(alpha=1.0),
                "Polynomial (deg 2)": Pipeline([
                    ("poly", PolynomialFeatures(degree=2, include_bias=False)),
                    ("lr",   LinearRegression()),
                ]),
                "Polynomial (deg 3)": Pipeline([
                    ("poly", PolynomialFeatures(degree=3, include_bias=False)),
                    ("lr",   LinearRegression()),
                ]),
            }

            results  = {}
            forecasts = {}
            preds_test = {}

            for name, model in models.items():
                model.fit(X_train, y_train)
                pred_test   = model.predict(X_test)
                pred_future = model.predict(X_future)
                rmse = float(np.sqrt(mean_squared_error(y_test, pred_test)))
                results[name]    = rmse
                forecasts[name]  = pred_future
                preds_test[name] = pred_test

            # ── Rank models ───────────────────────────────────────────
            ranked = sorted(results.items(), key=lambda x: x[1])
            best_model = ranked[0][0]

            # ── Metric cards ──────────────────────────────────────────
            st.markdown("**Model RMSE on held-out test set** (lower = better)")
            mc_cols = st.columns(len(models))
            for col, (name, rmse) in zip(mc_cols, ranked):
                is_best = (name == best_model)
                col.metric(
                    name,
                    f"{rmse:.4f}",
                    "🏆 Best" if is_best else "",
                )

            # ── Comparison chart: all forecasts ───────────────────────
            model_colors = {
                "Linear Regression":  "#3b82f6",
                "Ridge Regression":   "#a78bfa",
                "Polynomial (deg 2)": "#10b981",
                "Polynomial (deg 3)": "#f59e0b",
            }

            fig_mc = go.Figure()

            # Historical
            fig_mc.add_trace(go.Scatter(
                x=list(range(n_ml)), y=ts_clean,
                mode="lines", name="Historical",
                line=dict(color="#e2e8f0", width=1.5), opacity=0.6,
            ))

            # Test region shading
            fig_mc.add_vrect(
                x0=n_train, x1=n_ml,
                fillcolor="rgba(245,158,11,0.07)",
                line_width=0,
                annotation_text="Test set",
                annotation_position="top left",
                annotation_font_color="#f59e0b",
            )

            # Each model's forecast
            fore_x = list(range(n_ml, n_ml + n_fore))
            for name, color in model_colors.items():
                # Test fit line
                fig_mc.add_trace(go.Scatter(
                    x=list(range(n_train, n_ml)),
                    y=preds_test[name].tolist(),
                    mode="lines", name=f"{name} (fit)",
                    line=dict(color=color, width=1, dash="dot"),
                    showlegend=False,
                ))
                # Forecast
                fig_mc.add_trace(go.Scatter(
                    x=fore_x, y=forecasts[name].tolist(),
                    mode="lines",
                    name=f"{name} (RMSE={results[name]:.4f})",
                    line=dict(color=color, width=2.5,
                              dash="solid" if name==best_model else "dash"),
                ))

            fig_mc.update_layout(
                **plotly_dark_layout("Model Comparison — Forecast", 460),
                legend=dict(bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#e2e8f0"),
                            orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_mc, width='stretch')

            # ── Residuals chart for best model ────────────────────────
            st.markdown(f"**Residuals — {best_model}** (test set)")
            best_resid = y_test - preds_test[best_model]
            fig_res = go.Figure()
            fig_res.add_trace(go.Bar(
                x=list(range(n_train, n_ml)),
                y=best_resid.tolist(),
                marker_color=["#ef4444" if r > 0 else "#3b82f6" for r in best_resid],
                name="Residual",
            ))
            fig_res.add_hline(y=0, line_color="#64748b", line_dash="dot")
            fig_res.update_layout(**plotly_dark_layout("", 220), showlegend=False)
            st.plotly_chart(fig_res, width='stretch')

            # ── Winner summary ────────────────────────────────────────
            winner_rmse = results[best_model]
            runner_rmse = ranked[1][1] if len(ranked) > 1 else winner_rmse
            improvement = (runner_rmse - winner_rmse) / runner_rmse * 100
            st.markdown(
                f"<div class='card card-success'>"
                f"🏆 <b>{best_model}</b> wins with RMSE = <b>{winner_rmse:.5f}</b> "
                f"— <b>{improvement:.1f}%</b> better than the next-best model.<br>"
                f"Best forecast in {n_fore} steps: "
                f"<b>{forecasts[best_model][-1]:.4f} {units_ml}</b>"
                f"</div>",
                unsafe_allow_html=True,
            )



# ══════════════════════════════════════════════
#  TAB 4 — COMPARISON MODE
# ══════════════════════════════════════════════
with tabs[3]:
    st.markdown("#### ⚖️ Comparison Mode — Side-by-Side Dataset Explorer")

    # ── Mode selector: two files OR two time steps from one file ──────────
    cmp_source = st.radio(
        "Compare",
        ["Two uploaded datasets", "Two time steps from one dataset"],
        horizontal=True, key="cmp_source"
    )

    if cmp_source == "Two uploaded datasets":
        if len(datasets) < 2:
            st.info("📂 Upload **two or more NetCDF files** via the sidebar to use this mode.")
        else:
            col_l, col_r = st.columns(2)
            with col_l:
                ds_a_name = st.selectbox("Dataset A (e.g. 1990)", list(datasets.keys()), key="cmp_a")
            with col_r:
                ds_b_name = st.selectbox("Dataset B (e.g. 2020)", list(datasets.keys()),
                                         index=min(1, len(datasets)-1), key="cmp_b")
            ds_a, ds_b = datasets[ds_a_name], datasets[ds_b_name]
            if time_filter_enabled:
                ds_a = slice_dataset_time(ds_a, time_filter_start_idx, time_filter_end_idx)
                ds_b = slice_dataset_time(ds_b, time_filter_start_idx, time_filter_end_idx)
            vars_common = list(set(list_climate_vars(ds_a)) & set(list_climate_vars(ds_b)))
            if not vars_common:
                st.warning("No common variables found between the two datasets.")
                st.stop()
            cmp_var = st.selectbox("Variable", sorted(vars_common), key="cmp_var_files")
            lat_a, lon_a = detect_lat_lon(ds_a)
            lat_b, lon_b = detect_lat_lon(ds_b)
            if not (lat_a and lon_a and lat_b and lon_b):
                st.warning("Could not detect lat/lon in one of the datasets.")
            else:
                da_a = get_2d_slice(ds_a[cmp_var], lat_a, lon_a)
                da_b = get_2d_slice(ds_b[cmp_var], lat_b, lon_b)
                z_a, z_b = da_a.values.astype(float), da_b.values.astype(float)
                label_a, label_b = ds_a_name[:25], ds_b_name[:25]
                lats_a, lons_a = ds_a[lat_a].values, ds_a[lon_a].values
                lats_b, lons_b = ds_b[lat_b].values, ds_b[lon_b].values

                # shared color range
                vmin = min(np.nanmin(z_a), np.nanmin(z_b))
                vmax = max(np.nanmax(z_a), np.nanmax(z_b))

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"<div class='card card-accent' style='padding:.6rem 1rem; font-weight:700;'>📁 {label_a}</div>", unsafe_allow_html=True)
                    fig_a = go.Figure(go.Heatmap(
                        z=z_a, x=lons_a, y=lats_a,
                        colorscale=colorscale, zmin=vmin, zmax=vmax, showscale=False,
                        hovertemplate="Lat:%{y:.1f}° Lon:%{x:.1f}°<br>Val:%{z:.3f}<extra></extra>",
                    ))
                    fig_a.update_layout(**plotly_dark_layout("", 360), xaxis_title="Longitude", yaxis_title="Latitude")
                    st.plotly_chart(fig_a, width='stretch')
                    st.metric("Mean", f"{np.nanmean(z_a):.4f}")
                    st.metric("Std",  f"{np.nanstd(z_a):.4f}")

                with col2:
                    st.markdown(f"<div class='card card-accent' style='padding:.6rem 1rem; font-weight:700;'>📁 {label_b}</div>", unsafe_allow_html=True)
                    fig_b = go.Figure(go.Heatmap(
                        z=z_b, x=lons_b, y=lats_b,
                        colorscale=colorscale, zmin=vmin, zmax=vmax,
                        colorbar=dict(title=dict(text=cmp_var), tickfont=dict(color="#e2e8f0")),
                        hovertemplate="Lat:%{y:.1f}° Lon:%{x:.1f}°<br>Val:%{z:.3f}<extra></extra>",
                    ))
                    fig_b.update_layout(**plotly_dark_layout("", 360), xaxis_title="Longitude", yaxis_title="Latitude")
                    st.plotly_chart(fig_b, width='stretch')
                    st.metric("Mean", f"{np.nanmean(z_b):.4f}")
                    st.metric("Std",  f"{np.nanstd(z_b):.4f}")

                # Difference map
                st.markdown("##### 🔀 Difference Map  (B − A)")
                try:
                    if z_a.shape == z_b.shape:
                        diff = z_b - z_a
                        abs_max = max(abs(np.nanmin(diff)), abs(np.nanmax(diff))) or 1
                        fig_diff = go.Figure(go.Heatmap(
                            z=diff,
                            x=lons_a, y=lats_a,
                            colorscale="RdBu_r",
                            zmid=0, zmin=-abs_max, zmax=abs_max,
                            colorbar=dict(title=dict(text="Δ " + cmp_var), tickfont=dict(color="#e2e8f0")),
                            hovertemplate="Lat:%{y:.1f}° Lon:%{x:.1f}°<br>Δ:%{z:+.3f}<extra></extra>",
                        ))
                        fig_diff.update_layout(**plotly_dark_layout("", 380),
                                               xaxis_title="Longitude", yaxis_title="Latitude")
                        st.plotly_chart(fig_diff, width='stretch')

                        pos = diff[diff > 0]
                        neg = diff[diff < 0]
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Net change",     f"{np.nansum(diff):+.2f}")
                        c2.metric("Warming cells",  f"{(diff > 0).sum():,}",  f"{100*(diff>0).mean():.1f}%")
                        c3.metric("Cooling cells",  f"{(diff < 0).sum():,}",  f"{100*(diff<0).mean():.1f}%")
                        c4.metric("Max anomaly",    f"{np.nanmax(np.abs(diff)):.3f}")

                        # Distribution comparison
                        fig_hist = go.Figure()
                        fig_hist.add_trace(go.Histogram(x=z_a.flatten(), name=label_a,
                                                        opacity=0.7, marker_color="#3b82f6", nbinsx=50))
                        fig_hist.add_trace(go.Histogram(x=z_b.flatten(), name=label_b,
                                                        opacity=0.7, marker_color="#06b6d4", nbinsx=50))
                        fig_hist.update_layout(**plotly_dark_layout("Distribution Comparison", 280),
                                               barmode="overlay",
                                               legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")))
                        st.plotly_chart(fig_hist, width='stretch')
                    else:
                        st.warning(f"Grids differ in shape ({z_a.shape} vs {z_b.shape}). Cannot compute difference map directly.")
                except Exception as ex:
                    st.warning(f"Difference map error: {ex}")

    else:  # Two time steps from one dataset
        if not (time_dim and time_dim in da_raw.dims):
            st.info("No time dimension found in the selected variable.")
        else:
            t_len = len(ds[time_dim])
            t_vals = ds[time_dim].values
            try:
                t_labels_cmp = [str(pd.Timestamp(t).date()) for t in t_vals]
            except Exception:
                t_labels_cmp = [str(i) for i in range(t_len)]

            col_l, col_r = st.columns(2)
            with col_l:
                t_idx_a = st.slider("Time step A", 0, t_len-1, 0, key="cmp_ta")
            with col_r:
                t_idx_b = st.slider("Time step B", 0, t_len-1, min(t_len-1, t_len//2), key="cmp_tb")

            if lat_dim and lon_dim:
                da_ta = da_raw.isel({time_dim: t_idx_a})
                da_tb = da_raw.isel({time_dim: t_idx_b})
                z_a = get_2d_slice(da_ta, lat_dim, lon_dim).values.astype(float)
                z_b = get_2d_slice(da_tb, lat_dim, lon_dim).values.astype(float)
                lats_c = ds[lat_dim].values
                lons_c = ds[lon_dim].values
                label_a = f"Step {t_idx_a}: {t_labels_cmp[t_idx_a]}"
                label_b = f"Step {t_idx_b}: {t_labels_cmp[t_idx_b]}"
                vmin = min(np.nanmin(z_a), np.nanmin(z_b))
                vmax = max(np.nanmax(z_a), np.nanmax(z_b))

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"<div class='card card-accent' style='padding:.6rem 1rem; font-weight:700;'>⏱ {label_a}</div>", unsafe_allow_html=True)
                    fig_a = go.Figure(go.Heatmap(
                        z=z_a, x=lons_c, y=lats_c,
                        colorscale=colorscale, zmin=vmin, zmax=vmax, showscale=False))
                    fig_a.update_layout(**plotly_dark_layout("", 340))
                    st.plotly_chart(fig_a, width='stretch')
                    st.metric("Mean", f"{np.nanmean(z_a):.4f}")

                with col2:
                    st.markdown(f"<div class='card card-accent' style='padding:.6rem 1rem; font-weight:700;'>⏱ {label_b}</div>", unsafe_allow_html=True)
                    fig_b = go.Figure(go.Heatmap(
                        z=z_b, x=lons_c, y=lats_c,
                        colorscale=colorscale, zmin=vmin, zmax=vmax,
                        colorbar=dict(title=dict(text=sel_var), tickfont=dict(color="#e2e8f0"))))
                    fig_b.update_layout(**plotly_dark_layout("", 340))
                    st.plotly_chart(fig_b, width='stretch')
                    st.metric("Mean", f"{np.nanmean(z_b):.4f}")

                # Diff
                diff = z_b - z_a
                abs_max = max(abs(np.nanmin(diff)), abs(np.nanmax(diff))) or 1
                fig_diff = go.Figure(go.Heatmap(
                    z=diff, x=lons_c, y=lats_c,
                    colorscale="RdBu_r", zmid=0, zmin=-abs_max, zmax=abs_max,
                    colorbar=dict(title=dict(text="Δ"), tickfont=dict(color="#e2e8f0")),
                    hovertemplate="Δ:%{z:+.3f}<extra></extra>",
                ))
                fig_diff.update_layout(**plotly_dark_layout(f"Δ {label_b} − {label_a}", 360))
                st.plotly_chart(fig_diff, width='stretch')


# ══════════════════════════════════════════════
#  TAB 5 — STORY MODE
# ══════════════════════════════════════════════
with tabs[4]:
    st.markdown("#### 🕹️ Story Mode — Guided Climate Anomaly Tour")

    if not (time_dim and time_dim in da_raw.dims):
        st.info("Story Mode requires a variable with a time dimension.")
    elif not (lat_dim and lon_dim):
        st.info("Story Mode requires lat/lon coordinates.")
    else:
        # ── Pre-compute everything once ─────────────────────────────────────
        spatial_dims = [d for d in da_raw.dims if d != time_dim]
        ts = da_raw.mean(dim=spatial_dims).values.astype(float)
        t_len_s = len(ts)
        slope, intercept = trend_analysis(ts)
        mean_v, std_v = np.nanmean(ts), np.nanstd(ts)
        z_scores = (ts - mean_v) / (std_v + 1e-9)
        anomalies = np.abs(z_scores) > anomaly_thresh
        anom_indices = np.where(anomalies)[0]
        trend_line = slope * np.arange(t_len_s) + intercept

        t_vals_s = ds[time_dim].values
        try:
            t_labels_s = [str(pd.Timestamp(t).date()) for t in t_vals_s]
        except Exception:
            t_labels_s = [str(i) for i in range(t_len_s)]

        # Find top-3 hottest, top-3 coldest anomaly time steps
        sorted_anom = sorted(anom_indices, key=lambda i: z_scores[i], reverse=True)
        top_hot  = sorted_anom[:3]
        top_cold = sorted_anom[-3:][::-1] if len(sorted_anom) >= 3 else sorted_anom[:3]

        units = da_raw.attrs.get("units", "")
        long_name = da_raw.attrs.get("long_name", sel_var)

        # ── Build chapters ────────────────────────────────────────────────
        chapters = []

        # Ch 1: Dataset intro
        chapters.append({
            "title": "📖 Chapter 1: Meet the Dataset",
            "badge": "badge-blue",
            "text": f"""
                You have loaded <b>{ds_name}</b>.<br>
                Variable: <b>{long_name}</b> ({sel_var}) in <b>{units}</b><br>
                Record: <b>{t_labels_s[0]}</b> → <b>{t_labels_s[-1]}</b>
                &nbsp;|&nbsp; <b>{t_len_s}</b> time steps<br>
                Range: <b>{np.nanmin(ts):.3f}</b> → <b>{np.nanmax(ts):.3f}</b> {units}
            """,
            "chart": "overview",
            "highlight_idx": None,
        })

        # Ch 2: Long-term trend
        direction = "📈 warming / rising" if slope > 0 else "📉 cooling / falling"
        total_change = slope * t_len_s
        chapters.append({
            "title": "📈 Chapter 2: The Long-Term Trend",
            "badge": "badge-amber",
            "text": f"""
                The data shows a <b>{direction}</b> trend.<br>
                Slope: <b>{slope:+.5f}</b> {units}/step &nbsp;|&nbsp;
                Total change over record: <b>{total_change:+.3f}</b> {units}<br>
                {'⚠️ <b>Significant signal</b> — change exceeds 0.5× the natural variability.' if abs(total_change)/std_v > 0.5 else '✅ Change is within natural variability range.'}
            """,
            "chart": "trend",
            "highlight_idx": None,
        })

        # Ch 3: Anomaly overview
        chapters.append({
            "title": "🚨 Chapter 3: Anomaly Landscape",
            "badge": "badge-red",
            "text": f"""
                Using a Z-score threshold of <b>±{anomaly_thresh}σ</b>, the detector found
                <b>{len(anom_indices)}</b> anomalous time steps
                (<b>{100*len(anom_indices)/t_len_s:.1f}%</b> of the record).<br>
                Extreme highs: <b>{int((z_scores > anomaly_thresh).sum())}</b> &nbsp;|&nbsp;
                Extreme lows: <b>{int((z_scores < -anomaly_thresh).sum())}</b>
            """,
            "chart": "anomalies",
            "highlight_idx": None,
        })

        # Ch 4–6: Top 3 hottest anomaly events with spatial map
        for rank, idx in enumerate(top_hot, 1):
            date_str = t_labels_s[idx]
            val = ts[idx]
            zscore = z_scores[idx]
            # Get spatial map for this time step
            chapters.append({
                "title": f"🔴 Chapter {3+rank}: Hot Event #{rank} — {date_str}",
                "badge": "badge-red",
                "text": f"""
                    On <b>{date_str}</b> (time step {idx}), <b>{long_name}</b> spiked to
                    <b>{val:.4f}</b> {units} — a Z-score of <b>+{zscore:.2f}σ</b> above the mean.<br>
                    This ranks as the <b>#{rank} most extreme positive anomaly</b> in the record.
                    The spatial map below shows where the anomaly was concentrated.
                """,
                "chart": "spatial",
                "highlight_idx": idx,
            })

        # Ch 7: Coldest event
        if top_cold:
            idx = top_cold[0]
            date_str = t_labels_s[idx]
            val = ts[idx]
            zscore = z_scores[idx]
            chapters.append({
                "title": f"🔵 Chapter {3+len(top_hot)+1}: Coldest Event — {date_str}",
                "badge": "badge-cyan",
                "text": f"""
                    On <b>{date_str}</b> (time step {idx}), <b>{long_name}</b> dropped to
                    <b>{val:.4f}</b> {units} — a Z-score of <b>{zscore:.2f}σ</b>.<br>
                    This is the <b>most extreme negative anomaly</b> in the record.
                    Possible causes: La Niña, volcanic aerosols, or extreme cold outbreak.
                """,
                "chart": "spatial",
                "highlight_idx": idx,
            })

        # Final chapter: Outlook
        future_val = slope * (t_len_s + 20) + intercept
        chapters.append({
            "title": "🔮 Final Chapter: The Outlook",
            "badge": "badge-green",
            "text": f"""
                Based on the observed linear trend of <b>{slope:+.5f}</b>/step,
                <b>{long_name}</b> is projected to reach <b>{future_val:.3f}</b> {units}
                in 20 more time steps.<br>
                Anomaly rate: <b>{100*len(anom_indices)/t_len_s:.1f}%</b> of the historical
                record — continued monitoring is recommended.
            """,
            "chart": "forecast",
            "highlight_idx": None,
        })

        n_chapters = len(chapters)

        # ── Session state for chapter navigation ──────────────────────────
        if "story_chapter" not in st.session_state:
            st.session_state.story_chapter = 0
        ch_idx = st.session_state.story_chapter

        # ── Chapter card ──────────────────────────────────────────────────
        ch = chapters[ch_idx]
        st.markdown(f"""
        <div class="card" style='min-height:130px; border-left:3px solid #3b82f6;'>
          <div style='display:flex; align-items:center; gap:.75rem; margin-bottom:.6rem;'>
            <span class="badge {ch['badge']}" style='font-size:.7rem;'>
              Chapter {ch_idx+1} of {n_chapters}
            </span>
          </div>
          <div style='color:#3b82f6; font-family:Space Mono,monospace; font-weight:700;
                      font-size:1.05rem; margin-bottom:.6rem;'>{ch['title']}</div>
          <div style='color:#cbd5e1; line-height:1.9; font-size:.92rem;'>{ch['text']}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation ────────────────────────────────────────────────────
        nav_cols = st.columns([1, 1, 4, 1, 1])
        with nav_cols[0]:
            if st.button("⏮ First", disabled=ch_idx==0, key="story_first"):
                st.session_state.story_chapter = 0
                st.rerun()
        with nav_cols[1]:
            if st.button("◀ Prev", disabled=ch_idx==0, key="story_prev"):
                st.session_state.story_chapter -= 1
                st.rerun()
        with nav_cols[2]:
            st.progress((ch_idx+1)/n_chapters,
                        text=f"{'█' * (ch_idx+1)}{'░' * (n_chapters-ch_idx-1)}  {ch_idx+1}/{n_chapters}")
        with nav_cols[3]:
            if st.button("Next ▶", disabled=ch_idx==n_chapters-1, key="story_next"):
                st.session_state.story_chapter += 1
                st.rerun()
        with nav_cols[4]:
            if st.button("Last ⏭", disabled=ch_idx==n_chapters-1, key="story_last"):
                st.session_state.story_chapter = n_chapters - 1
                st.rerun()

        # ── Chapter-specific chart ────────────────────────────────────────
        chart_type = ch["chart"]
        hi = ch["highlight_idx"]
        t_ax = np.arange(t_len_s)

        if chart_type == "overview":
            fig_s = go.Figure()
            fig_s.add_trace(go.Scatter(x=t_ax, y=ts, mode="lines", name=sel_var,
                                       line=dict(color="#3b82f6", width=1.5)))
            fig_s.add_hline(y=mean_v, line_dash="dash", line_color="#64748b",
                            annotation_text="mean", annotation_font_color="#64748b")
            fig_s.update_layout(**plotly_dark_layout(f"{long_name} — Full Record", 300))
            st.plotly_chart(fig_s, width='stretch')

        elif chart_type == "trend":
            fig_s = go.Figure()
            fig_s.add_trace(go.Scatter(x=t_ax, y=ts, mode="lines", name=sel_var,
                                       line=dict(color="#3b82f6", width=1.2), opacity=0.7))
            fig_s.add_trace(go.Scatter(x=t_ax, y=trend_line, mode="lines", name="Trend",
                                       line=dict(color="#f59e0b", width=2.5, dash="dash")))
            fig_s.update_layout(**plotly_dark_layout("Long-Term Trend", 300),
                                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")))
            st.plotly_chart(fig_s, width='stretch')

        elif chart_type == "anomalies":
            colors_bar = ["#ef4444" if z > anomaly_thresh else
                          "#3b82f6" if z < -anomaly_thresh else "#334155"
                          for z in z_scores]
            fig_s = go.Figure(go.Bar(x=t_ax, y=z_scores, marker_color=colors_bar, name="Z-score"))
            fig_s.add_hline(y= anomaly_thresh, line_dash="dash", line_color="#f59e0b")
            fig_s.add_hline(y=-anomaly_thresh, line_dash="dash", line_color="#f59e0b")
            fig_s.update_layout(**plotly_dark_layout("Z-score Timeline — Red = Extreme High, Blue = Extreme Low", 300),
                                showlegend=False)
            st.plotly_chart(fig_s, width='stretch')

        elif chart_type == "spatial" and hi is not None:
            col_ts, col_sp = st.columns([1, 2])
            with col_ts:
                fig_s = go.Figure()
                fig_s.add_trace(go.Scatter(x=t_ax, y=ts, mode="lines", name=sel_var,
                                           line=dict(color="#3b82f6", width=1.2), opacity=0.5))
                # Highlight this event
                fig_s.add_trace(go.Scatter(
                    x=[hi], y=[ts[hi]], mode="markers+text",
                    marker=dict(color="#ef4444" if z_scores[hi]>0 else "#06b6d4",
                                size=14, symbol="star"),
                    text=[f"  {t_labels_s[hi]}"],
                    textfont=dict(color="#e2e8f0", size=10),
                    textposition="middle right",
                    name="This event",
                ))
                fig_s.add_hline(y=mean_v, line_dash="dot", line_color="#64748b")
                fig_s.update_layout(**plotly_dark_layout("Event in Context", 300),
                                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")))
                st.plotly_chart(fig_s, width='stretch')

            with col_sp:
                da_event = da_raw.isel({time_dim: hi})
                da_event_2d = get_2d_slice(da_event, lat_dim, lon_dim)
                z_event = da_event_2d.values.astype(float)
                # Show anomaly from mean
                da_mean_2d = da_raw.mean(dim=time_dim)
                da_mean_2d = get_2d_slice(da_mean_2d, lat_dim, lon_dim)
                z_anom_sp = z_event - da_mean_2d.values.astype(float)
                abs_m = max(abs(np.nanmin(z_anom_sp)), abs(np.nanmax(z_anom_sp))) or 1
                fig_sp = go.Figure(go.Heatmap(
                    z=z_anom_sp,
                    x=ds[lon_dim].values, y=ds[lat_dim].values,
                    colorscale="RdBu_r", zmid=0, zmin=-abs_m, zmax=abs_m,
                    colorbar=dict(title=dict(text=f"Δ{units}"), tickfont=dict(color="#e2e8f0")),
                    hovertemplate="Lat:%{y:.1f}° Lon:%{x:.1f}°<br>Anomaly:%{z:+.3f}<extra></extra>",
                ))
                fig_sp.update_layout(**plotly_dark_layout(f"Spatial Anomaly on {t_labels_s[hi]}", 300),
                                     xaxis_title="Lon", yaxis_title="Lat")
                st.plotly_chart(fig_sp, width='stretch')

        elif chart_type == "forecast":
            n_future_s = 30
            fut_x = np.arange(t_len_s, t_len_s + n_future_s)
            fut_y = slope * fut_x + intercept
            res_std = np.nanstd(ts - trend_line)
            fig_s = go.Figure()
            fig_s.add_trace(go.Scatter(x=t_ax, y=ts, mode="lines", name="Historical",
                                       line=dict(color="#3b82f6", width=1.5)))
            fig_s.add_trace(go.Scatter(x=t_ax, y=trend_line, mode="lines", name="Trend",
                                       line=dict(color="#f59e0b", dash="dash", width=1.5)))
            fig_s.add_trace(go.Scatter(x=fut_x, y=fut_y, mode="lines", name="Forecast",
                                       line=dict(color="#10b981", dash="dash", width=2.5)))
            fig_s.add_trace(go.Scatter(
                x=list(fut_x) + list(reversed(fut_x.tolist())),
                y=list(fut_y + 1.96*res_std) + list(reversed((fut_y - 1.96*res_std).tolist())),
                fill="toself", fillcolor="rgba(16,185,129,0.1)",
                line=dict(color="rgba(0,0,0,0)"), name="95% CI",
            ))
            fig_s.update_layout(**plotly_dark_layout("Trend Forecast (+30 steps)", 320),
                                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")))
            st.plotly_chart(fig_s, width='stretch')


# ══════════════════════════════════════════════
#  TAB 6 — 3D GLOBE VIEW
# ══════════════════════════════════════════════
with tabs[5]:
    st.markdown("#### 🌐 3D Climate Globe")

    if lat_dim is None or lon_dim is None:
        st.warning("Cannot render globe — lat/lon not detected.")
    else:
        has_time_3d = bool(time_dim and time_dim in da_raw.dims)
        t_len_3d    = len(ds[time_dim]) if has_time_3d else 1

        if "globe_frame"   not in st.session_state: st.session_state.globe_frame   = 0
        if "globe_playing" not in st.session_state: st.session_state.globe_playing = False

        # Controls
        c1, c2, c3 = st.columns([1, 1, 4])
        with c1:
            lbl = "⏹ Stop" if st.session_state.globe_playing else "▶ Play"
            if st.button(lbl, key="globe_play_btn", use_container_width=True):
                st.session_state.globe_playing = not st.session_state.globe_playing
                st.rerun()
        with c2:
            g_speed = st.selectbox("Speed", ["Slow","Normal","Fast"],
                                   index=1, key="g_speed",
                                   label_visibility="collapsed")
        with c3:
            if has_time_3d:
                gf = st.slider("🕐 Time", 0, t_len_3d-1,
                               value=int(st.session_state.globe_frame),
                               disabled=st.session_state.globe_playing,
                               key="globe_slider")
                if not st.session_state.globe_playing:
                    st.session_state.globe_frame = int(gf)

        g_delay = {"Slow":0.6,"Normal":0.28,"Fast":0.08}[g_speed]
        cur_3d  = int(st.session_state.globe_frame)

        if has_time_3d:
            try:    globe_date = str(pd.Timestamp(ds[time_dim].values[cur_3d]).date())
            except: globe_date = f"Step {cur_3d}"
        else:
            globe_date = ""

        st.markdown(
            f"<div style='text-align:center;font-family:Space Mono,monospace;"
            f"color:#3b82f6;font-size:1rem;margin:2px 0 8px;'>"
            f"📅 {globe_date} &nbsp;|&nbsp; Frame {cur_3d+1}/{t_len_3d}</div>",
            unsafe_allow_html=True)

        # Get 2D slice
        if has_time_3d:
            da_sl = get_2d_slice(da_raw.isel({time_dim: cur_3d}), lat_dim, lon_dim)
        else:
            da_sl = get_2d_slice(da_raw, lat_dim, lon_dim)

        z_g    = da_sl.values.astype(float)
        lats_g = ds[lat_dim].values
        lons_g = ds[lon_dim].values
        units_g = da_raw.attrs.get("units", "")

        # Global colour range (locked)
        @st.cache_data(show_spinner=False)
        def globe_color_range(ds_key, var_key, t_start_idx, t_end_idx):
            idxs = np.linspace(0, t_len_3d-1, min(t_len_3d, 10), dtype=int)
            samples = []
            for i in idxs:
                sl = get_2d_slice(da_raw.isel({time_dim: i}), lat_dim, lon_dim) \
                     if has_time_3d else get_2d_slice(da_raw, lat_dim, lon_dim)
                flat = sl.values.flatten()
                samples.append(flat[~np.isnan(flat)])
            arr = np.concatenate(samples)
            return float(np.nanpercentile(arr,2)), float(np.nanpercentile(arr,98))

        vmin_g, vmax_g = globe_color_range(
            ds_name,
            sel_var,
            time_filter_start_idx,
            time_filter_end_idx,
        )

        # Flatten grid
        lon_grid, lat_grid = np.meshgrid(lons_g, lats_g)
        lon_f = lon_grid.flatten().astype(float)
        lat_f = lat_grid.flatten().astype(float)
        val_f = z_g.flatten().astype(float)
        valid = ~np.isnan(val_f)
        lon_f, lat_f, val_f = lon_f[valid], lat_f[valid], val_f[valid]

        # Marker size proportional to grid spacing
        dlat = abs(float(lats_g[1]-lats_g[0])) if len(lats_g)>1 else 2.5
        dlon = abs(float(lons_g[1]-lons_g[0])) if len(lons_g)>1 else 2.5
        msize = max(2, int(min(dlat, dlon) * 5.5))
        max_pts_globe = st.slider(
            "Point cap",
            3000, 50000, 16000, 1000,
            key="globe_point_cap",
            help="Caps rendered points for smoother interaction.",
        )
        if len(val_f) > max_pts_globe:
            sample_idx = np.linspace(0, len(val_f) - 1, max_pts_globe, dtype=int)
            lon_r = lon_f[sample_idx]
            lat_r = lat_f[sample_idx]
            val_r = val_f[sample_idx]
        else:
            lon_r, lat_r, val_r = lon_f, lat_f, val_f

        fig_globe = go.Figure()
        fig_globe.add_trace(go.Scattergeo(
            lon=lon_r, lat=lat_r,
            mode="markers",
            marker=dict(
                color=val_r,
                colorscale=colorscale,
                cmin=vmin_g, cmax=vmax_g,
                size=msize,
                symbol="square",
                opacity=1.0,
                line=dict(width=0),
                colorbar=dict(
                    title=dict(text=f"{sel_var} ({units_g})",
                               font=dict(color="#e2e8f0",size=12)),
                    tickfont=dict(color="#e2e8f0"),
                    bgcolor="rgba(17,24,39,0.85)",
                    bordercolor="#1e2d45",
                    thickness=14, len=0.7,
                ),
            ),
            hovertemplate=(
                "<b>%{lat:.1f}degN  %{lon:.1f}degE</b><br>"
                f"{sel_var}: " + "%{marker.color:.3f} " + units_g +
                "<extra></extra>"
            ),
            showlegend=False,
        ))
        fig_globe.update_layout(
            height=600,
            paper_bgcolor="rgba(10,14,26,1)",
            font=dict(color="#e2e8f0"),
            margin=dict(l=0,r=0,t=40,b=0),
            title=dict(
                text=f"{da_raw.attrs.get('long_name',sel_var)}{'  -  '+globe_date if globe_date else ''}",
                font=dict(size=15, color="#e2e8f0", family="Space Mono"),
                x=0.5, xanchor="center",
            ),
            geo=dict(
                projection_type="orthographic",
                showocean=True,   oceancolor="#0d1b2e",
                showland=True,    landcolor="#1c2a1c",
                showlakes=True,   lakecolor="#0d1b2e",
                showrivers=False,
                showcountries=True,
                countrycolor="rgba(160,190,220,0.5)",
                countrywidth=0.6,
                showcoastlines=True,
                coastlinecolor="rgba(160,200,240,0.7)",
                coastlinewidth=0.9,
                showframe=True,
                framecolor="#1e2d45",
                bgcolor="rgba(10,14,26,1)",
            ),
        )
        st.plotly_chart(fig_globe, width='stretch')
        st.caption("Plotly globe active: drag to rotate, scroll to zoom, and double-click to reset.")

        lo, mid, hi = vmin_g, (vmin_g+vmax_g)/2, vmax_g
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;"
            f"font-size:.8rem;color:#94a3b8;margin:4px 0 14px;'>"
            f"<span>Min <b style='color:#60a5fa'>{lo:.2f}</b></span>"
            f"<span>Mid <b style='color:#e2e8f0'>{mid:.2f}</b></span>"
            f"<span>Max <b style='color:#f87171'>{hi:.2f}</b> {units_g}</span>"
            f"</div>", unsafe_allow_html=True)

        # Animation loop
        if st.session_state.globe_playing and has_time_3d:
            import time as _time
            nxt = cur_3d + 1
            if nxt >= t_len_3d:
                st.session_state.globe_playing = False
                st.session_state.globe_frame   = t_len_3d - 1
            else:
                st.session_state.globe_frame = nxt
                _time.sleep(g_delay)
            st.rerun()

        # ── 3D Terrain Surface ─────────────────────────────────────────
        st.markdown("---")
        st.markdown("##### 🏔️ 3D Terrain Surface")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            z_exag = st.slider("Vertical exaggeration", 0.1, 5.0, 1.0, 0.1, key="z_exag")
        with sc2:
            show_contour = st.checkbox("Contour lines", value=True, key="3d_cont")
        with sc3:
            wire = st.checkbox("Wireframe", value=False, key="3d_wire")

        max_pts  = 80
        lat_step = max(1, len(lats_g) // max_pts)
        lon_step = max(1, len(lons_g) // max_pts)
        z_surf   = z_g[::lat_step, ::lon_step]
        lon_sg, lat_sg = np.meshgrid(lons_g[::lon_step], lats_g[::lat_step])
        surf_kw = dict(
            z=z_surf*z_exag, x=lon_sg, y=lat_sg, colorscale=colorscale,
            colorbar=dict(title=dict(text=f"{sel_var} ({units_g})", side="right"),
                          tickfont=dict(color="#e2e8f0")),
            hovertemplate="Lon:%{x:.1f}° Lat:%{y:.1f}°<br>Val:%{z:.3f}<extra></extra>",
        )
        if show_contour:
            surf_kw["contours_z"] = dict(show=True,usecolormap=True,
                                         highlightcolor="#ffffff",project_z=False)
        if wire:
            surf_kw["hidesurface"] = True
            surf_kw["contours_x"]  = dict(show=True,color="#3b82f6",width=1)
            surf_kw["contours_y"]  = dict(show=True,color="#3b82f6",width=1)
        fig_surf = go.Figure(go.Surface(**surf_kw))
        fig_surf.update_layout(
            height=500, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"),
            scene=dict(
                bgcolor="rgba(10,14,26,0.95)",
                xaxis=dict(title="Longitude",gridcolor="#1e2d45",backgroundcolor="rgba(0,0,0,0)"),
                yaxis=dict(title="Latitude", gridcolor="#1e2d45",backgroundcolor="rgba(0,0,0,0)"),
                zaxis=dict(title=f"{sel_var} x{z_exag}",gridcolor="#1e2d45",backgroundcolor="rgba(0,0,0,0)"),
                camera=dict(eye=dict(x=1.5,y=1.5,z=0.9))),
            margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_surf, width='stretch')
        st.caption("💡 Drag to rotate · Scroll to zoom · Double-click to reset")


# ══════════════════════════════════════════════
#  TAB 7 — DATASET INFO
# ══════════════════════════════════════════════
with tabs[6]:
    st.markdown("#### 📄 Dataset Metadata & Structure")

    col_meta, col_vars = st.columns(2)
    with col_meta:
        st.markdown("**Global Attributes**")
        attrs = dict(ds.attrs)
        if attrs:
            df_attrs = pd.DataFrame({"Attribute": list(attrs.keys()),
                                     "Value": [str(v)[:120] for v in attrs.values()]})
            st.dataframe(df_attrs, width='stretch', hide_index=True)
        else:
            st.info("No global attributes found.")

    with col_vars:
        st.markdown("**Variables**")
        var_rows = []
        for v in variables:
            da_v = ds[v]
            var_rows.append({
                "Variable": v,
                "Long name": da_v.attrs.get("long_name", "—"),
                "Units": da_v.attrs.get("units", "—"),
                "Dims": str(da_v.dims),
                "Shape": str(da_v.shape),
                "dtype": str(da_v.dtype),
            })
        st.dataframe(pd.DataFrame(var_rows), width='stretch', hide_index=True)

    st.markdown("**Coordinates**")
    coord_rows = []
    for c in ds.coords:
        coord = ds[c]
        mn = float(coord.values.min()) if coord.values.ndim > 0 else "—"
        mx = float(coord.values.max()) if coord.values.ndim > 0 else "—"
        coord_rows.append({
            "Coordinate": c,
            "Size": len(coord),
            "Min": f"{mn:.4g}" if isinstance(mn, float) else mn,
            "Max": f"{mx:.4g}" if isinstance(mx, float) else mx,
            "dtype": str(coord.dtype),
        })
    st.dataframe(pd.DataFrame(coord_rows), width='stretch', hide_index=True)

    # Raw preview
    with st.expander("🔍 Raw xarray repr"):
        st.code(str(ds), language="text")












