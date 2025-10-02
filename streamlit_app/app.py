"""
Streamlit app for visualizing Oregon Dark Sky SQM data. 
- It leverages the custom class object OregonSQMProcessor for data handling.
- This app provides interactive maps and charts to explore Night Sky Brightness.
- Finally, Streamlit is used to build the web interface whenever it is run.
"""

# importing necessary libraries
import sys
from pathlib import Path
import streamlit as st
from streamlit_folium import st_folium

# local import
## Add project root to path so 'shared' package is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
## importing necessary local functions, classes and variables
from shared.utils.configs import get_meas_type_config, meas_type_dict
from shared.utils.data_processing import OregonSQMProcessor
from shared.utils.visualizations import (
    create_oregon_map_folium,
    create_ranking_chart,
    create_interactive_2d_plot
)

metric_text_dict = {
"clear_nights_brightness": """<ul>
    <li>The darkest Night Sky Location for clear nights based on current data is
        Hart Mountain.</li>
    <li>Bortle scale is a visual measure of night sky brightness,
        ranging from 1 for pristine night skies to 9 at light polluted
        urban night skies.</li>
    <li>Median Night Sky Brightness shown in a log scale of Magnitudes/Arcsecond
        squared is a common measure used in astronomy.</li>
    <li>Flux Ratio shows a linear scale of night sky brightness.</li>
    </ul>""",
"cloudy_nights_brightness": """<ul>
    <li>The darkest Night Sky Location for cloudy nights based on current data is Crater Lake National Park.</li>
    <li>Cloudy nights magnify the night sky brightness contrast 
        between pristine and light polluted sites. Cloudy nights at 
        pristine night sky locations are exceedingly dark and are a natural 
        part of the wild ecosystem there.</li>
    <li>Median Night Sky Brightness is in a log scale of Magnitudes/Arcsecond
        squared, a common measure used in astronomy.</li>
        <li>Flux Ratio shows a linear scale of night sky brightness.</li>
    </ul>""",
"long_term_trends": """<ul>
    <li>Only the sites with at least 2 years of data are included to calculate the long-term trends.</li>
    <li>Rate of Change in Night Sky Brightness is compared to Prineville Reservoir State Park which is a certified Dark Sky Park.</li>
    <li>Trendline Slope is calculated from regression fit of change over time scaled by a factor of 10000.</li>
    </ul>""",
"milky_way_visibility": """<ul>
    <li>Ratio Index: Ratio of Night Sky Brightness between Milky Way and nearby sky.</li>
    <li>Difference Index: Difference in Night Sky Brightness between Milky Way and nearby sky.</li>
    </ul>""",
"% clear nights": """Percentage of Clear nights mean the nights without any clouds
    in the night sky. Measurement at each site is averaged over all months of the year."""
}

def get_add_text_dict(row, meas_type):
    # Generate additional text information for each measurement type based on a data row
    if meas_type == "clear_nights_brightness":
        txt_ = f"""
            <br>{row['x_brighter_than_darkest_night_sky']:.2f}-times brighter than the darkest Night Sky
            <br>Bortle level: {row['bortle_sky_level']}
            <br>Median Night Sky Brightness: {row['median_brightness_mag_arcsec2']:.2f} mag/arcsec²
            <br>Flux Ratio: {row['median_linear_scale_flux_ratio']:.2f}
            """
    elif meas_type == "cloudy_nights_brightness":
        txt_ = f"""
            <br>{row['x_brighter_than_darkest_night_sky']:.2f}-times brighter than the darkest Night Sky
            <br>Median Night Sky Brightness: {row['median_brightness_mag_arcsec2']:.2f} mag/arcsec²
            <br>Flux Ratio: {row['median_linear_scale_flux_ratio']:.2f}
            """
    elif meas_type == "long_term_trends":
        txt_ = f"""
            <br>Rate of Change in Night Sky Brightness compared to a certified Dark Sky Park: {row['Rate_of_Change_vs_Prineville_Reservoir_State_Park']:.1f}
            <br>Trendline Slope: {row['Regression_Line_Slope_x_10000']:.2f}
            <br>Percentage Change in Night Sky Brightness per year: {row['Percent_Change_per_year']:.1f}%
            <br>Number of Years of Data: {row['Number_of_Years_of_Data']}
            """
    elif meas_type == "milky_way_visibility":
        txt_ = f"""
            <br>Ratio Index: {row['ratio_index']:.2f}
            <br>Difference Index: {row['difference_index_mag_arcsec2']:.2f}
            """
    elif meas_type == "% clear nights":
        txt_ = f"""
            <br>Percentage of Clear (no clouds) nights: {row['percent_clear_night_samples_all_months']:.2f}%
            """
    else:
        txt_ = ""
    return txt_

