import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (The "Professional Look")
st.set_page_config(
    page_title="UK Pharma Supply Risk Dashboard",
    page_icon="💊",
    layout="wide"
)

# Custom CSS to match NHS/Pharma professional aesthetic
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# 2. Load the Generated Data
@st.cache_data
def load_data():
    return pd.read_csv('UK_Pharma_Supply_Risk.csv')

df = load_data()

# 3. Sidebar - The "Stress Test" Controls
st.sidebar.header("🕹️ Brexit Stress Test")
st.sidebar.info("Adjust the sliders to simulate real-world UK border friction.")

border_delay = st.sidebar.slider(
    "Customs/Port Delay (Days)", 
    min_value=0, max_value=20, value=0, help="Simulates congestion at Dover-Calais/Eurotunnel"
)

# 4. Logic: Recalculate Risk based on User Input
# We increase lead time and decrease the "runway" of stock left
df['Live_Lead_Time'] = df['Predicted_Lead_Time'] + border_delay
df['Live_Runway'] = (df['Stock_Runway_Days'] - border_delay).apply(lambda x: max(x, 0))

# Redefine Risk Level
def get_status(runway):
    if runway <= 3: return "🔴 CRITICAL"
    if runway <= 7: return "🟡 WARNING"
    return "🟢 STABLE"

df['Status'] = df['Live_Runway'].apply(get_status)

# 5. Header Section
st.title("🇬🇧 UK Pharma Supply Resilience Optimizer")
st.markdown(f"**Scenario:** Modeling the impact of a **{border_delay} day** logistics delay on NHS critical medicine stock.")

# 6. Top KPIs
col1, col2, col3 = st.columns(3)
with col1:
    critical_count = len(df[df['Status'] == "🔴 CRITICAL"])
    st.metric("Critical SKUs", critical_count, delta=f"+{critical_count}" if border_delay > 0 else 0, delta_color="inverse")
with col2:
    avg_runway = round(df['Live_Runway'].mean(), 1)
    st.metric("Avg. Stock Runway (Days)", f"{avg_runway}d")
with col3:
    risk_value = f"£{int(df[df['Status'] != '🟢 STABLE']['Unit_Cost_GBP'].sum()):,}"
    st.metric("Inventory Value at Risk", risk_value)

# 7. Visualizations
st.divider()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Inventory Risk Distribution")
    fig = px.scatter(
        df, x="Live_Runway", y="Live_Lead_Time",
        color="Status", size="Unit_Cost_GBP", hover_name="Drug_Name",
        color_discrete_map={"🔴 CRITICAL": "#ff4b4b", "🟡 WARNING": "#ffa500", "🟢 STABLE": "#00873c"},
        labels={"Live_Runway": "Days of Stock Remaining", "Live_Lead_Time": "Total Lead Time (Days)"}
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Route Vulnerability")
    route_risk = df.groupby('Route')['Live_Runway'].mean().reset_index()
    fig2 = px.bar(route_risk, x='Route', y='Live_Runway', color='Route', title="Avg Runway by Entry Point")
    st.plotly_chart(fig2, use_container_width=True)

# 8. Data Table
st.subheader("📋 Detailed Risk Registry")
st.dataframe(
    df[['Drug_Name', 'Category', 'Route', 'Storage_Req', 'Status', 'Live_Runway']].sort_values('Live_Runway'),
    use_container_width=True
)
