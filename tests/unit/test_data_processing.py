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
                columns=['Name', 'Install Number'],
                data=[
                    ['Awbrey Butte', 1],
                    ['Pine Mountain Observatory', 2]
                ]
            ),
            'geocode': pd.DataFrame(
                columns=['site_name', 'latitude', 'longitude'],
                data=[
                    ['Awbrey Butte', 44.1, -121.3],
                    ['Pine Mountain Observatory', 43.8, -120.9]
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
                    ['Hopservatory', 5.1, 6.8, 5.979, 174.1],
                    ['Mt Pisgah Arboretum', 3.2, 4.0, 2.484, 72.4]
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
            ),
            'colormap_clear': pd.DataFrame(
                columns=['brightness_mag_arcsec2','red','green','blue','transparency'],
                data=[
                    [0.010,255,255,255,255],
                    [8.970,255,255,255,255]
                ]
            ),
            'colormap_cloudy': pd.DataFrame(
                columns=['brightness_mag_arcsec2','red','green','blue','transparency'],
                data=[
                    [0.010,255,255,255,255],
                    [8.970,255,255,255,255]
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
        
        def assert_column_data(df, col):
            """ Helper function to assert column data type and non-null values."""
            self.assertIn(col, df.columns)
            self.assertTrue(pd.api.types.is_numeric_dtype(df[col]))
            self.assertFalse(df[col].isnull().any())
        
        for key in valid_keys:
            if key in ['clear_measurements', 'cloudy_measurements']:
                value_col = "median_brightness_mag_arcsec2"
            elif key == 'trends':
                value_col = "Rate_of_Change_vs_Prineville_Reservoir_State_Park"
            elif key == 'milky_way':
                value_col = "ratio_index"
            elif key == 'cloud_coverage':
                value_col = "percent_clear_night_samples_all_months"
            else:
                value_col = None
            
            # Load processed data for each key
            processed_df = self.processor.load_processed_data(
                data_key=key,
                bar_chart_col=value_col
            )
            # Check that the result is not None
            self.assertIsNotNone(processed_df)
            # Check that the result is a DataFrame
            self.assertIsInstance(processed_df, pd.DataFrame)
            # Check that the DataFrame is not empty
            self.assertFalse(processed_df.empty, f"DataFrame for key '{key}' is empty")
            
            # Check that expected columns are present and have no nulls and are of string type
            for col in ['site_name', 'color_rgba']:
                self.assertIn(col, processed_df.columns)
                self.assertFalse(processed_df[col].isnull().any())
                self.assertTrue(pd.api.types.is_string_dtype(processed_df[col]))
            
            # initialize list of other columns to check
            extra_cols_to_check = ['latitude', 'longitude',]

            # Determine additional columns to check based on data_key
            if key in ['clear_measurements', 'cloudy_measurements']:
                add_cols = [
                    'median_brightness_mag_arcsec2',
                    'median_linear_scale_flux_ratio',
                    'x_brighter_than_darkest_night_sky'
                ]
            
            elif key == 'trends':
                add_cols = [
                    'Number_of_Years_of_Data',
                    'Percent_Change_per_year',
                    'Regression_Line_Slope_x_10000',
                    'Rate_of_Change_vs_Prineville_Reservoir_State_Park'
                ]
                
            elif key == 'milky_way':
                add_cols = ['difference_index_mag_arcsec2', 'ratio_index']
                
            elif key == 'cloud_coverage':
                add_cols = ['percent_clear_night_samples_all_months']

            else: add_cols = []

            # extend the list of columns to check
            extra_cols_to_check.extend(add_cols)

            # Check that these columns are present, numeric, and have no nulls
            for col in extra_cols_to_check: 
                print(col)
                assert_column_data(processed_df, col)

            if key == 'clear_measurements':
                for col in ['DarkSkyQualified', 'DarkSkyCertified']:
                    # Check that these columns are present and boolean
                    self.assertIn(col, processed_df.columns)
                    self.assertTrue(pd.api.types.is_string_dtype(processed_df[col]))
                    self.assertFalse(processed_df[col].isnull().any())               

if __name__ == "__main__":
    # Run the tests via command line
    unittest.main()
