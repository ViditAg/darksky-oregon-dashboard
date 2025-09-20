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
            'sites': 'sites_locations.csv',
            'geocode': 'sites_coordinates.csv',
            'clear_measurements': 'clear_night_measurements.csv',
            'cloudy_measurements': 'cloudy_night_measurements.csv',
            'trends': 'longterm_trends.csv',
            'milky_way': 'milky_way_visibility.csv',
            'cloud_coverage': 'cloud_coverage.csv',
            'colormap': 'color_map_for_SQM_readings.csv'
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


    def load_processed_data(
        self,
        data_key: str,
        bar_chart_col: str = None
    ):
        """
        Load and process data for a specific measurement type.
        - merges measurement data with geocode information.
        - assigns DarkSkyQualified status.
        - assigns DarkSkyCertified status.
        """
        ## Load all raw data from CSVs using the processor
        raw_dfs = self.load_raw_data()
        ## data-frame containing results to show on dash-board
        data_df = raw_dfs[data_key]
        ## Load geocode CSV and merge with selected data
        geocode_df = raw_dfs['geocode'].copy()
        # Merge geocode data with main data
        final_data_df = pd.merge(data_df, geocode_df, on="site_name", how="left")

        if bar_chart_col == 'x_brighter_than_darkest_night_sky':
            value_col = 'median_brightness_mag_arcsec2'
        else:
            value_col = bar_chart_col

        final_data_df = self._add_color_map_column(
            df=final_data_df,
            colormap_df=raw_dfs['colormap'],
            value_col=value_col
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
            final_data_df['DarkSkyQualified'] = 'NO'
            final_data_df.loc[final_data_df['median_brightness_mag_arcsec2'] > 21.2, 'DarkSkyQualified'] = 'YES'
        
        return final_data_df
    
    def _add_color_map_column(
        self,
        df: pd.DataFrame,
        colormap_df: pd.DataFrame,
        value_col: str,
        color_col: str = 'color_rgba'
    ) -> pd.DataFrame:
        """
        Add a color map column to the DataFrame based on value ranges.
        """
        df_with_colors = df.copy()
        df_val_max = df[value_col].max()
        df_val_min = df[value_col].min()
        for i, row in df.iterrows():
            value = row[value_col]
            if value_col == 'median_brightness_mag_arcsec2':
                site_color_bin = colormap_df[
                    (colormap_df['brightness_mag_arcsec2'] > value)
                    ]['brightness_mag_arcsec2'].min()
                color = colormap_df[
                colormap_df['brightness_mag_arcsec2'] == site_color_bin
                ].apply(lambda x: f"rgba({x['red']}, {x['green']}, {x['blue']}, 1)", axis=1).values[0]
            elif value_col == 'Rate_of_Change_vs_Prineville_Reservoir_State_Park':
                color = 'rgba({0}, {1}, {0}, 1)'.format(
                    int(255 * (value - df_val_min) / (df_val_max - df_val_min)),
                    255 - int(255 * (value - df_val_min) / (df_val_max - df_val_min))
                )
            else:
                color = 'rgba({0}, 0, {0}, 1)'.format(
                    int(255 * (value - df_val_min) / (df_val_max - df_val_min))
                )

            df_with_colors.at[i, color_col] = color
        
        return df_with_colors