"""
Unit tests for shared.utils.data_processing.OregonSQMProcessor
"""
# standard libraries
import unittest
import pandas as pd
from pathlib import Path
from shared.utils.data_processing import OregonSQMProcessor

# Test class for OregonSQMProcessor
class TestOregonSQMProcessor(unittest.TestCase):
    def setUp(self):
        """
        Set up test environment.
        """
        # Initialize the processor with test data directory
        self.processor = OregonSQMProcessor(data_dir=Path("shared/data"))
        
        # Initialize expected data to compare against
        self.expected_data = {
            'sites': pd.DataFrame(
                columns=['Name', 'Install_Number'],
                data=[
                    ['Awbrey Butte', 1],
                    ['Pine Mountain Observatory', 2]
                ]
            ),
            'geocode': pd.DataFrame(
                columns=['site_name', 'latitude', 'longitude', 'Elevation_in_meters'],
                data=[
                    ['Awbrey Butte', 44.08, -121.33, 1272.0],
                    ['Pine Mountain Observatory', 43.79, -120.94, 1912.0]
                ]
            ),
            'clear_measurements': pd.DataFrame(
                columns=[
                    'site_name',
                    'median_brightness_mag_arcsec2',
                    'bortle_sky_level',
                    'median_linear_scale_flux_ratio',
                    'x_brighter_than_darkest_night_sky'
                ],
                data=[
                    ['Eugene Downtown', 18.27, 7, 12.36, 26.79],
                    ['Portland SE', 18.45, 7, 10.47, 22.70]
                ]
            ),
            'cloudy_measurements': pd.DataFrame(
                columns=[
                    'site_name',
                    'median_brightness_mag_arcsec2',
                    'median_linear_scale_flux_ratio',
                    'x_brighter_than_darkest_night_sky'
                ],
                data=[
                    ['Eugene Downtown', 15.94, 94.62, 436.52],
                    ['Portland SE', 16.35, 63.68, 293.76]
                ]
            ),
            'trends': pd.DataFrame(
                columns=[
                    'site_name',
                    'Number_of_Years_of_Data',
                    'Percent_Change_per_year',
                    'Regression_Line_Slope_x_10000',
                    'Rate_of_Change_vs_Prineville_Reservoir_State_Park'
                ],
                data=[
                    ['Hopservatory', 5, 6.8, 5.979, 174.1],
                    ['Mt Pisgah Arboretum', 3, 4.0, 2.484, 72.4]
                ]
            ),
            'milky_way': pd.DataFrame(
                columns=['site_name', 'difference_index_mag_arcsec2', 'ratio_index'],
                data=[
                    ['Powell Butte Park', -0.07, 0.938],
                    ['Portland SE', -0.06, 0.946]
                ]
            ),
            'cloud_coverage': pd.DataFrame(
                columns=['site_name', 'percent_clear_night_samples_all_months'],
                data=[
                    ['Hyatt Lake', 48.4],
                    ['Summit Prairie', 46.8]
                ]
            )
        }

    
    def test_load_raw_data(self):
        """
        Test loading of raw data files.
        """
        # load raw data
        data = self.processor.load_raw_data()
        
        # Check that data is a dictionary
        self.assertIsInstance(data, dict)

        # Check that all expected keys are present
        for expected_key in self.expected_data.keys():
            self.assertIn(expected_key, data)

        # loop through each DataFrame and check it's valid
        for df in data.values():
            # Check that each value is a DataFrame
            self.assertIsInstance(df, pd.DataFrame)
            # Check that each DataFrame is not empty
            self.assertFalse(df.empty)

        # Check that the DataFrames have the expected columns
        for key, expected_df in self.expected_data.items():
            actual_df = data[key]
            # Check that the columns match between actual and expected DataFrames
            self.assertListEqual(
                list(actual_df.columns),
                list(expected_df.columns),
                f"Columns mismatch for {key}"
            )
        # Check that the DataFrames have the expected dtypes
        for key, expected_df in self.expected_data.items():
            actual_df = data[key]
            for col in expected_df.columns:
                # Check that the dtypes match between actual and expected DataFrames
                self.assertEqual(
                    actual_df[col].dtype,
                    expected_df[col].dtype,
                    f"Dtype mismatch for {col} in {key}"
                )

    
    def test_load_processed_data(self):
        """
        Test loading and processing of data for a specific measurement type.
        """
        # list of valid raw_df_key values to test
        valid_keys = [
            'clear_measurements',
            'cloudy_measurements',
            'trends',
            'milky_way',
            'cloud_coverage'
        ]
        for key in valid_keys:
            # Load processed data for each key
            processed_df = self.processor.load_processed_data(raw_df_key=key)
            # Check that the result is not None
            self.assertIsNotNone(processed_df)
            # Check that the result is a DataFrame
            self.assertIsInstance(processed_df, pd.DataFrame)
            # Check that the DataFrame is not empty
            self.assertFalse(processed_df.empty, f"DataFrame for key '{key}' is empty")
            
            # Check that expected columns are present
            expected_columns = ['site_name', 'latitude', 'longitude', 'Elevation_in_meters']
            for col in expected_columns:
                self.assertIn(col, processed_df.columns)
            
            # Check that site_name column has string type and no nulls
            self.assertTrue(pd.api.types.is_string_dtype(processed_df['site_name']))
            self.assertFalse(processed_df['site_name'].isnull().any())
            # Check that latitude and longitude columns are numeric and have no nulls
            for col in ['latitude', 'longitude', 'Elevation_in_meters']:
                self.assertTrue(pd.api.types.is_numeric_dtype(processed_df[col]))
                self.assertFalse(processed_df[col].isnull().any())

            if key in ['clear_measurements', 'cloudy_measurements']:
                # Check that brightness columns are numeric and have no nulls
                brightness_cols = [
                    'median_brightness_mag_arcsec2',
                    'median_linear_scale_flux_ratio',
                    'x_brighter_than_darkest_night_sky'
                ]
                for col in brightness_cols:
                    self.assertIn(col, processed_df.columns)
                    self.assertTrue(pd.api.types.is_numeric_dtype(processed_df[col]))
                    self.assertFalse(processed_df[col].isnull().any())
            elif key == 'trends':
                # Check that trend-related columns are numeric and have no nulls
                trend_cols = [
                    'Number_of_Years_of_Data',
                    'Percent_Change_per_year',
                    'Regression_Line_Slope_x_10000',
                    'Rate_of_Change_vs_Prineville_Reservoir_State_Park'
                ]
                for col in trend_cols:
                    self.assertIn(col, processed_df.columns)
                    self.assertTrue(pd.api.types.is_numeric_dtype(processed_df[col]))
                    self.assertFalse(processed_df[col].isnull().any())
            elif key == 'milky_way':
                # Check that milky way related columns are numeric and have no nulls
                milky_way_cols = ['difference_index_mag_arcsec2', 'ratio_index']
                for col in milky_way_cols:
                    self.assertIn(col, processed_df.columns)
                    self.assertTrue(pd.api.types.is_numeric_dtype(processed_df[col]))
                    self.assertFalse(processed_df[col].isnull().any())
            elif key == 'cloud_coverage':
                # Check that cloud coverage column is numeric and has no nulls
                self.assertIn('percent_clear_night_samples_all_months', processed_df.columns)
                self.assertTrue(pd.api.types.is_numeric_dtype(processed_df['percent_clear_night_samples_all_months']))
                self.assertFalse(processed_df['percent_clear_night_samples_all_months'].isnull().any())
            else: pass

if __name__ == "__main__":
    # Run the tests via command line
    unittest.main()