@st.cache_data(ttl=3600) # caching data loading for 1 hour
def load_data():
    """
    Load OregonSQMProcessor class to handle data loading and processing.
    
    Returns
    -------
    OregonSQMProcessor
        Initialized OregonSQMProcessor object with data loaded.
    """
    return OregonSQMProcessor(data_dir=project_root / "shared" / "data")

def main():
    """
    Main function to run the Streamlit app.
    """
    # Set Streamlit page layout to wide for best use of screen space
    st.set_page_config(
        layout="wide",
        page_title="Oregon DarkSky Dashboard",
    )
    
    # Initialize map zoom and center in session state if not already set
    if "map_zoom" not in st.session_state:
        st.session_state["map_zoom"] = 6  # default zoom
    if "map_center" not in st.session_state:
        st.session_state["map_center"] = [44.0, -121.0]  # default center
 
    # Initialize clicked site from map as None
    if "clicked_sites" not in st.session_state.keys():
        st.session_state["clicked_sites"] = None
    
    # Load data using the OregonSQMProcessor class
    processor = load_data()

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
    st.title("DarkSky Oregon - Night Sky Brightness")
    
    # Description below the title, always shown in the layout
    for str_ in [
        """
        [DarkSky Oregon](https://www.darkskyoregon.org/) has 
        established a network of continuously recording Sky Quality Meters (SQMs) 
        in Oregon to measure the brightness of our night skies at the zenith.
        This dashboard shows results from their 
        [latest report (Edition #9, 2024)](https://static1.squarespace.com/static/64325bb7c8993f109f0e62cb/t/679c8b55f32ba64b8739b9c2/1738312560582/DarkSky_Oregon_SQM_Network_TechnicalReport_Edition_09_v3_cmpress.pdf)
        """,
        "<h6>Help guide</h6> ",
        """
        <ul>
        <li>Click on a 'marker' to select a SQM site. The site will be highlighted on the graphics below and 
            it's corresponding measurements will be shown. Also, note how the highlighted site ranks compared to other sites.</li>
        <li>Use the buttons on the top-right corner of each the graphics to zoom, pan, reset or save chart as an image.</li>
        <li>The dashboard will remember your site selection and map view across different questions.</li>
        </ul>
        """
        ]: st.markdown(str_, unsafe_allow_html=True)
    
    # Measurement type selection (for future extensibility)
    meas_type = st.sidebar.radio(
        "**Select a question?**",
        list(meas_type_dict.keys()),
        format_func=lambda x: meas_type_dict[x]['Question_text'],
        help="Toggle between questions"
    )
    
    # Add a refresh button in the sidebar
    with st.sidebar:
        # If the refresh button is clicked
        if st.button("Refresh"):
            # Clear all session state to reset the app
            st.session_state.clear()
            # Re-run the app to refresh all components
            st.rerun()

    # parameters bases on measurement selection
    meas_type_configs = get_meas_type_config(meas_type)
    
    # Explanation of the selected measurement type
    st.markdown("<h6>Measurements explained:</h6> ", unsafe_allow_html=True)
    st.markdown(metric_text_dict[meas_type], unsafe_allow_html=True)

    # load processed data based on the selected measurement type
    final_data_df = processor.load_processed_data(
        data_key=meas_type_configs['data_key'],
        bar_chart_col=meas_type_configs['bar_chart']['bar_chart_y_col']
    )
    
    # Layout: Two columns - Map + Scatter plot on left, Ranking chart on right
    col_left, col_middle, col_right = st.columns([0.4, 0.35, 0.25], gap="small")

    # Display map and scatter plot in the left column
    with col_left:
        # Header text for the map
        for str_ in [
            "<h3 style='font-size: 20px;'>SQM measurement site map</h3>",
            "Note: all locations shown in the map below are approximated for privacy."
        ]: st.markdown(str_, unsafe_allow_html=True)

        # If map_center is a dict, convert to list
        if isinstance(st.session_state["map_center"], dict):
            center_ = [
                st.session_state["map_center"]["lat"],
                st.session_state["map_center"]["lng"]
            ]
        else:
            center_ = st.session_state["map_center"]

        ## Determine color column for map based on measurement type
        if meas_type in ["clear_nights_brightness", "cloudy_nights_brightness"]:
            color_col = meas_type_configs['scatter_plot']['scatter_x_col']
        else:
            color_col = meas_type_configs['bar_chart']['bar_chart_y_col']

        # Create Oregon map using Folium
        cmap = create_oregon_map_folium(
            sites_df=final_data_df,
            main_col=color_col,
            zoom=st.session_state["map_zoom"],
            map_center=center_,
            highlight_sites=st.session_state["clicked_sites"]
        )
        # Display Folium map and capture click events
        map_data = st_folium(cmap, width=600, height=400)

        # Update session state with current map view if available
        if "zoom" in map_data:
            st.session_state["map_zoom"] = map_data["zoom"]
        if "center" in map_data:
            st.session_state["map_center"] = map_data["center"]
        
        # If a site was clicked map_data will have this key and value
        if map_data.get("last_object_clicked"):
            # Get the clicked object's details
            clicked_obj = map_data["last_object_clicked"]
            # Extract latitude and longitude
            lat, lng = clicked_obj.get("lat"), clicked_obj.get("lng")
            # Find the site in your DataFrame
            site_row = final_data_df[
                (abs(final_data_df["latitude"] - lat) < 1e-4) 
                &
                (abs(final_data_df["longitude"] - lng) < 1e-4)
            ]
            # If a matching site is found, get its name
            if not site_row.empty:
                new_clicked = site_row["site_name"].values
                if not (
                    isinstance(st.session_state["clicked_sites"], type(new_clicked))
                    and
                    (st.session_state["clicked_sites"] == new_clicked).all()
                ):
                    st.session_state["clicked_sites"] = new_clicked
                    st.rerun()

        # Display site information below the map
        if st.session_state.get("clicked_sites") is not None:      
            site_row = final_data_df[final_data_df["site_name"].isin(st.session_state["clicked_sites"])]
            for i, row in site_row.iterrows():
                # Display site information first line
                markdown_text = f"<p style='margin:0; padding:0;'><strong>{row['site_name']}</strong>"
                # Special note for Dark Sky Certified/Qualified sites
                if meas_type == "clear_nights_brightness":
                    if row['DarkSkyCertified'] == 'YES':
                        markdown_text += " - <strong style='color:green;'>Dark Sky Certified</strong>"
                    if (row['DarkSkyQualified'] == 'YES') and (row['DarkSkyCertified'] == 'NO'):
                        markdown_text += " - <strong style='color:orange;'>Dark Sky Qualified</strong>"
                
                # additional text based on measurement type
                add_text = get_add_text_dict(row, meas_type)
                # Append additional text to the markdown
                markdown_text += add_text
                # show the final markdown in the app
                st.markdown(markdown_text, unsafe_allow_html=True)
        

    # display ranking chart in the left column
    with col_middle:
        # adding header for the ranking chart
        for str_ in [
            f"<h3 style='font-size: 20px;'> {meas_type_configs['bar_chart']['bar_chart_title']}</h3>",
            f"Note: the x-axis is shown in {meas_type_configs['bar_chart']['bar_chart_yicks']['tickmode']} scale"
        ]: st.markdown(str_, unsafe_allow_html=True)
        
        # creating ranking chart based on the selected measurement type
        fig_bar = create_ranking_chart(
            sites_df=final_data_df,
            configs=meas_type_configs['bar_chart'],
            clicked_sites=st.session_state["clicked_sites"],
        )

        # plotting the ranking chart via plotly
        st.plotly_chart(
            fig_bar,
            use_container_width=True,
            config = {"displayModeBar": True, "displaylogo": False }
        )

    # Scatter plot directly below the map
    with col_right:
        if meas_type in ["clear_nights_brightness", "cloudy_nights_brightness"]:
            # Add header text for scatter plot
            st.markdown(
                f"<h3 style='font-size: 20px;'>{meas_type_configs['scatter_plot']['scatter_plot_title']}</h3>",
                unsafe_allow_html=True
            )

            # vertical line at 21.2 mag/arcsec2 for reference in clear nights brightness
            vline_ = 21.2 if meas_type == "clear_nights_brightness" else None

            # creating interactive 2d scatter plot based on the selected measurement type
            fig_scatter = create_interactive_2d_plot(
                df=final_data_df,
                configs=meas_type_configs['scatter_plot'],
                vline=vline_,
                clicked_sites=st.session_state["clicked_sites"]
            )
            # plotting the scatter plot via plotly
            st.plotly_chart(
                fig_scatter,
                use_container_width=False,
                config = {"displayModeBar": True, "displaylogo": False }
            )
    
    # Footer with project info
    st.markdown("---")
    st.markdown(
    """
    **Framework**: Streamlit | **Data Source**: [DarkSky Oregon SQM Network Technical Report Edition #9](https://static1.squarespace.com/static/64325bb7c8993f109f0e62cb/t/679c8b55f32ba64b8739b9c2/1738312560582/DarkSky_Oregon_SQM_Network_TechnicalReport_Edition_09_v3_cmpress.pdf)
    **Repository**:  https://github.com/ViditAg/darksky-oregon-dashboard | **Contact**: AI Tech Professional Volunteer
    """
    )

# Run the Streamlit app when the script is executed directly from the command line
if __name__ == "__main__":
    main()