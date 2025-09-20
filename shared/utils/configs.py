"""
Defining configuration utilities for measurement types:
- Centralize configuration settings for different night sky measurement types.
- Provide mapping and descriptive metadata for use in data processing and visualization.
- Supply utility functions to retrieve configuration details for each measurement type.
"""
# Configuration dictionary for different measurement types
meas_type_dict = {
    "clear_nights_brightness": {
        "data_key": "clear_measurements",
        "Question_text": "Where in Oregon is the Night Sky most pristine and, most light polluted during Clear nights?",
        "bar_chart_title": "Ranking sites by how brighter they are compared to the darkest night sky (Hart Mountain)",
        "bar_chart_text" : "by how many times the night sky at that site is brighter than at Hart Mountain",
        "bar_chart_y_col": "x_brighter_than_darkest_night_sky",
        "bar_chart_y_label": "<--- Darker -------------------------------- Brighter --->",
        "scatter_plot_title": "Ranking metric vs Median Night Sky Brightness",
        "scatter_x_col": "median_brightness_mag_arcsec2",
        "scatter_y_col": "x_brighter_than_darkest_night_sky",
        "scatter_x_label": "Median Night Sky Brightness <br> (mag/arcsec²)",
        "scatter_y_label": "X-times brighter",
        "vline": 21.2
    },
    "cloudy_nights_brightness": {
        "data_key": "cloudy_measurements",
        "Question_text": "Where in Oregon is the Night Sky most pristine and, most light polluted during Cloudy nights?",
        "bar_chart_title": "Ranking sites by how brighter they are compared to the darkest night sky (Crater Lake)",
        "bar_chart_text" : "by how many times the night sky at that site is brighter than at Crater Lake",
        "bar_chart_y_col": "x_brighter_than_darkest_night_sky",
        "bar_chart_y_label": "<--- Darker -------------------------------- Brighter --->",
        "scatter_plot_title": "Ranking metric vs Median Night Sky Brightness",
        "scatter_x_col": "median_brightness_mag_arcsec2",
        "scatter_y_col": "x_brighter_than_darkest_night_sky",
        "scatter_x_label": "Median Night Sky Brightness <br> (mag/arcsec²)",
        "scatter_y_label": "X-times brighter",
        "vline": None
        },
    "long_term_trends": {
        "data_key": "trends",
        "Question_text": "Where are the starry night skies disappearing the fastest in Oregon?",
        "bar_chart_title": "Ranking sites by the rate of change in night sky brightness compared to Prineville Reservoir State Park - a certified Dark Sky Park",
        "bar_chart_text" : "relative rate of change in night sky brightness at that site",
        "bar_chart_y_col": "Rate_of_Change_vs_Prineville_Reservoir_State_Park",
        "bar_chart_y_label": "<--- Slower ------------------- Faster --->",
        "scatter_plot_title": "Night Sky Brightness: Rate of change vs % Change per year",
        "scatter_x_col": "Percent_Change_per_year",
        "scatter_y_col": "Rate_of_Change_vs_Prineville_Reservoir_State_Park",
        "scatter_x_label": "Percentage change <br> (per year)",
        "scatter_y_label": "Rate of change vs. a Dark Sky Park",
        "vline": None
    },
    "milky_way_visibility": {
        "data_key": "milky_way",
        "Question_text": "Where does the Milky Way stand out best in Oregon?",
        "bar_chart_title": "Ranking sites by how much Milky Way is brighter the than surrounding night sky",
        "bar_chart_text" : " that site's Ratio Index, which is a unitless ratio of linear flux data from Milky Way compared to the surrounding sky",
        "bar_chart_y_col": "ratio_index",
        "bar_chart_y_label": "<--- Not visible --------------------------- Clearly visible --->",
        "scatter_plot_title": "Ratio Index vs. Difference Index (both give similar information about Milky Way visibility)",
        "scatter_x_col": "difference_index_mag_arcsec2",
        "scatter_y_col": "ratio_index",
        "scatter_x_label": "Difference Index <br> (mag/arcsec²)",
        "scatter_y_label": "Ratio Index",
        "vline": None
    },
    "% clear nights": {
        "data_key": "cloud_coverage",
        "Question_text": "Where in Oregon are the clearest – least cloudy – night skies?",
        "bar_chart_title": "Ranking sites by percentage of clear nights",
        "bar_chart_text" : "the percentage of nights that are clear (not cloudy) at that site averaged over all months in the year",
        "bar_chart_y_col": "percent_clear_night_samples_all_months",
        "bar_chart_y_label": "<--- Cloudiest -------------------------------- Clearest --->",
        "scatter_plot_title": "",
        "scatter_x_col": "",
        "scatter_y_col": "",
        "scatter_x_label": "",
        "scatter_y_label": "",
        "vline": None
    },
}

# Function to get configuration values for a given measurement type
def get_meas_type_config(meas_type: str) -> dict:
    """
    Build configuration values for a given measurement type.
    It leverages the meas_type_dict to extract relevant settings.
    Parameters:
    - meas_type (str): The measurement type key.
    Returns:
        dict of str : 
    """
    # Validate measurement type
    if meas_type not in meas_type_dict:
        raise ValueError(f"Invalid measurement type: {meas_type}")
    # Map to table name
    
    return meas_type_dict[meas_type]