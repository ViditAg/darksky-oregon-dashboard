"""
Defining configuration utilities for measurement types:
- Centralize configuration settings for different night sky measurement types.
- Provide mapping and descriptive metadata for use in data processing and visualization.
- Supply utility functions to retrieve configuration details for each measurement type.
"""

# Configuration dictionary for scatter plot (common across some measurement types)
scatter_plot_configs = {
    "scatter_plot_title": "Ranking metric vs Median Night Sky Brightness",
    "scatter_x_col": "median_brightness_mag_arcsec2",
    "scatter_y_col": "x_brighter_than_darkest_night_sky",
    "scatter_x_label": "Median Night Sky Brightness <br> (mag/arcsec²)",
    "scatter_y_label": "X-times brighter",
}

# Configuration dictionary for different measurement types
meas_type_dict = {
    "clear_nights_brightness": {
        "data_key": "clear_measurements",
        "Question_text": "Clear Nights – where is the Night Sky most and least light polluted?",
        "map_text": "Clear Nights - Light Pollution?",
        "bar_chart": {
            "bar_chart_title": "Clear Nights - Ranking sites by how much brighter they are compared to our darkest night sky measurement site",
            "bar_chart_y_col": "x_brighter_than_darkest_night_sky",
            "bar_chart_y_label": "<--- Darker -------------------------------- Brighter --->",
            "bar_chart_yicks": {
                "tickmode": "log",
                "tickvals": [1, 2, 10, 20],  # your actual data values
                "ticktext": ["1", "2", "10", "20"] # your actual tick labels
            }
        },
        "scatter_plot": scatter_plot_configs
    },
    "cloudy_nights_brightness": {
        "data_key": "cloudy_measurements",
        "Question_text": "Cloudy Nights – where is the Night Sky most and least light polluted?",
        "map_text": "Cloudy Nights - Light Pollution?",
        "bar_chart": {
            "bar_chart_title": "Cloudy Nights - Ranking sites by how much brighter they are compared to our darkest night sky measurement site",
            "bar_chart_y_col": "x_brighter_than_darkest_night_sky",
            "bar_chart_y_label": "<--- Darker -------------------------------- Brighter --->",
            "bar_chart_yicks": {
                "tickmode": "log",
                "tickvals": [1, 10, 100, 1000],  # your actual data values
                "ticktext": ["1", "10", "100", "1000"] # your actual tick labels
            }
        },
        "scatter_plot": scatter_plot_configs
    },
    "long_term_trends": {
        "data_key": "trends",
        "Question_text": "Starry night skies – where are they disappearing or recovering?",
        "map_text": "Starry Nights - Disappearing?",
        "bar_chart": {
            "bar_chart_title": "Ranking sites by the rate of change in night sky brightness compared to a certified Dark Sky Park",
            "bar_chart_y_col": "Rate_of_Change_vs_Prineville_Reservoir_State_Park",
            "bar_chart_y_label": "<--- Slower ------------------- Faster --->",
            "bar_chart_yicks": {
                "tickmode": "linear",
                 "tickvals": [0, 50, 100, 150],  # your actual data values
                 "ticktext": ["0", "50", "100", "150"] # your actual tick labels
            }
        },
        "scatter_plot": None  
    },
    "milky_way_visibility": {
        "data_key": "milky_way",
        "Question_text": "Milky Way – where does it stand out best?",
        "map_text": "Milky Way Visibility?",
        "bar_chart": {
            "bar_chart_title": "Milky Way – Ranking sites by how well it stands out in the clear night sky.",
            "bar_chart_y_col": "ratio_index",
            "bar_chart_y_label": "<--- Not visible --------------------------- Clearly visible --->",
            "bar_chart_yicks": {
                "tickmode": "log",
                "tickvals": [1, 1.2, 1.4, 1.6],  # your actual data values
                "ticktext": ["1", "1.2", "1.4", "1.6"] # your actual tick labels
            }
        },
        "scatter_plot": None
    },
    "% clear nights": {
        "data_key": "cloud_coverage",
        "Question_text": "Cloudiness – where are the night skies most and least cloudy?",
        "map_text": "Cloudiness?",
        "bar_chart": {
            "bar_chart_title": "Cloudiness – Ranking sites by the percentage of clear, not cloudy, nighttime measurements.",
            "bar_chart_y_col": "percent_clear_night_samples_all_months",
            "bar_chart_y_label": "<--- Cloudiest -------------------------------- Clearest --->",
            "bar_chart_yicks": {
                "tickmode": "linear",
                "tickvals": [0, 20, 40, 60, 80, 100],  # your actual data values
                "ticktext": ["0%", "20%", "40%", "60%", "80%", "100%"] # your actual tick labels
            }
        },
        "scatter_plot": None
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
        dict of str : dict: Configuration settings for the specified measurement type.
    """
    # Validate measurement type
    if meas_type not in meas_type_dict:
        raise ValueError(f"Invalid measurement type: {meas_type}")
    # Map to table name
    
    return meas_type_dict[meas_type]