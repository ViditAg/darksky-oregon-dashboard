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
            'colormap_clear': 'color_map_for_SQM_readings_clear_nights.csv',
            'colormap_cloudy': 'color_map_for_SQM_readings_cloudy_nights.csv',
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
        color_col : str, optional
            Name of the new color column to be added, by default 'color_rgba'.
        Returns
        -------
        pd.DataFrame
            DataFrame with the new color column added.
        """
        # Create a copy of the DataFrame to avoid modifying the original
        df_with_colors = df.copy()

        # get min and max values for normalization
        df_val_max = df[value_col].max()
        df_val_min = df[value_col].min()
        
        # iterate over rows and assign colors based on value ranges 
        for i, row in df.iterrows():
            # get the value for the current row
            value = row[value_col]

            # determine the color scheme based on the column being processed
            if value_col == 'median_brightness_mag_arcsec2':
                # find the closest color bin in the colormap
                site_color_bin = colormap_df[
                    (colormap_df['brightness_mag_arcsec2'] > value)
                    ]['brightness_mag_arcsec2'].min()
                # get the corresponding RGBA color
                color = colormap_df[
                    (colormap_df['brightness_mag_arcsec2'] == site_color_bin)
                ].apply(
                    lambda x: f"rgba({x['red']}, {x['green']}, {x['blue']}, 1)", axis=1
                    ).values[0]
            
            elif value_col == 'Rate_of_Change_vs_Prineville_Reservoir_State_Park':
                # Use a red-green gradient for rate of change
                color = 'rgba({0}, {1}, {0}, 1)'.format(
                    int(255 * (value - df_val_min) / (df_val_max - df_val_min)),
                    255 - int(255 * (value - df_val_min) / (df_val_max - df_val_min))
                )
            
            else:
                # Use a blue gradient for other values
                color = 'rgba({0}, 0, {0}, 1)'.format(
                    int(255 * (value - df_val_min) / (df_val_max - df_val_min))
                )

            # assign the color to the new column
            df_with_colors.at[i, color_col] = color
        
        return df_with_colors
    
    
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
        Parameters
        ----------
        data_key : str
            Key for the measurement type (e.g., 'clear_measurements').
        bar_chart_col : str, optional
            Column used for bar chart ranking, by default None.
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
        
        # Add color mapping table based on measurement type
        if data_key == 'clear_measurements':
            colormap_key = 'colormap_clear'
        else:
            colormap_key = 'colormap_cloudy'

        # Determine the value column for color mapping
        if bar_chart_col == 'x_brighter_than_darkest_night_sky':
            value_col = 'median_brightness_mag_arcsec2'
        else:
            value_col = bar_chart_col

        # Add color mapping column
        final_data_df = self._add_color_map_column(
            df=final_data_df,
            colormap_df=raw_dfs[colormap_key],
            value_col=value_col,
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
    
    
    