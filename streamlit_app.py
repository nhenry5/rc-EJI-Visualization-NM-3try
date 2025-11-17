# streamlit_app.py
# TEAM 23: Environmental Justice in New Mexico — EJI Visualization (3try)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(
    page_title="TEAM 23: Environmental Justice in New Mexico — 📊 EJI Visualization (3try)",
    page_icon="🌎",
    layout="wide"
)

# ------------------------------
# Hide Streamlit's Auto Navigation and Add Custom Title in Logo Spot
# ------------------------------
st.markdown('<style>div[data-testid="stSidebarNav"] {display: none;}</style>', unsafe_allow_html=True)
st.markdown("""
<style>
div[data-testid="stLogoSpacer"] {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    padding-top: 40px;
}
div[data-testid="stLogoSpacer"]::before {
    content: "TEAM 23:";
    font-size: 30px;
    font-weight: bold;
    white-space: nowrap;
    margin-bottom: 5px;
}
div[data-testid="stLogoSpacer"]::after {
    content: "🌎 Environmental Justice in New Mexico";
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: -40px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Custom Sidebar
# ------------------------------
with st.sidebar:
    st.write("---")
    st.page_link("streamlit_app.py", label="EJI Visualization", icon="📊")
    st.page_link("pages/1_What_Goes_Into_EJI.py", label="What Goes Into the EJI?", icon="🧩")
    st.page_link("pages/2_EJI_Scale_and_Categories.py", label="What Does the EJI Mean?", icon="🌡️")

# ------------------------------
# Load Data Function
# ------------------------------
@st.cache_data
def load_data_for_year(year: str):
    """Load the state and county CSVs for the given year."""
    base = "https://github.com/rileycochrell/rc-EJI-Visualization-NM-3try/raw/refs/heads/main/data"
    state_path = f"{base}/{year}/clean/{year}EJI_StateAverages_RPL.csv"
    county_path = f"{base}/{year}/clean/{year}EJI_NewMexico_CountyMeans.csv"
    state_df = pd.read_csv(state_path)
    county_df = pd.read_csv(county_path)
    return state_df, county_df

# ------------------------------
# Main App Layout
# ------------------------------
st.title("📊 Environmental Justice Index Visualization (New Mexico) — 3try")
st.info("""
**Interpreting the EJI Score:**  
Lower EJI values (closer to 0) indicate *lower cumulative environmental and social burdens*.  
Higher EJI values (closer to 1) indicate *higher cumulative burdens and vulnerabilities*.
""")
st.write("Use the dropdowns below to explore data for **New Mexico** or specific **counties**.")
st.info("🔴 Rows highlighted in red represent areas with **Very High Concern/Burden (EJI ≥ 0.76)**.")

# ------------------------------
# Year Selection
# ------------------------------
years_available = ["2022", "2024"]
selected_year = st.selectbox("Select Year:", years_available)

# Load CSVs for the selected year
try:
    state_df, county_df = load_data_for_year(selected_year)
except Exception as e:
    st.error(f"Error loading data for {selected_year}: {e}")
    st.stop()

# ------------------------------
# Normalize Columns & Metrics
# ------------------------------
rename_map = {
    "Mean_EJI": "RPL_EJI",
    "Mean_EBM": "RPL_EBM",
    "Mean_SVM": "RPL_SVM",
    "Mean_HVM": "RPL_HVM",
    "Mean_CBM": "RPL_CBM",
    "Mean_EJI_CBM": "RPL_EJI_CBM"
}
state_df.rename(columns=rename_map, inplace=True)
county_df.rename(columns=rename_map, inplace=True)

BASE_METRICS = ["RPL_EJI", "RPL_EBM", "RPL_SVM", "RPL_HVM"]
OPTIONAL_METRICS = ["RPL_CBM", "RPL_EJI_CBM"]
metrics = BASE_METRICS.copy()
for m in OPTIONAL_METRICS:
    if m in county_df.columns or m in state_df.columns:
        metrics.append(m)

pretty = {
    "RPL_EJI": "Overall EJI",
    "RPL_EBM": "Environmental Burden",
    "RPL_SVM": "Social Vulnerability",
    "RPL_HVM": "Health Vulnerability",
    "RPL_CBM": "Climate Burden",
    "RPL_EJI_CBM": "EJI + Climate Burden"
}

dataset1_rainbows = {
    "RPL_EJI": "#911eb4",
    "RPL_EBM": "#c55c29",
    "RPL_SVM": "#4363d8",
    "RPL_HVM": "#f032e6",
    "RPL_CBM": "#469990",
    "RPL_EJI_CBM": "#801650"
}
dataset2_rainbows = {
    "RPL_EJI": "#b88be1",
    "RPL_EBM": "#D2B48C",
    "RPL_SVM": "#87a1e5",
    "RPL_HVM": "#f79be9",
    "RPL_CBM": "#94c9c4",
    "RPL_EJI_CBM": "#f17cb0"
}

# Build dropdown lists dynamically
counties = sorted(county_df["County"].dropna().unique())
states = sorted(state_df["State"].dropna().unique())
parameter1 = ["New Mexico", "County"]

# ------------------------------
# Helper Functions
# ------------------------------
def get_contrast_color(hex_color: str):
    try:
        rgb = tuple(int(hex_color.strip("#")[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return "black"
    brightness = (0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2])
    return "black" if brightness > 150 else "white"

def no_data_label_color():
    return "black"

def display_colored_table_html(df, color_map, pretty_map, title=None):
    if isinstance(df, pd.Series):
        df = df.to_frame().T
    df_display = df.rename(columns=pretty_map)
    if title:
        st.markdown(f"### {title}")

    header_html = "<tr>"
    for col in df_display.columns:
        orig_keys = [k for k, v in pretty_map.items() if v == col]
        color = color_map.get(orig_keys[0], "#FFFFFF") if orig_keys else "#FFFFFF"
        text_color = get_contrast_color(color)
        header_html += f'<th style="background-color:{color};color:{text_color};padding:6px;text-align:center;">{col}</th>'
    header_html += "</tr>"

    body_html = ""
    for _, row in df_display.iterrows():
        highlight = any([(isinstance(v, (int, float)) and v >= 0.76) for v in row])
        row_style = "background-color:#ffb3b3;" if highlight else ""
        body_html += f"<tr style='{row_style}'>"
        for val in row:
            cell_text = "No Data" if pd.isna(val) else (f"{val:.3f}" if isinstance(val, float) else val)
            body_html += f"<td style='text-align:center;padding:4px;border:1px solid #ccc'>{cell_text}</td>"
        body_html += "</tr>"

    table_html = f"<table style='border-collapse:collapse;width:100%;border:1px solid black;'>{header_html}{body_html}</table>"
    st.markdown(table_html, unsafe_allow_html=True)

NO_DATA_HEIGHT = 0.5
NO_DATA_PATTERN = dict(shape="/", fgcolor="black", bgcolor="white", size=6)

def build_customdata(area_label, values):
    out = []
    for v in values:
        out.append([area_label, "No Data"] if pd.isna(v) else [area_label, f"{v:.3f}"])
    return out

def build_texts_and_colors(colors_map, area_label, values):
    texts, fonts = [], []
    for metric_key, v in zip(metrics, values):
        c = colors_map.get(metric_key, "#FFFFFF")
        if pd.isna(v):
            texts.append("No Data")
            fonts.append(no_data_label_color())
        else:
            val_str = f"{v:.3f}"
            texts.append(f"{area_label}<br>{val_str}" if area_label else val_str)
            fonts.append(get_contrast_color(c))
    return texts, fonts

# ------------------------------
# Plot Functions
# ------------------------------
def plot_single_chart(title, data_values, area_label=None):
    vals = np.array([np.nan if pd.isna(v) else float(v) for v in data_values.loc[metrics].values])
    color_list = [dataset1_rainbows.get(m, "#888888") for m in metrics]
    has_y = [v if not pd.isna(v) else 0 for v in vals]
    nodata_y = [NO_DATA_HEIGHT if pd.isna(v) else 0 for v in vals]

    texts, fonts = build_texts_and_colors(dataset1_rainbows, area_label, vals)
    customdata = build_customdata(area_label, vals)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[pretty[m] for m in metrics],
        y=has_y,
        marker_color=color_list,
        text=texts,
        texttemplate="%{text}",
        textposition="inside",
        textfont=dict(size=10, color=fonts),
        customdata=customdata,
        hovertemplate="%{x}<br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>",
        showlegend=False
    ))
    fig.add_trace(go.Bar(
        x=[pretty[m] for m in metrics],
        y=nodata_y,
        marker=dict(color="white", pattern=NO_DATA_PATTERN),
        text=[f"{area_label}<br>No Data" if pd.isna(v) else "" for v in vals],
        texttemplate="%{text}",
        textposition="outside",
        textfont=dict(size=10, color=no_data_label_color()),
        customdata=customdata,
        hovertemplate="%{x}<br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>",
        name="No Data"
    ))
    fig.update_layout(
        title=title,
        yaxis=dict(title="Percentile Rank Value", range=[0, 1], dtick=0.25),
        xaxis_title="Environmental Justice Index Metric",
        barmode="overlay",
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# plot_comparison function remains identical to your current version

# ------------------------------
# Parameter Selection
# ------------------------------
selected_parameter = st.selectbox("View EJI data for:", parameter1)

if selected_parameter == "County":
    selected_county = st.selectbox("Select a New Mexico County:", counties)
    subset = county_df[county_df["County"] == selected_county]
    if subset.empty:
        st.warning(f"No data found for {selected_county}.")
    else:
        st.subheader(f"⚖️ EJI Data for {selected_county} — {selected_year}")
        display_colored_table_html(subset, dataset1_rainbows, pretty)
        county_values = subset.iloc[0]
        plot_single_chart(f"EJI Metrics — {selected_county} ({selected_year})", county_values, area_label=selected_county)

else:
    nm_row = state_df[state_df["State"].str.strip().str.lower() == "new mexico"]
    if nm_row.empty:
        st.warning("No New Mexico data found.")
    else:
        st.subheader(f"⚖️ New Mexico Statewide EJI Scores — {selected_year}")
        display_colored_table_html(nm_row, dataset1_rainbows, pretty)
        nm_values = nm_row.iloc[0]
        plot_single_chart(f"EJI Metrics — New Mexico ({selected_year})", nm_values, area_label="New Mexico")

st.divider()
st.caption("Data Source: CDC Environmental Justice Index | Visualization by Riley Cochrell")
