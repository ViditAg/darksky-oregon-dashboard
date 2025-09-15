# function to get measurement type configurations

meas_type_dict = {
    "clear_nights_brightness": {
        "raw_df_key": "clear_measurements",
        "Question_text": "Where in Oregon is the Night Sky Most Pristine? And, Most Light Polluted? **(Clear nights)**",
        "Main_col_name": "x_brighter_than_darkest_night_sky"
        },
    "cloudy_nights_brightness": {
        "raw_df_key": "cloudy_measurements",
        "Question_text": "Where in Oregon is the Night Sky Most Pristine? And, Most Light Polluted? **(Cloudy nights)**",
        "Main_col_name": "x_brighter_than_darkest_night_sky"
        },
    "long_term_trends": {
        "raw_df_key": "trends",
        "Question_text": "Where are the starry night skies disappearing the fastest in Oregon?",
        "Main_col_name": "Rate_of_Change_vs_Prineville_Reservoir_State_Park"
    },
    "milky_way_visibility": {
        "raw_df_key": "milky_way",
        "Question_text": "Where does the Milky Way stand out best in Oregon?",
        "Main_col_name": "ratio_index"
    },
    "% clear nights": {
        "raw_df_key": "cloud_coverage",
        "Question_text": "Where in Oregon are the clearest – least cloudy – night skies?",
        "Main_col_name": "percent_clear_night_samples_all_months"
    }
}

def get_meas_type_config(meas_type: str) -> dict:
    """
    Build configuration values for a given measurement type.

    Returns a dictionary containing:
        meas_type_table, bar_metric, scatter_x, scatter_y,
        legend_str, legend_order, vline
    """
    # Measurement type selection (for future extensibility)
    ## Question text for each measurement type
    ## Main column for map visualization
    ## Y-axis column for bar and scatter plots
    
    
    # Column names for y-axis in plots
    y_col_print_dict = {
        "ratio_index": "Ratio of linear scale SQM flux data",
        "x_brighter_than_darkest_night_sky": "Night sky brightness relative compared to the darkest site",
        "percent_clear_night_samples_all_months": "% Clear Nights over all months",
        "Rate_of_Change_vs_Prineville_Reservoir_State_Park": "Rate of Change vs. Prineville Reservoir State Park",
        "Percent_Change_per_year": "Percent Change per year",
        "median_brightness_mag_arcsec2": "Median Brightness (mag/arcsec²)",
        "difference_index_mag_arcsec2": "Difference Index (mag/arcsec²)"
    }

    # Map to table name
    meas_selection = meas_type_dict[meas_type]
    raw_df_key = meas_selection['raw_df_key']
    main_col_ = meas_selection['Main_col_name']
    y_col_print = y_col_print_dict[main_col_]
    
    # Legend string
    if meas_type in ["clear_nights_brightness", "cloudy_nights_brightness"]:
        legend_str = "**Skyglow level**: 🟥 Worst  🟨 Medium  🟩 Pristine"
    elif meas_type == "milky_way_visibility":
        legend_str = "**Milky Way visibility**: 🟥 Worst  🟨 Medium  🟩 Best"
    elif meas_type == "% clear nights":
        legend_str = "**Clear nights**: 🟥 Least  🟨 Medium  🟩 Highest"
    elif meas_type == "long_term_trends":
        legend_str = "**Disappearing starry night skies**: 🟥 Fastest  🟨 Medium  🟩 Slowest"
    else:
        legend_str = ""

    # Legend order
    if meas_type in ["clear_nights_brightness", "cloudy_nights_brightness", "long_term_trends"]:
        legend_order = ["Green", "Yellow", "Red"]
    else:
        legend_order = ["Red", "Yellow", "Green"]
   
    # Metrics and scatter axes
    if meas_type == "% clear nights":
        bar_metric = "percent_clear_night_samples_all_months"
        scatter_x = ""
        scatter_y = ""
    elif meas_type == "milky_way_visibility":
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
    
    scatter_title = ""
    if meas_type != "% clear nights":
        scatter_title = f"{y_col_print_dict[scatter_x]} vs. {y_col_print_dict[scatter_y]}"

    # Vertical reference line
    if meas_type in ["clear_nights_brightness", "cloudy_nights_brightness"]:
        vline = 21.2
    else:
        vline = None

    return {
        "main_col_": main_col_,
        "raw_df_key": raw_df_key,
        "legend_str": legend_str,
        "legend_order": legend_order,
        "bar_metric": bar_metric,
        "y_col_print": y_col_print,
        "scatter_x": scatter_x,
        "scatter_y": scatter_y,
        "scatter_title": scatter_title,
        "vline": vline,
    }