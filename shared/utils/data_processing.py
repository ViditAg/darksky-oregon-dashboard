# shared/utils/data_processing.py
"""
Core data processing utilities for Oregon SQM Network data
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging


# Create a module-level logger and add a handler only if none exist (prevents duplicate logs in Jupyter)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.propagate = False  # Prevent log messages from being propagated to the root logger (avoids duplicate output in Jupyter)


class OregonSQMProcessor:
    """
    Process Oregon SQM Network data for dashboard consumption.
    """

    def __init__(
        self,
        data_dir: str = "shared/data"
    ):
        """
        Initialize processor with data directory paths.

        Parameters
        ----------
        data_dir : str, optional
            Path to the data directory. Defaults to "shared/data".
        """
        # Log the initialization
        logger.info(f"Initializing OregonSQMProcessor with data directory: {data_dir}")
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
        """Return mapping of dataset names to CSV file names."""
        return {
            'sites': 'sites_locations.csv',
            'geocode': 'sites_coordinates.csv',
            'clear_measurements': 'clear_night_measurements.csv',
            'cloudy_measurements': 'cloudy_night_measurements.csv',
            'trends': 'longterm_trends.csv',
            'milky_way': 'milky_way_visibility.csv',
            'cloud_coverage': 'cloud_coverage.csv'
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
            logger.info(f"Loaded {key}: {len(data[key])} records")
        else:
            # If the file doesn't exist, create an empty DataFrame
            data[key] = pd.DataFrame()
            logger.warning(f"File not found: {file_path}")

def main():
    """Main processing pipeline"""
    processor = OregonSQMProcessor()
    
    # Load raw data
    raw_data = processor.load_raw_data()

    print("Data processing complete!")

if __name__ == "__main__":
    main()