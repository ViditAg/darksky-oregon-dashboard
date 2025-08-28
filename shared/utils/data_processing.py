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

# configure the logging system to display messages at the INFO level or higher (INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)
# create a logger object named after the current module to write log messages throughout the code
logger = logging.getLogger(__name__)

class OregonSQMProcessor:
    """Process Oregon SQM Network data for dashboard consumption"""
    
    def __init__(
            self,
            data_dir: str = "shared/data"
        ):
        """
        Initialize processor with data directory paths

        Parameters:
            data_dir (str, optional): Path to the data directory. Defaults to "shared/data".
        """
        
        # Log the initialization
        logger.info(f"Initializing OregonSQMProcessor with data directory: {data_dir}")
        
        # Set up data directory paths
        self.data_dir = Path(data_dir)
        
        # Define raw and processed data directories
        self.raw_dir = self.data_dir / "raw"
        # Define processed data directory
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_raw_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all raw CSV files into DataFrames

        Returns:
            data (Dict[str, pd.DataFrame]): Dictionary of DataFrames keyed by dataset name
        """
        # Initialize a dictionary to hold the data
        data = {}

        # Map dataset names to their CSV file paths
        csv_files = {
            'sites': 'sites_locations.csv',
            'clear_measurements': 'clear_night_measurements.csv',
            # 'cloudy_measurements': 'cloudy_night_measurements.csv', 
            # 'trends': 'longterm_trends.csv',
            # 'milky_way': 'milky_way_visibility.csv',
            # 'cloud_coverage': 'cloud_coverage_monthly.csv'
        }

        # Load each CSV file into a DataFrame
        for key, filename in csv_files.items():
            # Construct the file path to the CSV file
            file_path = self.raw_dir / filename
            # Check if the file exists
            if file_path.exists():
                # Load the CSV file into a DataFrame
                data[key] = pd.read_csv(file_path)
                # Log the number of records loaded
                logger.info(f"Loaded {key}: {len(data[key])} records")
            else:
                # If the file doesn't exist, create an empty DataFrame
                data[key] = pd.DataFrame()
                # Log a warning
                logger.warning(f"File not found: {file_path}")

        # Return the loaded data dictionary
        return data
    
    def validate_data(
            self,
            data: Dict[str, pd.DataFrame]
        ) -> Dict[str, bool]:
        """
        Validate data quality and completeness
        Parameters:
            data (Dict[str, pd.DataFrame]): The dataset to validate

        Returns:
            Dict[str, bool]: Validation results for each dataset
        """
        # Initialize validation results
        validation_results = {}
        
        # Check sites data
        # Sites data should have at least 60 records and contain latitude/longitude
        sites_df = data.get('site_name', pd.DataFrame())
        validation_results['sites_complete'] = len(sites_df) >= 60  # Expect ~65 sites
        # sites have coordinates defined
        validation_results['sites_have_coords'] = 'latitude' in sites_df.columns and 'longitude' in sites_df.columns
        
        # Check measurements data
        clear_df = data.get('clear_measurements', pd.DataFrame())
        # Clear measurements should have at least 30 records
        validation_results['clear_measurements_exist'] = len(clear_df) > 30
        # Clear measurements should have brightness values in the expected range
        validation_results['brightness_in_range'] = (
            clear_df['median_brightness_mag_arcsec2'].between(17, 22).all() 
            if 'median_brightness_mag_arcsec2' in clear_df.columns else False
        )
        
        # Log validation results
        for check, passed in validation_results.items():
            status = "PASS" if passed else "FAIL"
            logger.info(f"{check}: {status}")
        
        return validation_results
    
    def merge_site_data(
            self,
            data: Dict[str, pd.DataFrame]
        ) -> pd.DataFrame:
        """
        Merge all site-related data into master dataset

        Parameters:
            data (Dict[str, pd.DataFrame]): The dataset to merge

        Returns:
            pd.DataFrame: The merged master dataset
        """
        # Start with sites data
        sites_df = data['sites'].copy()
        
        # Merge measurement data
        if not data['clear_measurements'].empty:
            sites_df = sites_df.merge(
                data['clear_measurements'], 
                on='site_name', 
                how='left',
                suffixes=('', '_clear')
            )
        
        if not data['cloudy_measurements'].empty:
            sites_df = sites_df.merge(
                data['cloudy_measurements'],
                on='site_name', 
                how='left',
                suffixes=('', '_cloudy')  
            )
        
        # Add trend data
        if not data['trends'].empty:
            sites_df = sites_df.merge(
                data['trends'],
                on='site_name',
                how='left'
            )
        
        # Add Milky Way visibility
        if not data['milky_way'].empty:
            sites_df = sites_df.merge(
                data['milky_way'],
                on='site_name', 
                how='left'
            )
        
        return sites_df
    
    def save_processed_data(
            self,
            sites_df: pd.DataFrame,
            data: Dict[str, pd.DataFrame]
        ):
        """
        Save processed data in multiple formats

        Parameters:
            sites_df (pd.DataFrame): The master sites dataset
            data (Dict[str, pd.DataFrame]): The individual datasets to save
        """
        
        # Save master sites dataset  
        sites_df.to_json(
            self.processed_dir / 'sites_master.json',
            orient='records', 
            indent=2
        )
        # Save master sites dataset as CSV
        sites_df.to_csv(
            self.processed_dir / 'sites_master.csv',
            index=False
        )
        
        # Save individual datasets
        for name, df in data.items():
            if not df.empty:
                df.to_json(
                    self.processed_dir / f'{name}.json',
                    orient='records',
                    indent=2
                )
        
        # Create summary statistics
        summary = {
            'total_sites': len(sites_df),
            'darkest_site': sites_df.loc[sites_df['median_brightness_mag_arcsec2'].idxmax(), 'site_name'],
            'brightest_site': sites_df.loc[sites_df['median_brightness_mag_arcsec2'].idxmin(), 'site_name'],
            'avg_brightness': float(sites_df['median_brightness_mag_arcsec2'].mean()),
            'processing_timestamp': pd.Timestamp.now().isoformat()
        }

        # Save summary statistics
        with open(self.processed_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Processed data saved to {self.processed_dir}")

def main():
    """Main processing pipeline"""
    processor = OregonSQMProcessor()
    
    # Load raw data
    raw_data = processor.load_raw_data()
    
    # Validate data quality
    validation_results = processor.validate_data(raw_data)
    
    # Merge into master dataset
    sites_master = processor.merge_site_data(raw_data)
    
    # Save processed data
    processor.save_processed_data(sites_master, raw_data)
    
    print("✅ Data processing complete!")
    print(f"📊 Processed {len(sites_master)} sites")
    print(f"📁 Data saved to: shared/data/processed/")

if __name__ == "__main__":
    main()