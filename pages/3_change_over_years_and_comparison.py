import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(
    page_title="TEAM 23: Environmental Justice in New Mexico — 📈 Yearly Comparison",
    page_icon="📈",
    layout="wide"
)

# ------------------------------
# Hide Streamlit's Auto Navigation and Add Custom Title
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
    margin-bottom: 5px;
}
div[data-testid="stLogoSpacer"]::after {
    content: "🌎 Environmental Justice in New Mexico";
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
    st.page_link("pages/3_change_over_years_and_comparison.py", label="EJI – Change Over Years", icon="📈")
    st.page_link("pages/1_What_Goes_Into_EJI.py", label="What Goes Into the EJI?", icon="🧩")
    st.page_link("pages/2_EJI_Scale_and_Categories.py", label="What Does the EJI Mean?", icon="🌡️")

# ------------------------------
# Available Years
# ------------------------------
AVAILABLE_YEARS = ["2022", "2024"]

# ------------------------------
# Load Data
# ------------------------------
@st.cache_data
def load_data_for_year(year: str):
    base = "https://github.com/rileycochrell/rc-EJI-Visualization-NM-3try/raw/refs/heads/main/data"
    state_path = f"{base}/{year}/clean/{year}EJI_StateAverages_RPL.csv"
    county_path = f"{base}/{year}/clean/{year}EJI_NewMexico_CountyMeans.csv"
    state_df = pd.read_csv(state_path)
    county_df = pd.read_csv(county_path)
    return state_df, county_df

rename_map = {
    "Mean_EJI": "RPL_EJI",
    "Mean_EBM": "RPL_EBM",
    "Mean_SVM": "RPL_SVM",
    "Mean_HVM": "RPL_HVM",
    "Mean_CBM": "RPL_CBM",
    "Mean_EJI_CBM": "RPL_EJI_CBM"
}

BASE_METRICS = ["RPL_EJI", "RPL_EBM", "RPL_SVM", "RPL_HVM"]
OPTIONAL_METRICS = ["RPL_CBM", "RPL_EJI_CBM"]

pretty = {
    "RPL_EJI": "Overall EJI",
    "RPL_EBM": "Environmental Burden",
    "RPL_SVM": "Social Vulnerability",
    "RPL_HVM": "Health Vulnerability",
    "RPL_CBM": "Climate Burden",
    "RPL_EJI_CBM": "EJI + Climate Burden"
}

dataset_year1_rainbows = {
    "RPL_EJI": "#911eb4",
    "RPL_EBM": "#c55c29",
    "RPL_SVM": "#4363d8",
    "RPL_HVM": "#f032e6",
    "RPL_CBM": "#469990",
    "RPL_EJI_CBM": "#801650"
}

dataset_year2_rainbows = {
    "RPL_EJI": "#b88be1",
    "RPL_EBM": "#D2B48C",
    "RPL_SVM": "#87a1e5",
    "RPL_HVM": "#f79be9",
    "RPL_CBM": "#94c9c4",
    "RPL_EJI_CBM": "#f17cb0"
}

# ------------------------------
# Helper Functions
# ------------------------------
def get_contrast_color(hex_color):
    try:
        rgb = tuple(int(hex_color.strip("#")[i:i+2], 16) for i in (0,2,4))
    except:
        return "black"
    brightness = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
    return "black" if brightness>150 else "white"

def get_theme_color():
    return "black"

def display_colored_table_html(df, color_map, pretty_map, title=None):
    if isinstance(df, pd.Series):
        df = df.to_frame().T
    df_display = df.rename(columns=pretty_map)
    if title:
        st.markdown(f"### {title}")

    header_html = "<tr>"
    for col in df_display.columns:
        orig = [k for k,v in pretty_map.items() if v==col]
        color = color_map.get(orig[0], "#FFFFFF") if orig else "#FFFFFF"
        text_color = get_contrast_color(color)
        header_html += f'<th style="background-color:{color};color:{text_color};padding:6px;text-align:center;">{col}</th>'
    header_html += "</tr>"

    body_html = ""
    for _, row in df_display.iterrows():
        row_style = ""
        body_html += f"<tr style='{row_style}'>"
        for val in row:
            cell_text = "No Data" if pd.isna(val) else (f"{val:.3f}" if isinstance(val,float) else val)
            body_html += f"<td style='text-align:center;padding:4px;border:1px solid #ccc'>{cell_text}</td>"
        body_html += "</tr>"

    table_html = f"<table style='border-collapse:collapse;width:100%;border:1px solid black;'>{header_html}{body_html}</table>"
    st.markdown(table_html, unsafe_allow_html=True)

# ------------------------------
# Plot Function with Discrepancy
# ------------------------------
def plot_year_single(y1_values, y2_values, label1, label2, metrics):
    vals1 = np.array([np.nan if pd.isna(v) else float(v) for v in y1_values])
    vals2 = np.array([np.nan if pd.isna(v) else float(v) for v in y2_values])
    metric_names = [pretty[m] for m in metrics]
    colors1 = [dataset_year1_rainbows[m] for m in metrics]
    colors2 = [dataset_year2_rainbows[m] for m in metrics]

    # Compute discrepancy
    disc1, disc2, disc_colors = [], [], []
    for v1,v2 in zip(vals1, vals2):
        if pd.isna(v1) or pd.isna(v2):
            disc1.append(0); disc2.append(0); disc_colors.append("white")
        elif v1<v2:
            disc1.append(v2-v1); disc2.append(0); disc_colors.append("red")
        elif v2<v1:
            disc1.append(0); disc2.append(v1-v2); disc_colors.append("green")
        else:
            disc1.append(0); disc2.append(0); disc_colors.append("white")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=metric_names, y=vals1, marker_color=colors1, name=label1))
    fig.add_trace(go.Bar(x=metric_names, y=disc1, marker_color=disc_colors, name="Discrepancy (↑)"))
    fig.add_trace(go.Bar(x=metric_names, y=vals2, marker_color=colors2, name=label2))
    fig.add_trace(go.Bar(x=metric_names, y=disc2, marker_color=disc_colors, name="Discrepancy (↓)"))

    fig.update_layout(
        barmode="stack",
        title=f"EJI Metrics Comparison: {label1} vs {label2}",
        yaxis=dict(title="Percentile Rank Value", range=[0,1], dtick=0.25),
        xaxis_title="EJI Metric",
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# Main App
# ------------------------------
st.title("Year-Year Comparison")
st.info("""
Negative change (Δ < 0) indicates improvement (reduced burden).  
Positive change (Δ > 0) indicates worse outcome (increased burden).
""")

# ------------------------------
# Year Selection
# ------------------------------
baseline_year = st.selectbox("Select baseline year:", AVAILABLE_YEARS, index=0)
other_year_options = [y for y in AVAILABLE_YEARS if y != baseline_year]
other_year = st.selectbox("Select comparison year:", other_year_options, index=0)

# ------------------------------
# Load Baseline Year Data
# ------------------------------
try:
    state_df1, county_df1 = load_data_for_year(baseline_year)
except Exception as e:
    st.error(f"Error loading data for {baseline_year}: {e}")
    st.stop()

state_df1.rename(columns=rename_map, inplace=True)
county_df1.rename(columns=rename_map, inplace=True)

metrics = BASE_METRICS.copy()
for m in OPTIONAL_METRICS:
    if m in county_df1.columns:
        metrics.append(m)

counties = sorted(county_df1["County"].dropna().unique())
states = sorted(state_df1["State"].dropna().unique())

selected_parameter = st.selectbox("View EJI data for:", ["New Mexico", "County"])

# ------------------------------
# Handle County or State
# ------------------------------
if selected_parameter=="County":
    selected_county = st.selectbox("Select a New Mexico County:", counties)
    subset1 = county_df1[county_df1["County"]==selected_county]

    county_df2 = load_data_for_year(other_year)[1]
    county_df2.rename(columns=rename_map, inplace=True)
    subset2 = county_df2[county_df2["County"]==selected_county]

    # Only keep metrics present in both datasets
    metrics_in_both = [m for m in metrics if m in subset1.columns and m in subset2.columns]

    if subset1.empty or subset2.empty:
        st.warning(f"No data for {selected_county} in one of the years")
    else:
        y1_values = subset1[metrics_in_both].iloc[0]
        y2_values = subset2[metrics_in_both].iloc[0]
        plot_year_single(y1_values, y2_values, baseline_year, other_year, metrics_in_both)

else:
    nm_row1 = state_df1[state_df1["State"].str.strip().str.lower()=="new mexico"]
    state_df2 = load_data_for_year(other_year)[0]
    state_df2.rename(columns=rename_map, inplace=True)
    nm_row2 = state_df2[state_df2["State"].str.strip().str.lower()=="new mexico"]

    # Only keep metrics present in both datasets
    metrics_in_both = [m for m in metrics if m in nm_row1.columns and m in nm_row2.columns]

    if nm_row1.empty or nm_row2.empty:
        st.warning("No New Mexico data found")
    else:
        y1_values = nm_row1[metrics_in_both].iloc[0]
        y2_values = nm_row2[metrics_in_both].iloc[0]
        plot_year_single(y1_values, y2_values, baseline_year, other_year, metrics_in_both)

st.divider()
st.caption("Data Source: CDC Environmental Justice Index | Visualization by Riley Cochrell")
