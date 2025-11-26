"""
Unit tests for shared.utils.visualizations
"""
import unittest

import folium
import plotly.graph_objects as go
from shared.utils.visualizations import (
    create_oregon_map_folium, 
    create_oregon_map_plotly,
    create_ranking_chart,
    create_interactive_2d_plot
)
import pandas as pd

# Test class for visualizations
class TestVisualizations(unittest.TestCase):
    def setUp(self):
        """
        Set up test environment.
        """
        # Set default parameters
        self.default_zoom = 6
        self.default_map_center = [44.0, -121.0]
        self.clicked_sites = ["SiteA"]

        # Sample DataFrame for testing
        self.df = pd.DataFrame({
            "site_name": ["SiteA", "SiteB"],
            "median_brightness_mag_arcsec2": [21.5, 20.0],
            "x_brighter_than_darkest_night_sky": [2.0, 10.0],
            "latitude": [44.0, 45.0],
            "longitude": [-123.0, -122.0],
            "color_rgba": ["rgba(0, 200, 210, 1)", "rgba(255, 0, 0, 1)"] 
        })
        
        # Sample config for current functions
        self.sample_configs = {
            'bar_chart_y_col': 'median_brightness_mag_arcsec2',
            'bar_chart_y_label': 'Median Brightness',
            'bar_chart_yicks': {
                'tickmode': 'linear',
                'tickvals': [20, 21, 22],
                'ticktext': ["20", "21", "22"]
            },
            'scatter_x_col': 'median_brightness_mag_arcsec2',
            'scatter_y_col': 'x_brighter_than_darkest_night_sky', 
            'scatter_x_label': 'Median Brightness',
            'scatter_y_label': 'Site Name'
        }

    def test_create_oregon_map_folium(self):
        """
        Test the creation of an Oregon map with folium.
        """
        # Create a folium map
        fmap = create_oregon_map_folium(
            sites_df=self.df,
            main_col=self.sample_configs['bar_chart_y_col'],
            zoom=self.default_zoom,
            map_center=self.default_map_center,
            highlight_sites=self.clicked_sites
        )
        # Check that the map is created
        self.assertIsNotNone(fmap)
        
        # and that it is a folium Map object
        self.assertIsInstance(fmap, folium.Map)

        # Check that the map has markers (children)
        self.assertGreater(len(fmap._children), 0)

    def test_create_oregon_map_plotly(self):
        """
        Test the creation of an Oregon map with plotly.
        """
        # Create the map
        fig = create_oregon_map_plotly(
            sites_df=self.df,
            color_col=self.sample_configs['scatter_x_col'],
            zoom=self.default_zoom,
            map_center=self.default_map_center,
            highlight_sites=self.clicked_sites
        )
        # Check that the map is created
        self.assertIsNotNone(fig)
        
        # and that it is a plotly Figure object
        self.assertIsInstance(fig, go.Figure)

        # Check that the map has data
        self.assertGreater(len(fig.data), 0)

    
    def test_create_ranking_chart(self):
        """
        Test the creation of a ranking chart with plotly."""
        # Create the ranking chart with configs
        fig = create_ranking_chart(
            sites_df=self.df,
            configs=self.sample_configs,
            clicked_sites=self.clicked_sites,
        )

        # Check that the figure is created
        self.assertIsNotNone(fig)
        # and that it is a plotly Figure object
        self.assertIsInstance(fig, go.Figure)
        # Check that the figure has data
        self.assertGreater(len(fig.data), 0)

    def test_create_interactive_2d_plot(self):
        """
        Test the creation of an interactive 2D scatter plot with plotly.
        """
        # Create the scatter plot with configs
        fig = create_interactive_2d_plot(
                df=self.df,
                configs=self.sample_configs,
                vline=21.2,
                clicked_sites=self.clicked_sites
            )
        # Check that the figure is created
        self.assertIsNotNone(fig)
        # and that it is a plotly Figure object
        self.assertIsInstance(fig, go.Figure)
        # Check that the figure has data
        self.assertGreater(len(fig.data), 0)
        # Check that axes are labeled with config values
        self.assertEqual(fig.layout.xaxis.title.text, self.sample_configs['scatter_x_label'])
        self.assertEqual(fig.layout.yaxis.title.text, self.sample_configs['scatter_y_label'])


if __name__ == "__main__":
    unittest.main()
