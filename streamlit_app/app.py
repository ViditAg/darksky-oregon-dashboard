# Streamlit implementation
# streamlit_app/app.py
"""
Streamlit implementation of Oregon Dark Sky Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import folium
from streamlit_folium import st_folium
import sys
from pathlib import Path

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent / "shared"))
from utils.data_processing import OregonSQMProcessor
from utils.visualizations import create_oregon_map, create_ranking_chart
from utils.geocoding import OregonGeocoder

# Page configuration
st.set_page_config(
    page_title="Oregon Dark Sky Dashboard - Streamlit",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main > div { padding-top: 2rem; }
    .stMetric { 
        background-color: #f0f2f6; 
        border: 1px solid #d1d5db; 
        padding: 1rem; 
        border-radius: 0.5rem; 
    }
    .dark-sky-badge {
        background: linear-gradient(90deg, #1e3a8a, #3730a3);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load and cache processed data"""
    processor = OregonSQMProcessor()
    
    # Load processed data
    sites_path = Path("shared/data/processed/sites_master.json")
    if sites_path.exists():
        sites_df = pd.read_json(sites_path)
    else:
        st.error("Processed data not found. Please run data processing pipeline.")
        return None
    
    return sites_df


def main():
    """Main Streamlit application"""
    
    # Header
    st.title("Oregon Dark Sky Dashboard")
    st.markdown("**Streamlit Implementation** - Interactive Light Pollution Visualization")
    
    # Load data
    sites_df = load_data()
    if sites_df is None:
        return
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Night type toggle
    night_type = st.sidebar.radio(
        "Measurement Type",
        ["clear", "cloudy"],
        format_func=lambda x: f"{x.title()} Nights",
        help="Toggle between clear and cloudy night measurements"
    )
    
    # Metric selection for bar chart
    metric = st.sidebar.selectbox(
        "Bar Chart Metric",
        ["brightness", "bortle", "pollution_ratio", "annual_change"],
        format_func=lambda x: {
            'brightness': 'Sky Brightness',
            'bortle': 'Bortle Scale',
            'pollution_ratio': 'Pollution Ratio', 
            'annual_change': 'Annual Change'
        }[x]
    )
    
    # Sort order for bar chart
    sort_ascending = st.sidebar.checkbox(
        "Sort Ascending",
        value=(metric == 'brightness'),  # Default ascending for brightness
        help="Check to sort from lowest to highest values"
    )
    
    # Key metrics summary
    st.subheader("Key Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sites = len(sites_df.dropna(subset=['latitude', 'longitude']))
        st.metric("Total Sites", total_sites)
    
    with col2:
        if night_type == 'clear' and 'median_brightness_mag_arcsec2' in sites_df.columns:
            darkest_brightness = sites_df['median_brightness_mag_arcsec2'].max()
            st.metric("Darkest Sky", f"{darkest_brightness:.2f} mag/arcsec²")
        else:
            st.metric("Darkest Sky", "N/A")
    
    with col3:
        certified_sites = len(sites_df[sites_df.get('dark_sky_status', 'None') != 'None'])
        st.metric("Dark Sky Places", certified_sites)
    
    with col4:
        if 'annual_percent_change' in sites_df.columns:
            avg_change = sites_df['annual_percent_change'].mean()
            st.metric("Avg Annual Change", f"{avg_change:.1f}%")
        else:
            st.metric("Avg Annual Change", "N/A")
    
    # Main content area
    col_map, col_chart = st.columns([3, 2])
    
    with col_map:
        st.subheader(f"🗺️ Oregon Light Pollution Map ({night_type.title()} Nights)")
        
        # Create and display map
        oregon_map = create_interactive_map(sites_df, night_type)
        map_data = st_folium(oregon_map, width=700, height=500)
        
        # Display legend
        st.markdown("""
        **Legend:**
        -  **Dark Green**: Pristine (≥21.5 mag/arcsec²)
        -  **Green**: Dark Sky Park Quality (≥21.2 mag/arcsec²)  
        -  **Yellow**: Rural (≥20.0 mag/arcsec²)
        -  **Orange**: Suburban (≥19.0 mag/arcsec²)
        -  **Red**: Urban (<19.0 mag/arcsec²)
        """)
    
    with col_chart:
        st.subheader(f"📊 Site Rankings")
        
        # Create and display bar chart
        ranking_chart = create_ranking_bar_chart(sites_df, metric, night_type)
        st.plotly_chart(ranking_chart, use_container_width=True)
    
    # Data table
    st.subheader("📋 Complete Site Data")
    
    # Display options
    show_all_columns = st.checkbox("Show All Columns", value=False)
    
    if show_all_columns:
        display_df = sites_df
    else:
        # Show essential columns only
        essential_cols = ['site_name', 'median_brightness_mag_arcsec2', 'bortle_scale', 
                         'dark_sky_status', 'region']
        available_cols = [col for col in essential_cols if col in sites_df.columns]
        display_df = sites_df[available_cols]
    
    # Search functionality
    search_term = st.text_input("Search sites:", placeholder="Enter site name...")
    if search_term:
        display_df = display_df[display_df['site_name'].str.contains(search_term, case=False, na=False)]
    
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Framework**: Streamlit | **Data Source**: DarkSky Oregon SQM Network Technical Report Edition #9  
    **Repository**: [GitHub Link] | **Contact**: AI Tech Professional Volunteer
    """)

if __name__ == "__main__":
    main()