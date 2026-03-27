import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import os

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="UHI Dashboard — Port Harcourt",
    page_icon="🌆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0a0e14; color: #e8f0fa; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111820;
        border-right: 1px solid #1e2d40;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #111820;
        border: 1px solid #1e2d40;
        border-radius: 6px;
        padding: 16px;
    }

    [data-testid="stMetricLabel"] { color: #6a8aaa !important; font-size: 12px !important; }
    [data-testid="stMetricValue"] { color: #e8f0fa !important; font-size: 28px !important; }

    /* Headers */
    h1, h2, h3 { color: #e8f0fa !important; }

    /* Dataframe */
    [data-testid="stDataFrame"] { border: 1px solid #1e2d40; border-radius: 6px; }

    /* Divider */
    hr { border-color: #1e2d40; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #111820; border-radius: 6px; }
    .stTabs [data-baseweb="tab"] { color: #6a8aaa; }
    .stTabs [aria-selected="true"] { color: #ff5c3a !important; border-bottom-color: #ff5c3a !important; }

    /* Insight boxes */
    .insight-box {
        background-color: #111820;
        border: 1px solid #1e2d40;
        border-left: 4px solid #ff5c3a;
        border-radius: 4px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .insight-title { color: #ffaa44; font-weight: bold; font-size: 14px; margin-bottom: 6px; }
    .insight-text  { color: #a0b8cc; font-size: 13px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA — embedded directly so no CSV files needed
# ============================================================

@st.cache_data
def load_data():
    # Yearly trend
    yearly = pd.DataFrame({
        'year': [2019, 2020, 2021, 2022, 2023, 2024],
        'avg_day_temp_C':   [29.57, 27.95, 27.60, 27.35, 27.44, 27.05],
        'avg_night_temp_C': [21.70, 21.88, 21.93, 21.36, 22.60, 22.63],
        'avg_ndvi':         [0.5635, 0.4230, 0.4057, 0.3613, 0.4441, 0.4174]
    })

    # Seasonal
    seasonal = pd.DataFrame({
        'season':           ['Early Rains\n(Mar–May)', 'Dry Season\n(Dec–Feb)',
                             'Late Rains\n(Sep–Nov)', 'Peak Rains\n(Jun–Aug)'],
        'avg_day_temp_C':   [28.66, 27.78, 27.42, 26.17],
        'avg_night_temp_C': [22.75, 22.38, 21.92, 21.22],
        'avg_ndvi':         [0.4662, 0.4179, 0.4071, 0.3597]
    })

    # Zone summary
    zones = pd.DataFrame({
        'zone':             ['Vegetated', 'Dense Vegetation', 'Urban-Suburban'],
        'avg_day_temp_C':   [27.97, 27.49, 26.91],
        'avg_night_temp_C': [22.49, 23.14, 21.49],
        'avg_ndvi':         [0.4735, 0.6330, 0.3250]
    })

    # GHSL
    ghsl = pd.DataFrame({
        'urban_class': ['High Urban', 'Urban', 'Suburban', 'Rural'],
        'pixel_count': [18156, 8756, 7556, 26032],
        'avg_built_up_m2': [4281.48, 1441.61, 161.20, 0.0]
    })

    # Hotspots
    hotspots = pd.DataFrame({
        'rank':        list(range(1, 11)),
        'period':      ['April 2020','March 2020','April 2021','October 2022',
                        'December 2019','March 2023','May 2020','February 2020',
                        'April 2022','January 2024'],
        'year':        [2020,2020,2021,2022,2019,2023,2020,2020,2022,2024],
        'month':       [4,3,4,10,12,3,5,2,4,1],
        'avg_lst_day': [31.18,30.12,30.08,29.80,29.57,29.41,29.21,29.20,28.95,28.44],
        'avg_ndvi':    [0.5442,0.4533,0.4626,0.2524,0.5635,0.5090,0.5298,0.3850,0.3927,0.4219],
        'zone':        ['Vegetated','Vegetated','Vegetated','Urban-Suburban',
                        'Vegetated','Vegetated','Vegetated','Urban-Suburban',
                        'Urban-Suburban','Vegetated']
    })

    return yearly, seasonal, zones, ghsl, hotspots

yearly, seasonal, zones, ghsl, hotspots = load_data()

COLORS = {
    'hot':    '#ff3a1a',
    'warm':   '#ff8c44',
    'yellow': '#ffaa44',
    'blue':   '#44aaff',
    'green':  '#44dd88',
    'purple': '#aa66ff',
    'muted':  '#6a8aaa',
    'bg':     '#0a0e14',
    'surface':'#111820',
    'border': '#1e2d40'
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#6a8aaa', family='monospace'),
    xaxis=dict(gridcolor='#1e2d40', showgrid=True),
    yaxis=dict(gridcolor='#1e2d40', showgrid=True),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#a0b8cc')),
    margin=dict(t=40, b=40, l=40, r=20)
)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🌆 UHI Dashboard")
    st.markdown("**Port Harcourt, Nigeria**")
    st.markdown("---")

    st.markdown("### 📊 Study Info")
    st.markdown("**Period:** 2019 – 2024")
    st.markdown("**Tool:** Apache PySpark")
    st.markdown("**Resolution:** 1 km")
    st.markdown("**Projection:** WGS84")
    st.markdown("---")

    st.markdown("### 🗺️ Bounding Box")
    st.code("Lat: 4.70 – 4.95\nLon: 6.90 – 7.10", language=None)
    st.markdown("---")

    st.markdown("### 📁 Data Sources")
    st.markdown("- MODIS MOD11A2 (LST)")
    st.markdown("- MODIS MOD13A2 (NDVI)")
    st.markdown("- GHSL R2023A (Built-up)")
    st.markdown("---")

    year_filter = st.multiselect(
        "Filter Years",
        options=[2019,2020,2021,2022,2023,2024],
        default=[2019,2020,2021,2022,2023,2024]
    )

    st.markdown("---")
    st.markdown("<div style='color:#6a8aaa;font-size:11px'>Built with PySpark · Streamlit · Plotly · Folium</div>",
                unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div style='border-left:4px solid #ff5c3a; padding-left:20px; margin-bottom:32px'>
    <div style='color:#ff5c3a;font-size:11px;letter-spacing:3px;text-transform:uppercase;margin-bottom:6px'>
        Urban Heat Island Analysis · PySpark Pipeline
    </div>
    <h1 style='font-size:42px;font-weight:900;margin:0;color:#e8f0fa'>
        Port Harcourt <span style='color:#ff5c3a'>Heat Intelligence</span>
    </h1>
    <p style='color:#6a8aaa;font-family:monospace;margin-top:8px'>
        Study Period: 2019–2024 &nbsp;|&nbsp; MODIS LST + NDVI + GHSL &nbsp;|&nbsp; Apache PySpark
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# KPI CARDS
# ============================================================
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("🌡️ Peak Temp",    "31.18°C",  "April 2020")
k2.metric("🏙️ UHI Index",   "−1.05°C",  "Inverse UHI")
k3.metric("🏗️ Urban Cover", "56.97%",   "34,468 pixels")
k4.metric("🌿 Avg NDVI",    "0.417",    "Moderate cover")
k5.metric("☀️ Hot Season",  "28.66°C",  "Early Rains")
k6.metric("📉 Temp Trend",  "−2.52°C",  "2019 → 2024")

st.markdown("---")


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Temperature Trends",
    "🌿 Vegetation & Zones",
    "🏙️ Urban Structure",
    "🔥 Hotspots",
    "🗺️ Map"
])


# ────────────────────────────────────────────────────────────
# TAB 1: TEMPERATURE TRENDS
# ────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### Temperature Trends — Port Harcourt (2019–2024)")

    # Filter by selected years
    yearly_f = yearly[yearly['year'].isin(year_filter)]

    col1, col2 = st.columns(2)

    # Yearly Day + Night
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly_f['year'], y=yearly_f['avg_day_temp_C'],
            name='Day Temp', mode='lines+markers',
            line=dict(color=COLORS['hot'], width=2.5),
            marker=dict(size=8, color=COLORS['hot']),
            fill='tozeroy', fillcolor='rgba(255,58,26,0.06)'
        ))
        fig.add_trace(go.Scatter(
            x=yearly_f['year'], y=yearly_f['avg_night_temp_C'],
            name='Night Temp', mode='lines+markers',
            line=dict(color=COLORS['blue'], width=2),
            marker=dict(size=6, color=COLORS['blue']),
            fill='tozeroy', fillcolor='rgba(68,170,255,0.04)'
        ))
        fig.update_layout(**PLOTLY_LAYOUT, title='Yearly Day & Night Temperature',
                          yaxis_title='Temperature (°C)', height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Seasonal bar
    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=seasonal['season'], y=seasonal['avg_day_temp_C'],
            name='Day Temp', marker_color=[COLORS['hot'], COLORS['warm'],
                                           COLORS['yellow'], COLORS['blue']],
            text=seasonal['avg_day_temp_C'].apply(lambda x: f"{x}°C"),
            textposition='outside', textfont=dict(color='#a0b8cc', size=11)
        ))
        fig2.add_trace(go.Bar(
            x=seasonal['season'], y=seasonal['avg_night_temp_C'],
            name='Night Temp',
            marker_color=['rgba(255,58,26,0.3)','rgba(255,140,68,0.3)',
                          'rgba(255,170,68,0.3)','rgba(68,170,255,0.3)']
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, title='Seasonal Temperature Breakdown',
                           yaxis_title='Temperature (°C)', barmode='group',
                           yaxis_range=[20, 31], height=320)
        st.plotly_chart(fig2, use_container_width=True)

    # Day–Night spread + NDVI
    col3, col4 = st.columns(2)

    with col3:
        yearly_f = yearly_f.copy()
        yearly_f['spread'] = yearly_f['avg_day_temp_C'] - yearly_f['avg_night_temp_C']
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=yearly_f['year'], y=yearly_f['spread'],
            name='Day–Night Spread', mode='lines+markers',
            line=dict(color=COLORS['yellow'], width=2.5),
            marker=dict(size=8),
            fill='tozeroy', fillcolor='rgba(255,170,68,0.08)'
        ))
        fig3.update_layout(**PLOTLY_LAYOUT, title='Day–Night Temperature Spread',
                           yaxis_title='°C Difference', height=300)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        fig4.add_trace(go.Bar(
            x=yearly_f['year'], y=yearly_f['avg_day_temp_C'],
            name='Day Temp', marker_color='rgba(255,92,58,0.5)'
        ), secondary_y=False)
        fig4.add_trace(go.Scatter(
            x=yearly_f['year'], y=yearly_f['avg_ndvi'],
            name='NDVI', mode='lines+markers',
            line=dict(color=COLORS['green'], width=2.5),
            marker=dict(size=7)
        ), secondary_y=True)
        fig4.update_layout(**PLOTLY_LAYOUT, title='Temperature vs NDVI', height=300)
        fig4.update_yaxes(title_text='Day Temp (°C)', secondary_y=False,
                          gridcolor='#1e2d40', color='#6a8aaa')
        fig4.update_yaxes(title_text='NDVI', secondary_y=True,
                          gridcolor=None, color=COLORS['green'])
        st.plotly_chart(fig4, use_container_width=True)

    # Data table
    st.markdown("#### 📋 Yearly Data Table")
    display_yearly = yearly_f.copy()
    display_yearly.columns = ['Year','Avg Day Temp (°C)','Avg Night Temp (°C)','Avg NDVI','Day–Night Spread']
    st.dataframe(display_yearly, use_container_width=True, hide_index=True)


# ────────────────────────────────────────────────────────────
# TAB 2: VEGETATION & ZONES
# ────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### Vegetation & Zone Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # NDVI trend
        yearly_f2 = yearly[yearly['year'].isin(year_filter)]
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=yearly_f2['year'], y=yearly_f2['avg_ndvi'],
            mode='lines+markers',
            line=dict(color=COLORS['green'], width=3),
            marker=dict(size=9, color=COLORS['green'],
                        line=dict(color='#0a0e14', width=2)),
            fill='tozeroy', fillcolor='rgba(68,221,136,0.07)',
            name='NDVI'
        ))
        fig5.add_hline(y=0.4, line_dash='dash',
                       line_color='rgba(255,170,68,0.5)',
                       annotation_text='Moderate threshold (0.4)',
                       annotation_font_color='#ffaa44')
        fig5.update_layout(**PLOTLY_LAYOUT, title='NDVI Trend 2019–2024',
                           yaxis_title='NDVI Value', yaxis_range=[0.2, 0.7], height=320)
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        # Zone comparison — grouped bar
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            x=zones['zone'], y=zones['avg_day_temp_C'],
            name='Day Temp (°C)',
            marker_color=[COLORS['warm'], COLORS['green'], COLORS['blue']],
            text=zones['avg_day_temp_C'].apply(lambda x: f"{x}°C"),
            textposition='outside', textfont=dict(color='#a0b8cc', size=11)
        ))
        fig6.add_trace(go.Bar(
            x=zones['zone'], y=zones['avg_ndvi'] * 30,  # scale for visibility
            name='NDVI ×30',
            marker_color=['rgba(255,140,68,0.4)','rgba(68,221,136,0.4)','rgba(68,170,255,0.4)']
        ))
        fig6.update_layout(**PLOTLY_LAYOUT, title='Temperature & NDVI by Zone',
                           yaxis_title='Value', barmode='group',
                           yaxis_range=[0, 35], height=320)
        st.plotly_chart(fig6, use_container_width=True)

    # Zone summary table
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Zone Summary Table")
        st.dataframe(zones.rename(columns={
            'zone':'Zone','avg_day_temp_C':'Day Temp (°C)',
            'avg_night_temp_C':'Night Temp (°C)','avg_ndvi':'Avg NDVI'
        }), use_container_width=True, hide_index=True)

    with col4:
        st.markdown("#### Seasonal Summary Table")
        st.dataframe(seasonal.rename(columns={
            'season':'Season','avg_day_temp_C':'Day Temp (°C)',
            'avg_night_temp_C':'Night Temp (°C)','avg_ndvi':'Avg NDVI'
        }), use_container_width=True, hide_index=True)

    # Insights
    st.markdown("---")
    st.markdown("### 💡 Vegetation Insights")
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("""
        <div class='insight-box'>
            <div class='insight-title'>🌿 Vegetation Decline</div>
            <div class='insight-text'>NDVI dropped from 0.5635 (2019) to 0.4174 (2024) — a 25.9% reduction
            in vegetation density, indicating ongoing urban expansion and land-use change in Port Harcourt.</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown("""
        <div class='insight-box'>
            <div class='insight-title'>🏙️ Inverse UHI Pattern</div>
            <div class='insight-text'>Urban zones (26.91°C) are slightly cooler than vegetated areas (27.97°C).
            This inverse UHI may reflect Port Harcourt's coastal location and high humidity moderating urban heat.</div>
        </div>
        """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# TAB 3: URBAN STRUCTURE
# ────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### GHSL Urban Structure — Port Harcourt")

    col1, col2 = st.columns(2)

    with col1:
        fig7 = go.Figure(go.Pie(
            labels=ghsl['urban_class'],
            values=ghsl['pixel_count'],
            hole=0.6,
            marker=dict(
                colors=[COLORS['hot'], COLORS['warm'], COLORS['yellow'], COLORS['green']],
                line=dict(color='#111820', width=3)
            ),
            textfont=dict(color='#e8f0fa', size=12),
            hovertemplate='<b>%{label}</b><br>Pixels: %{value:,}<br>Share: %{percent}<extra></extra>'
        ))
        fig7.update_layout(
            **PLOTLY_LAYOUT,
            title='Urban Land Classification (GHSL)',
            annotations=[dict(text='56.97%<br>Urban', x=0.5, y=0.5,
                              font_size=16, showarrow=False,
                              font_color='#e8f0fa')],
            height=380
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        fig8 = go.Figure(go.Bar(
            x=ghsl['urban_class'],
            y=ghsl['avg_built_up_m2'],
            marker_color=[COLORS['hot'], COLORS['warm'], COLORS['yellow'], COLORS['green']],
            text=ghsl['avg_built_up_m2'].apply(lambda x: f"{x:,.0f} m²"),
            textposition='outside',
            textfont=dict(color='#a0b8cc', size=11)
        ))
        fig8.update_layout(
            **PLOTLY_LAYOUT,
            title='Average Built-up Surface per Zone (m²)',
            yaxis_title='Built-up Surface (m²)',
            height=380
        )
        st.plotly_chart(fig8, use_container_width=True)

    # GHSL Table
    st.markdown("#### 📋 GHSL Data Table")
    ghsl_display = ghsl.copy()
    ghsl_display['percentage'] = (ghsl_display['pixel_count'] / ghsl_display['pixel_count'].sum() * 100).round(2).astype(str) + '%'
    ghsl_display.columns = ['Urban Class', 'Pixel Count', 'Avg Built-up (m²)', 'Coverage %']
    st.dataframe(ghsl_display, use_container_width=True, hide_index=True)

    # Urban metrics
    st.markdown("---")
    st.markdown("### 🏗️ Urban Coverage Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Pixels",    "60,500",  "Study area")
    m2.metric("Urban Pixels",    "34,468",  "Built-up")
    m3.metric("High Urban",      "18,156",  "30.01%")
    m4.metric("Avg Built-up",    "4,281 m²", "High Urban zone")


# ────────────────────────────────────────────────────────────
# TAB 4: HOTSPOTS
# ────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🔥 Heat Hotspot Detection — Top 10 Hottest Months")

    col1, col2 = st.columns([3, 2])

    with col1:
        # Horizontal bar chart
        hotspots_sorted = hotspots.sort_values('avg_lst_day')
        colors_hs = [COLORS['hot'] if t >= 30 else COLORS['warm']
                     for t in hotspots_sorted['avg_lst_day']]
        fig9 = go.Figure(go.Bar(
            x=hotspots_sorted['avg_lst_day'],
            y=hotspots_sorted['period'],
            orientation='h',
            marker_color=colors_hs,
            text=hotspots_sorted['avg_lst_day'].apply(lambda x: f"{x}°C"),
            textposition='outside',
            textfont=dict(color='#a0b8cc', size=11)
        ))
        fig9.add_vline(x=30, line_dash='dash',
                       line_color='rgba(255,58,26,0.5)',
                       annotation_text='30°C threshold',
                       annotation_font_color=COLORS['hot'])
        fig9.update_layout(
            **PLOTLY_LAYOUT,
            title='Top 10 Hottest Months',
            xaxis_title='Avg Day Temperature (°C)',
            xaxis_range=[27, 32],
            height=400
        )
        st.plotly_chart(fig9, use_container_width=True)

    with col2:
        # Scatter — temp vs NDVI
        fig10 = go.Figure(go.Scatter(
            x=hotspots['avg_ndvi'],
            y=hotspots['avg_lst_day'],
            mode='markers+text',
            marker=dict(
                size=14,
                color=hotspots['avg_lst_day'],
                colorscale=[[0,'#44aaff'],[0.5,'#ffaa44'],[1,'#ff3a1a']],
                showscale=True,
                colorbar=dict(title='°C', tickfont=dict(color='#6a8aaa')),
                line=dict(color='#111820', width=2)
            ),
            text=hotspots['year'].astype(str),
            textposition='top center',
            textfont=dict(color='#a0b8cc', size=10),
            hovertemplate='<b>%{text}</b><br>Temp: %{y}°C<br>NDVI: %{x}<extra></extra>'
        ))
        fig10.update_layout(
            **PLOTLY_LAYOUT,
            title='Temp vs NDVI (Hotspots)',
            xaxis_title='NDVI', yaxis_title='Avg Day Temp (°C)',
            height=400
        )
        st.plotly_chart(fig10, use_container_width=True)

    # Hotspot table
    st.markdown("#### 📋 Hotspot Details Table")
    hs_display = hotspots[['rank','period','avg_lst_day','avg_ndvi','zone']].copy()
    hs_display.columns = ['Rank','Period','Avg Day Temp (°C)','NDVI','Zone']
    st.dataframe(hs_display, use_container_width=True, hide_index=True)

    # Insights
    st.markdown("---")
    st.markdown("### 💡 Hotspot Insights")
    col3, col4, col5 = st.columns(3)
    with col3:
        st.markdown("""
        <div class='insight-box'>
            <div class='insight-title'>🔥 2020 Heat Cluster</div>
            <div class='insight-text'>4 of the top 10 hottest months occurred in 2020,
            making it the most thermally intense year despite not having the highest annual average.</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class='insight-box'>
            <div class='insight-title'>🌧️ Seasonal Pattern</div>
            <div class='insight-text'>Peak Rains (Jun–Aug) is the coolest season at 26.17°C.
            Early Rains (Mar–May) is hottest at 28.66°C — pre-rain heat buildup is most intense.</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown("""
        <div class='insight-box'>
            <div class='insight-title'>📉 Cooling Trend</div>
            <div class='insight-text'>Avg daytime temp dropped from 29.57°C (2019) to 27.05°C (2024),
            a 2.52°C decline over five years — possibly linked to increased cloud cover.</div>
        </div>
        """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# TAB 5: MAP
# ────────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 🗺️ Port Harcourt — Study Area Map")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Folium map
        m = folium.Map(
            location=[4.825, 7.0],
            zoom_start=12,
            tiles='CartoDB dark_matter'
        )

        # Study area bounding box
        folium.Rectangle(
            bounds=[[4.70, 6.90], [4.95, 7.10]],
            color='#ff5c3a',
            fill=True,
            fill_color='#ff5c3a',
            fill_opacity=0.08,
            weight=2,
            tooltip='Study Area Boundary'
        ).add_to(m)

        # Key locations with temperature markers
        locations = [
            {'name': 'Port Harcourt City Centre', 'lat': 4.8156, 'lon': 7.0498,
             'temp': 27.44, 'type': 'urban', 'color': 'red'},
            {'name': 'Trans Amadi Industrial', 'lat': 4.8420, 'lon': 7.0180,
             'temp': 28.10, 'type': 'industrial', 'color': 'darkred'},
            {'name': 'GRA Phase 1', 'lat': 4.7830, 'lon': 7.0230,
             'temp': 26.90, 'type': 'residential', 'color': 'orange'},
            {'name': 'Rumuola', 'lat': 4.8310, 'lon': 7.0140,
             'temp': 27.80, 'type': 'urban', 'color': 'red'},
            {'name': 'Eleme (Peri-urban)', 'lat': 4.7600, 'lon': 7.1200,
             'temp': 26.50, 'type': 'peri-urban', 'color': 'green'},
            {'name': 'Rumuigbo', 'lat': 4.8650, 'lon': 7.0350,
             'temp': 27.20, 'type': 'residential', 'color': 'orange'},
            {'name': 'Diobu', 'lat': 4.7980, 'lon': 6.9950,
             'temp': 28.30, 'type': 'urban', 'color': 'darkred'},
            {'name': 'Mile 1 Market Area', 'lat': 4.7890, 'lon': 6.9840,
             'temp': 28.90, 'type': 'commercial', 'color': 'darkred'},
            {'name': 'Choba (University)', 'lat': 4.9000, 'lon': 6.9200,
             'temp': 26.30, 'type': 'suburban', 'color': 'lightgreen'},
            {'name': 'Alakahia', 'lat': 4.8800, 'lon': 6.9400,
             'temp': 26.80, 'type': 'suburban', 'color': 'green'},
        ]

        for loc in locations:
            folium.CircleMarker(
                location=[loc['lat'], loc['lon']],
                radius=10,
                color=loc['color'],
                fill=True,
                fill_color=loc['color'],
                fill_opacity=0.7,
                tooltip=f"<b>{loc['name']}</b><br>Est. Temp: {loc['temp']}°C<br>Type: {loc['type']}"
            ).add_to(m)

        # UHI index marker
        folium.Marker(
            location=[4.825, 7.0],
            popup=folium.Popup(
                '<b>Port Harcourt UHI Study</b><br>'
                'UHI Index: −1.05°C<br>'
                'Urban Coverage: 56.97%<br>'
                'Period: 2019–2024',
                max_width=200
            ),
            icon=folium.Icon(color='red', icon='fire', prefix='fa')
        ).add_to(m)

        st_folium(m, width=700, height=500)

    with col2:
        st.markdown("#### 📍 Location Legend")
        st.markdown("""
        | Color | Zone Type |
        |---|---|
        | 🔴 Dark Red | High Urban / Commercial |
        | 🟠 Orange | Residential |
        | 🟢 Green | Suburban / Peri-urban |
        | 🟡 Light Green | University / Low density |
        """)

        st.markdown("---")
        st.markdown("#### 📊 Area Statistics")
        st.metric("Study Area", "~550 km²")
        st.metric("City Population", "~1.9M")
        st.metric("Coordinates", "4.82°N, 7.05°E")
        st.metric("Climate Zone", "Tropical Wet")

        st.markdown("---")
        st.markdown("#### 🌡️ Temperature Range")
        st.metric("Min Recorded", "26.17°C", "Peak Rains")
        st.metric("Max Recorded", "31.18°C", "April 2020")
        st.metric("Avg (2019–24)", "27.66°C")

        st.markdown("---")
        st.markdown("""
        <div class='insight-box'>
            <div class='insight-title'>🗺️ Map Note</div>
            <div class='insight-text'>Markers show representative
            temperature estimates per neighbourhood based on MODIS
            1km resolution data and zone classification.</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style='display:flex;justify-content:space-between;align-items:center;
            color:#6a8aaa;font-family:monospace;font-size:11px;padding:8px 0'>
    <span>Data: NASA MODIS MOD11A2 · MOD13A2 · GHSL R2023A · Processed with Apache PySpark</span>
    <span style='color:#ff5c3a'>UHI-PH · 2019–2024</span>
</div>
""", unsafe_allow_html=True)
