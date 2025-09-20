"""
Streamlit app for visualizing Oregon Dark Sky SQM data. 
- This app provides interactive maps and charts to explore Night Sky Brightness.
- It leverages the custom class object OregonSQMProcessor for data handling.
- Plotly/Folium for creating visualizations. 
- Finally, Streamlit is used to build the web interface whenever it is run.
"""

# importing necessary libraries
import sys
from pathlib import Path
import streamlit as st


from streamlit_folium import st_folium
from streamlit_plotly_events import plotly_events


# local import
# Add project root to path so 'shared' package is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from shared.utils.configs import get_meas_type_config, meas_type_dict
from shared.utils.data_processing import OregonSQMProcessor
from shared.utils.visualizations import create_oregon_map_folium, create_ranking_chart, create_interactive_2d_plot

@st.cache_data(ttl=3600)
def load_data(meas_type_configs):
    # Initialize processor and load data
    processor = OregonSQMProcessor(data_dir=project_root / "shared" / "data")

    # Load raw data
    final_data_df = processor.load_processed_data(
        data_key=meas_type_configs['data_key'],
        bar_chart_col=meas_type_configs['bar_chart_y_col']
    )
    return final_data_df

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
    st.title("[Dark Sky Oregon](https://www.darkskyoregon.org/) - Night Sky Brightness at the Zenith")
    # Description
    st.markdown(
        """
        [Oregon Skyglow Measurement Network](https://www.darkskyoregon.org/oregon-skyglow-measurement-network) : DarkSky Oregon has 
        established a network of continuously recording Sky Quality Meters (SQMs) in Oregon to measure the brightness of our night skies,
         due to both man-made artificial light and natural light. Here we show results from their latest report (Edition #9, 2024)
    """
        )
    # Sidebar controls for user interaction
    st.sidebar.info(
        """ Select a question below and select a site on the map to explore how brightness measurements look across different locations."""
    )
    
    # Measurement type selection (for future extensibility)
    meas_type = st.sidebar.radio(
        "**Question?**",
        list(meas_type_dict.keys()),
        format_func=lambda x: meas_type_dict[x]['Question_text'],
        help="Toggle between questions"
    )
    
    # Add a refresh button in the sidebar
    with st.sidebar:
        # If the refresh button is clicked
        if st.button("Refresh Dashboard"):
            # Clear all session state to reset the app
            st.session_state.clear()
            # Re-run the app to refresh all components
            st.rerun()

    # Initialize map zoom and center in session state if not already set
    if "map_zoom" not in st.session_state:
        st.session_state["map_zoom"] = 6  # default zoom
    if "map_center" not in st.session_state:
        st.session_state["map_center"] = [44.0, -121.0]  # default center
 
    # Initialize clicked site from map as None
    if "clicked_sites" not in st.session_state.keys():
        st.session_state["clicked_sites"] = None

    # parameters bases on measurement selection
    meas_type_configs = get_meas_type_config(meas_type)
    
    # load data
    final_data_df = load_data(meas_type_configs)

    # Layout: Two columns - Map + Scatter plot on left, Ranking chart on right
    col_left, col_middle, col_right = st.columns([0.4, 0.35, 0.25], gap="small")

    # Display map and scatter plot in the left column
    with col_left:
        # Sub-Header for the map
        st.markdown(
            "<h3 style='font-size: 20px;'>SQM measurement site map</h3>"
            , unsafe_allow_html=True
        )
        st.markdown(
            """Click on a SQM site on the map to see its night sky brightness measurement 
            and how it ranks compared to other sites. While selecting the next site you may need 
            to click the site again for the app to re-load. You can also zoom/pan the map 
            and the app will remember your view across different questions."""
            )

        # If map_center is a dict, convert to list
        if isinstance(st.session_state["map_center"], dict):
            center_ = [st.session_state["map_center"]["lat"], st.session_state["map_center"]["lng"]]
        else:
            center_ = st.session_state["map_center"]

        # Create Oregon map using Folium
        cmap = create_oregon_map_folium(
            sites_df=final_data_df,
            main_col=meas_type_configs['bar_chart_y_col'],
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
                (abs(final_data_df["latitude"] - lat) < 1e-4) & (abs(final_data_df["longitude"] - lng) < 1e-4)
            ]
            # If a matching site is found, get its name
            if not site_row.empty:
                new_clicked = site_row["site_name"].values
                if not (
                    isinstance(st.session_state["clicked_sites"], type(new_clicked))
                    and (st.session_state["clicked_sites"] == new_clicked).all()
                ):
                    st.session_state["clicked_sites"] = new_clicked
                    st.rerun()

        # Display site information below the map
        if st.session_state.get("clicked_sites") is not None:      
            site_row = final_data_df[final_data_df["site_name"].isin(st.session_state["clicked_sites"])]
            for i, row in site_row.iterrows():
                markdown_text = "<p style='margin:0; padding:0;'><strong>{0}</strong>".format(row["site_name"])
                if meas_type == "clear_nights_brightness":
                    if row['DarkSkyCertified'] == 'YES':
                        markdown_text += " - <strong style='color:green;'>Dark Sky Certified</strong>"
                    if (row['DarkSkyQualified'] == 'YES') and (row['DarkSkyCertified'] == 'NO'):
                        markdown_text += " - <strong style='color:orange;'>Dark Sky Qualified</strong>"
                        
                    add_text = """
                        <br>{x_bright:.2f}-times brighter than the darkest Night Sky (Hart Mountain)
                        <br>Bortle Scale (1: Excellent dark sky - 9:  Inner-city sky): {bortle}
                        <br>Median Night Sky Brightness (log scale): {mag_arcsec2:.2f} mag/arcsec²
                        <br>Flux Ratio (Night Sky Brightness converted to a linear scale): = {flux_ratio:.2f}
                          """.format(
                              x_bright=row['x_brighter_than_darkest_night_sky'],
                              mag_arcsec2=row['median_brightness_mag_arcsec2'],
                              bortle=row['bortle_sky_level'],
                              flux_ratio=row['median_linear_scale_flux_ratio']
                              )
                elif meas_type == "cloudy_nights_brightness":
                    add_text = """
                        <br>{x_bright:.2f}-times brighter than the darkest Night Sky (Crater Lake)
                        <br>Median Night Sky Brightness (log scale): {mag_arcsec2:.2f} mag/arcsec²
                        <br>Flux Ratio (Night Sky Brightness converted to a linear scale): = {flux_ratio:.2f}
                          """.format(
                              x_bright=row['x_brighter_than_darkest_night_sky'],
                              mag_arcsec2=row['median_brightness_mag_arcsec2'],
                              flux_ratio=row['median_linear_scale_flux_ratio']
                              )
                elif meas_type == "long_term_trends":
                    add_text = """
                        <br>Rate of Change in Night Sky Brightness vs Prineville Reservoir State Park - a certified Dark Sky Park: {rate_of_change:.4f}
                        <br>Trendline Slope (regression fit of change over time scaled by a factor of 10000): {regression_slope_x10000:.2f}
                        <br>Percentage Change in Night Sky Brightness per year: {percent_change:.2f}%
                        <br>Number of Years of Data: {num_years}
                        """.format(
                            rate_of_change=row['Rate_of_Change_vs_Prineville_Reservoir_State_Park'],
                            percent_change=row['Percent_Change_per_year'],
                            regression_slope_x10000=row['Regression_Line_Slope_x_10000'],
                            num_years=row['Number_of_Years_of_Data'],
                        )
                elif meas_type == "milky_way_visibility":
                    add_text = """
                        <br>Ratio Index (ratio of brightness of Milky Way to the surrounding sky): {ratio_index:.2f}
                        <br>Difference Index (difference in brightness between Milky Way and surrounding sky): {difference_index:.2f}
                        """.format(
                            ratio_index=row['ratio_index'],
                            difference_index=row['difference_index_mag_arcsec2']
                        )
                elif meas_type == "% clear nights":
                    add_text = """
                        <br>Percentage of Clear (no clouds) nights averaged over all months in the year: {clear_nights:.2f}%
                        """.format(
                            clear_nights=row['percent_clear_night_samples_all_months']
                        )
                else:
                    add_text = """"""
                    
                markdown_text += add_text + "<br>Site Elevation: {elevation:.0f} meters</p>".format(
                    elevation=row['Elevation_in_meters']
                )

                st.markdown(markdown_text, unsafe_allow_html=True)

        

    # display ranking chart in the left column
    with col_middle:
        # adding header for the ranking chart
        st.markdown(
            f"<h3 style='font-size: 20px;'> {meas_type_configs['bar_chart_title']}</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            "Hover over bars to see {0}. Use the buttons on the top-right of the chart to zoom, pan, reset or save chart as an image".format(
                meas_type_configs['bar_chart_text']
            )
        )
        #print("clicked_sites before ranking chart:", st.session_state["clicked_sites"])
        # creating ranking chart based on the selected measurement type
        fig_bar = create_ranking_chart(
            sites_df=final_data_df,
            y_col=meas_type_configs['bar_chart_y_col'],
            y_label=meas_type_configs['bar_chart_y_label'],
            clicked_sites=st.session_state["clicked_sites"],
        )

        # plotting the ranking chart via plotly
        st.plotly_chart(fig_bar, use_container_width=True, config = {"displayModeBar": True})

    # Scatter plot directly below the map
    with col_right:
        if meas_type != "% clear nights":
            # Add subheader for scatter plot
            st.markdown(
                f"<h3 style='font-size: 20px;'>{meas_type_configs['scatter_plot_title']}</h3>",
                unsafe_allow_html=True
            )
            st.markdown(
                "Hover over data-points to see the values. Use the buttons just like the ranking chart."
            )
            # creating interactive 2d scatter plot based on the selected measurement type
            fig_scatter = create_interactive_2d_plot(
                df=final_data_df,
                x_col=meas_type_configs['scatter_x_col'],
                y_col=meas_type_configs['scatter_y_col'],
                x_label=meas_type_configs['scatter_x_label'],
                y_label=meas_type_configs['scatter_y_label'],
                vline=meas_type_configs['vline'],
                clicked_sites=st.session_state["clicked_sites"]
            )
            st.plotly_chart(fig_scatter, use_container_width=False, config = {"displayModeBar": True})
    

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