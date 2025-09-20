"""
Unit tests for shared.utils.visualizations
"""
import unittest

import folium
from shared.utils.visualizations import create_oregon_map, create_ranking_chart
import pandas as pd

# Test class for visualizations
class TestVisualizations(unittest.TestCase):
    def setUp(self):
        # Sample DataFrame for testing
        self.df = pd.DataFrame({
            "site_name": ["SiteA", "SiteB"],
            "median_brightness_mag_arcsec2": [21.5, 20.0],
            "latitude": [44.0, 45.0],
            "longitude": [-123.0, -122.0]
        })

    def test_create_oregon_map(self):
        """
        Test the creation of an Oregon map with folium.
        """
        # Create the map
        fmap = create_oregon_map(
            self.df,
            main_col="median_brightness_mag_arcsec2",
            legend_order=["Green", "Yellow", "Red"]
        )
        # Check that the map is created
        self.assertIsNotNone(fmap)
        
        # and that it is a folium Map object
        self.assertIsInstance(fmap, folium.Map)

        # Check that the map has markers (children)
        self.assertGreater(len(fmap._children), 0)

    
    def test_create_ranking_chart(self):
        """
        Test the creation of a ranking chart with plotly."""
        # Create the ranking chart
        fig = create_ranking_chart(
            self.df,
            y_col="median_brightness_mag_arcsec2"
        )
        # Check that the figure is created
        self.assertIsNotNone(fig)
        # and that it is a plotly Figure object
        from plotly.graph_objs import Figure
        self.assertIsInstance(fig, Figure)
        # Check that the figure has data
        self.assertGreater(len(fig.data), 0)

    def test_create_interactive_2d_plot(self):
        """
        Test the creation of an interactive 2D scatter plot with plotly.
        """
        from shared.utils.visualizations import create_interactive_2d_plot
        # Create the scatter plot
        fig = create_interactive_2d_plot(
            self.df,
            x_col="median_brightness_mag_arcsec2",
            y_col="site_name",
            vline=21.0
        )
        # Check that the figure is created
        self.assertIsNotNone(fig)
        # and that it is a plotly Figure object
        from plotly.graph_objs import Figure
        self.assertIsInstance(fig, Figure)
        # Check that the figure has data
        self.assertGreater(len(fig.data), 0)
        # Check that the x-axis is labeled correctly
        self.assertEqual(fig.layout.xaxis.title.text, "median_brightness_mag_arcsec2")
        # Check that the y-axis is labeled "Site"
        self.assertEqual(fig.layout.yaxis.title.text, "site_name")


if __name__ == "__main__":
    unittest.main()
