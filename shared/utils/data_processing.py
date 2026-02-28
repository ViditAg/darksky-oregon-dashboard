"""
Core data processing utilities for Oregon SQM Network data.
- Load and preprocess raw data files.
"""

# import standard libraries
from platform import processor
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict


class OregonSQMProcessor:
    """
    Process Oregon SQM Network data for dashboard consumption.
    This class handles loading, cleaning, and transforming raw data files.
    Parameters
    ----------
    data_dir : str
        Path to the data directory containing raw and processed data. Defaults to "shared/data".
    """

    def __init__(
        self,
        data_dir: str = "shared/data"
    ):
        """
        Initialize processor with data directory paths.
        """
        # Set up data directory paths
        self.data_dir = Path(data_dir)
        # Define raw and processed data directories
        self.raw_dir = self.data_dir / "raw"

    
    def load_raw_data(
        self
    ) -> Dict[str, pd.DataFrame]:
        """
        Load all raw CSV files into DataFrames.

        Returns
        -------
        Dict[str, pd.DataFrame]
            Dictionary of DataFrames keyed by dataset name.
        """
        # Initialize a dictionary to hold the data
        data = {}
        # Get mapping of dataset names to CSV file paths
        csv_files = self._get_csv_file_map()
        # Load each CSV file into a DataFrame
        for key, filename in csv_files.items():
            self._load_single_csv(data, key, filename)
        
        return data

    
    def _get_csv_file_map(self) -> Dict[str, str]:
        """
        Return mapping of dataset names to CSV file names.
        """
        return {
            'sites': 'sites_locations_install_sequence_2026.csv',
            'geocode': 'sites_coordinates_2026.csv',
            'clear_measurements': 'clear_night_measurements_2026.csv',
            'cloudy_measurements': 'cloudy_night_measurements_2026.csv',
            'trends': 'longterm_trends_2026.csv',
            'milky_way': 'milky_way_visibility_2026.csv',
            'cloud_coverage': 'cloud_coverage_2026.csv',
            'colormap_clear': 'color_map_for_SQM_readings_clear_nights.csv',
            'colormap_cloudy': 'color_map_for_SQM_readings_cloudy_nights.csv',
            'colormap_trends': 'color_map_for_long_term_trends.csv',
            'colormap_milky_way': 'color_map_for_milky_way_visibility.csv',
            'colormap_cloud_coverage': 'color_map_for_cloud_coverage.csv',
        }

    
    def _load_single_csv(
        self,
        data: dict,
        key: str,
        filename: str
    ):
        """
        Load a single CSV file into the data dictionary, with logging.

        Parameters
        ----------
        data : dict
            Dictionary to store loaded DataFrames.
        key : str
            Key for the dataset.
        filename : str
            CSV file name.
        """
        file_path = self.raw_dir / filename
        if file_path.exists():
            # Load the CSV file into a DataFrame
            data[key] = pd.read_csv(file_path)
        else:
            # If the file doesn't exist, create an empty DataFrame
            data[key] = pd.DataFrame()


    def _add_color_map_column(
        self,
        df: pd.DataFrame,
        colormap_df: pd.DataFrame,
        value_col: str,
        colormap_bin_col: str = 'brightness_mag_arcsec2',
        color_col: str = 'color_rgba'
    ) -> pd.DataFrame:
        """
        Add a color map column to the DataFrame based on value ranges.
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to which the color column will be added.
        colormap_df : pd.DataFrame
            DataFrame containing color mapping information.
        value_col : str
            Column in df whose values will determine the color mapping.
        colormap_bin_col : str, optional
            Column in colormap_df that contains the bin boundaries, by default 'brightness_mag_arcsec2'.
        color_col : str, optional
            Name of the new color column to be added, by default 'color_rgba'.
        Returns
        -------
        pd.DataFrame
            DataFrame with the new color column added.
        """
        # Create a copy of the DataFrame to avoid modifying the original
        df_with_colors = df.copy()

        # iterate over rows and assign colors based on value ranges 
        for i, row in df.iterrows():
            # get the value for the current row
            value = row[value_col]

            # find the nearest colormap bin above the current value (ceiling lookup)
            above_bins = colormap_df[colormap_df[colormap_bin_col] > value][colormap_bin_col]
            if above_bins.empty:
                # value is at or above the max bin — use the last color
                site_color_bin = colormap_df[colormap_bin_col].max()
            else:
                site_color_bin = above_bins.min()

            # get the corresponding RGBA color from the colormap
            color = colormap_df[
                colormap_df[colormap_bin_col] == site_color_bin
            ].apply(
                lambda x: f"rgba({x['red']}, {x['green']}, {x['blue']}, 1)", axis=1
            ).values[0]

            # assign the color to the new column
            df_with_colors.at[i, color_col] = color
        
        return df_with_colors
    
    
    def load_processed_data(
        self,
        data_key: str,
        bar_chart_col: str
    ):
        """
        Load and process data for a specific measurement type.
        - merges measurement data with geocode information.
        - assigns DarkSkyQualified status.
        - assigns DarkSkyCertified status.
        Parameters
        ----------
        data_key : str
            Key for the measurement type (e.g., 'clear_measurements').
        bar_chart_col : str
            Column used for bar chart ranking
        Returns
        -------
        pd.DataFrame
            Processed DataFrame ready for dashboard visualization.
        """
        ## Load all raw data from CSVs using the processor
        raw_dfs = self.load_raw_data()
        ## data-frame containing results to show on dash-board
        data_df = raw_dfs[data_key]
        ## Load geocode CSV and merge with selected data
        geocode_df = raw_dfs['geocode'].copy()
        # Merge geocode data with main data
        final_data_df = pd.merge(data_df, geocode_df, on="site_name", how="left")
        
        # Determine the value column for color mapping
        if bar_chart_col == 'x_brighter_than_darkest_night_sky':
            value_col = 'median_brightness_mag_arcsec2'
        else:
            value_col = bar_chart_col

        # Select the colormap and its bin column based on measurement type
        colormap_config = {
            'clear_measurements':  ('colormap_clear',        'brightness_mag_arcsec2'),
            'cloudy_measurements': ('colormap_cloudy',       'brightness_mag_arcsec2'),
            'trends':              ('colormap_trends',       'Rate_of_Change_vs_Prineville_Reservoir_State_Park'),
            'milky_way':           ('colormap_milky_way',    'ratio_index'),
            'cloud_coverage':      ('colormap_cloud_coverage', 'percent_clear_night_samples_all_months'),
        }
        colormap_key, colormap_bin_col = colormap_config.get(
            data_key, ('colormap_cloudy', 'brightness_mag_arcsec2')
        )

        # Add color mapping column
        final_data_df = self._add_color_map_column(
            df=final_data_df,
            colormap_df=raw_dfs[colormap_key],
            value_col=value_col,
            colormap_bin_col=colormap_bin_col,
        )
        
        # Assign DarkSkyQualified status
        if data_key == 'clear_measurements':
            # Assign DarkSkyCertified status
            DSC_SITES = [
                'Hart Mountain',
                'Sisters East',
                'Sisters High School',
                'Oregon Observatory Sunriver',
                'Prineville Reservoir State Park',
                'Oregon Caves National Monument',
                'Antelope',
                'Cottonwood Canyon State Park'
            ]
            final_data_df['DarkSkyCertified'] = 'NO'
            final_data_df.loc[
                final_data_df['site_name'].isin(DSC_SITES), 'DarkSkyCertified'
            ] = 'YES'
            # Assign DarkSkyQualified status based on median brightness
            final_data_df['DarkSkyQualified'] = 'NO'
            final_data_df.loc[
                final_data_df['median_brightness_mag_arcsec2'] > 21.2, 'DarkSkyQualified'
            ] = 'YES'
        
        return final_data_df
    
    
    