"""
Streamlit implementation of Oregon Dark Sky Dashboard
"""

# importing neccessary libraries
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
    # Set dashboard title and description
    st.title("[Dark Sky Oregon](https://www.darkskyoregon.org/) - Skyglow Dashboard")
    st.markdown("**Interactive Light Pollution Visualization")

    # Load all raw data from CSVs using the processor
    raw_dfs = load_data(data_dir=project_root / "shared" / "data")

    # Sidebar controls for user interaction
    st.sidebar.header("Dashboard Controls")

    # Measurement type selection (for future extensibility)
    meas_type_dict = {
        "clear_nights_brightness": "clear_measurements",
        "cloudy_nights_brightness": "cloudy_measurements",
        "long_term_trends": "trends",
        "milky_way_visibility": "milky_way",
        "% clear nights": "cloud_coverage"
    }
    meas_type = st.sidebar.radio(
        "Measurement Type",
        list(meas_type_dict.keys()),
        help="Toggle between measurements types"
    )
    # save selected measurement type in a variable
    meas_type_table = meas_type_dict[meas_type]
    
    # data-frame containing results to show on dash-board
    data_df = raw_dfs[meas_type_table]

    # Load geocode CSV and merge with selected data
    geocode_df = raw_dfs['geocode'].copy()

    final_data_df = pd.merge(data_df, geocode_df, on="site_name", how="left")  
    print(final_data_df)
    # Dynamic column selection based on plot type
    numeric_cols = [
        col for col in final_data_df.columns if pd.api.types.is_numeric_dtype(final_data_df[col]) and col not in ["latitude", "longitude"]
    ]
    # only show bar chart when showing % of clear nights
    if meas_type == "% clear nights":
        plot_type = "Bar Chart"
    else:
        # Plot type selection
        plot_type = st.sidebar.radio(
            "Plot Type",
            ["Bar Chart", "Scatter Plot"],
            help="Choose the type of visualization to display"
        )
    
    if plot_type == "Bar Chart":
        bar_metric = st.sidebar.selectbox(
            "Bar Chart Metric",
            numeric_cols,
            help="Choose which metric to visualize in the ranking bar chart"
        )
    else:
        scatter_x = st.sidebar.selectbox(
            "Scatter Plot X Axis", numeric_cols, index=0
        )
        scatter_y = st.sidebar.selectbox(
            "Scatter Plot Y Axis", numeric_cols, index=1 if len(numeric_cols) > 1 else 0
        )
        scatter_color = st.sidebar.selectbox("Scatter Plot Color (optional)", [None] + numeric_cols, index=0)

    # Layout: two columns (map | chart)
    col_map, col_plot = st.columns([1.1, 1])
    
    # add folium map here
    main_col_for_map_dict = {
        "clear_nights_brightness": "x_brighter_than_darkest_night_sky",
        "cloudy_nights_brightness": "x_brighter_than_darkest_night_sky",
        "long_term_trends": "Rate_of_Change_vs_Prineville_Reservoir_State_Park",
        "milky_way_visibility": "ratio_index",
        "% clear nights": "percent_clear_night_samples_all_months"
    }
    cmap = create_oregon_map(
        sites_df=final_data_df,
        main_col=main_col_for_map_dict[meas_type]
    )

    with col_map:
        st.subheader("SQM measurement site Map")
        st_folium(cmap, height=600, use_container_width=True)

    with col_plot:
        if plot_type == "Bar Chart":
            st.subheader("Ranking")
            fig_bar = create_ranking_chart(
                sites_df=final_data_df,
                y_col=bar_metric
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.subheader("Scatter Plot")
            fig_scatter = create_interactive_2d_plot(
                df=final_data_df,
                x_col=scatter_x,
                y_col=scatter_y,
                title=f"{scatter_y} vs {scatter_x}"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    

    # Footer with project info
    st.markdown("---")
    st.markdown("""
    **Framework**: Streamlit | **Data Source**: [DarkSky Oregon SQM Network Technical Report Edition #9](https://static1.squarespace.com/static/64325bb7c8993f109f0e62cb/t/679c8b55f32ba64b8739b9c2/1738312560582/DarkSky_Oregon_SQM_Network_TechnicalReport_Edition_09_v3_cmpress.pdf)
    **Repository**:  https://github.com/ViditAg/darksky-oregon-dashboard | **Contact**: AI Tech Professional Volunteer
    """)

if __name__ == "__main__":
    main()