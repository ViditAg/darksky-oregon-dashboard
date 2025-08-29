# importing necessary libraries
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

# local import
# Add project root to path so 'shared' package is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from shared.utils.configs import get_meas_type_config, meas_type_dict
from shared.utils.data_processing import OregonSQMProcessor
from shared.utils.visualizations import create_oregon_map, create_ranking_chart, create_interactive_2d_plot

# Cached data loader
@st.cache_data(
        ttl=3600,  # Cache data for 1 hour
        show_spinner="Loading raw SQM data..."
        )
def load_data(data_dir: Path | None = None):
    """
    Instantiate OregonSQMProcessor and load all raw data frames.

    Parameters
    ----------
    data_dir : Path | None
        Optional override for data directory. If None, processor uses its internal default.

    Returns
    -------
    dict | None
        Dictionary of raw DataFrames keyed by dataset name, or None on failure.
    """
    try:
        processor = OregonSQMProcessor(data_dir=data_dir)
        raw_dfs = processor.load_raw_data()
        # Basic validation
        if not isinstance(raw_dfs, dict) or not raw_dfs:
            st.error("Loaded data is empty or invalid.")
            return None
        return raw_dfs
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None


def main():
    """
    Main function to run the Streamlit app.
    """
    # Set Streamlit page layout to wide for best use of screen space
    st.set_page_config(
        layout="wide",
        page_title="Oregon Dark Sky Dashboard",
    )
    # Custom CSS for top margin adjustment
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1rem !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        header { margin-top: 0 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Set dashboard title and description
    st.title("[Dark Sky Oregon](https://www.darkskyoregon.org/) - Skyglow Dashboard")

    # Sidebar controls for user interaction
    st.sidebar.info(
        """**[Skyglow](https://en.wikipedia.org/wiki/Skyglow)**: Diffused unnatural luminance of the night sky, 
        caused by artificial lights scattering in the atmosphere and obscuring
         stars and celestial objects."""
    )

    # Measurement type selection (for future extensibility)
    meas_type = st.sidebar.radio(
        "**Question?**",
        list(meas_type_dict.keys()),
        format_func=lambda x: meas_type_dict[x]['Question_text'],
        help="Toggle between measurements types"
    )
    
    # parameters bases on measurement selection
    meas_type_configs = get_meas_type_config(meas_type)

    # Load all raw data from CSVs using the processor
    raw_dfs = load_data(data_dir=project_root / "shared" / "data")
    # data-frame containing results to show on dash-board
    data_df = raw_dfs[meas_type_configs['raw_df_key']]
    # Load geocode CSV and merge with selected data
    geocode_df = raw_dfs['geocode'].copy()
    # Merge geocode data with main data
    final_data_df = pd.merge(data_df, geocode_df, on="site_name", how="left")
    # Assign DarkSkyCertified status
    if meas_type in ['clear_nights_brightness', 'cloudy_nights_brightness']:
        final_data_df['DarkSkyCertified'] = 'NO'
        final_data_df.loc[final_data_df['median_brightness_mag_arcsec2'] > 21.2, 'DarkSkyCertified'] = 'YES'


    # Create Oregon map
    cmap = create_oregon_map(
        sites_df=final_data_df,
        main_col=meas_type_configs['main_col_'],
        legend_order=meas_type_configs['legend_order']
    )

    # Layout: two wide columns (map | chart), both use full container width
    col_left, col_right = st.columns([0.5, 0.5], gap="small")
    with col_left:
        st.header("SQM measurement site Map")
        st.markdown(meas_type_configs['legend_str'])
        st_folium(cmap, height=300, width=500)
    with col_right:
        st.header("Worst 20 sites")
        fig_bar = create_ranking_chart(
            sites_df=final_data_df,
            y_col=meas_type_configs['bar_metric'],
            title=meas_type_configs['y_col_print']
        )
        st.plotly_chart(
            fig_bar,
            height=1500,
            width=500,
            use_container_width=True,
            key="top_20"
        )

    # Second row: Empty (left), Scatter plot (right)
    row2_left, row2_middle, row2_right = st.columns([0.3, 0.2, 0.5], gap="small")
    if meas_type != "% clear nights":
        
        with row2_left:
            st.subheader(meas_type_configs['scatter_title'])
            fig_scatter = create_interactive_2d_plot(
                df=final_data_df,
                x_col=meas_type_configs['scatter_x'],
                y_col=meas_type_configs['scatter_y'],
                vline=meas_type_configs['vline'],
            )
            st.plotly_chart(fig_scatter)
    with row2_right:
        st.header("Pristine 20 sites")
        fig_bar2 = create_ranking_chart(
            sites_df=final_data_df,
            y_col=meas_type_configs['bar_metric'],
            title=meas_type_configs['y_col_print'],
            key="bottom_20"
        )
        st.plotly_chart(fig_bar2, height=1500, width=500, use_container_width=True, key="bottom_20")

    # Footer with project info
    st.markdown("---")
    st.markdown(
    """
    **Framework**: Streamlit | **Data Source**: [DarkSky Oregon SQM Network Technical Report Edition #9](https://static1.squarespace.com/static/64325bb7c8993f109f0e62cb/t/679c8b55f32ba64b8739b9c2/1738312560582/DarkSky_Oregon_SQM_Network_TechnicalReport_Edition_09_v3_cmpress.pdf)
    **Repository**:  https://github.com/ViditAg/darksky-oregon-dashboard | **Contact**: AI Tech Professional Volunteer
    """
    )

if __name__ == "__main__":
    main()