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
    meas_type_dict = {
        "clear_nights_brightness": "clear_measurements",
        "cloudy_nights_brightness": "cloudy_measurements",
        "long_term_trends": "trends",
        "milky_way_visibility": "milky_way",
        "% clear nights": "cloud_coverage"
    }
    question_dict = {
        "clear_nights_brightness": "Where in Oregon is the Night Sky Most Pristine? And, Most Light Polluted? **(Clear nights)**",
        "cloudy_nights_brightness": "Where in Oregon is the Night Sky Most Pristine? And, Most Light Polluted? **(Cloudy nights)**",
        "long_term_trends": "Where are the starry night skies disappearing the fastest in Oregon?",
        "milky_way_visibility": "Where does the Milky Way stand out best in Oregon?",
        "% clear nights": "Where in Oregon are the clearest – least cloudy – night skies?"
    }
    meas_type = st.sidebar.radio(
        "**Question?**",
        list(meas_type_dict.keys()),
        format_func=lambda x: question_dict[x],
        help="Toggle between measurements types"
    )
    # save selected measurement type in a variable
    meas_type_table = meas_type_dict[meas_type]
    
    # only show bar chart when showing % of clear nights
    if meas_type == "% clear nights":
        plot_type = "Bar Chart"
        bar_metric = "percent_clear_night_samples_all_months"
    else:
        # Plot type selection
        plot_type = "Bar+Scatter Chart"
        if meas_type == "milky_way_visibility":
            bar_metric = "ratio_index"
            scatter_x = "difference_index_mag_arcsec2"
            scatter_y = "ratio_index"
        elif meas_type == "long_term_trends":
            bar_metric = "Rate_of_Change_vs_Prineville_Reservoir_State_Park"
            scatter_x = "Percent_Change_per_year"
            scatter_y = "Rate_of_Change_vs_Prineville_Reservoir_State_Park"
        else:
            bar_metric = "x_brighter_than_darkest_night_sky"
            scatter_x = "median_brightness_mag_arcsec2"
            scatter_y = "x_brighter_than_darkest_night_sky"

    # Legend string for plot
    if meas_type in ['clear_nights_brightness', 'cloudy_nights_brightness']:
        legend_str = "**Skyglow level**: 🟥 Worst  🟨 Medium  🟩 Pristine"
    elif meas_type == 'milky_way_visibility':
        legend_str = "**Milky Way visibility**: 🟥 Worst  🟨 Medium  🟩 Best"
    elif meas_type == "% clear nights":
        legend_str = "**Clear nights**: 🟥 Least  🟨 Medium  🟩 Highest"
    elif meas_type == "long_term_trends":
        legend_str = "**Disappearing starry night skies**: 🟥 Fastest  🟨 Medium  🟩 Slowest"


    if meas_type in ["clear_nights_brightness",'cloudy_nights_brightness',"long_term_trends"]:
        legend_order = ['Green', 'Yellow', 'Red']
    else:
        legend_order = ['Red', 'Yellow', 'Green']

    if meas_type in ['clear_nights_brightness', 'cloudy_nights_brightness']:
        vline = 21.2
    else:
        vline = None
    
    y_col_print_dict = {
        "ratio_index": "Ratio of linear scale SQM flux data",
        "x_brighter_than_darkest_night_sky": "Night sky brightness relative compared to the darkest site",
        "percent_clear_night_samples_all_months": "% Clear Nights over all months",
        "Rate_of_Change_vs_Prineville_Reservoir_State_Park": "Rate of Change vs. Prineville Reservoir State Park",
        "Percent_Change_per_year": "Percent Change per year",
        "median_brightness_mag_arcsec2": "Median Brightness (mag/arcsec²)",
        "difference_index_mag_arcsec2": "Difference Index (mag/arcsec²)"
    }


    # Load all raw data from CSVs using the processor
    raw_dfs = load_data(data_dir=project_root / "shared" / "data")
    # data-frame containing results to show on dash-board
    data_df = raw_dfs[meas_type_table]
    # Load geocode CSV and merge with selected data
    geocode_df = raw_dfs['geocode'].copy()
    # Merge geocode data with main data
    final_data_df = pd.merge(data_df, geocode_df, on="site_name", how="left")
    if meas_type in ['clear_nights_brightness', 'cloudy_nights_brightness']:
        final_data_df['DarkSkyCertified'] = 'NO'
        final_data_df.loc[final_data_df['median_brightness_mag_arcsec2'] > 21.2, 'DarkSkyCertified'] = 'YES'

    main_col_for_map_dict = {
        "clear_nights_brightness": "x_brighter_than_darkest_night_sky",
        "cloudy_nights_brightness": "x_brighter_than_darkest_night_sky",
        "long_term_trends": "Rate_of_Change_vs_Prineville_Reservoir_State_Park",
        "milky_way_visibility": "ratio_index",
        "% clear nights": "percent_clear_night_samples_all_months"
    }
    cmap = create_oregon_map(
        sites_df=final_data_df,
        main_col=main_col_for_map_dict[meas_type],
        legend_order=legend_order
    )

    # Layout: two wide columns (map | chart), both use full container width
    col_left, col_right = st.columns([0.5, 0.5], gap="small")
    with col_left:
        st.header("SQM measurement site Map")
        st.markdown(legend_str)
        st_folium(cmap, height=300, width=500)
    with col_right:
        st.header("Worst 20 sites")
        fig_bar = create_ranking_chart(
            sites_df=final_data_df,
            y_col=bar_metric,
            title=y_col_print_dict[bar_metric]
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
            st.subheader(f"{y_col_print_dict[scatter_x]} vs. {y_col_print_dict[scatter_y]}")
            fig_scatter = create_interactive_2d_plot(
                df=final_data_df,
                x_col=scatter_x,
                y_col=scatter_y,
                vline=vline,
            )
            st.plotly_chart(fig_scatter)
    with row2_right:
        st.header("Pristine 20 sites")
        fig_bar2 = create_ranking_chart(
            sites_df=final_data_df,
            y_col=bar_metric,
            title=y_col_print_dict[bar_metric],
            key="bottom_20"
        )
        st.plotly_chart(fig_bar2, height=1500, width=500, use_container_width=True, key="bottom_20")

    # Footer with project info
    st.markdown("---")
    st.markdown("""
    **Framework**: Streamlit | **Data Source**: [DarkSky Oregon SQM Network Technical Report Edition #9](https://static1.squarespace.com/static/64325bb7c8993f109f0e62cb/t/679c8b55f32ba64b8739b9c2/1738312560582/DarkSky_Oregon_SQM_Network_TechnicalReport_Edition_09_v3_cmpress.pdf)
    **Repository**:  https://github.com/ViditAg/darksky-oregon-dashboard | **Contact**: AI Tech Professional Volunteer
    """)

if __name__ == "__main__":
    main()