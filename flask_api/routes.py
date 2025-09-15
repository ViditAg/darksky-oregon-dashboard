"""
Flask routes for Oregon Dark Sky Dashboard.
"""
from flask import render_template, request
from pathlib import Path
import sys

# Add project root to path so 'shared' package is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from shared.utils.configs import get_meas_type_config, meas_type_dict
from shared.utils.data_processing import OregonSQMProcessor
from shared.utils.visualizations import create_oregon_map, create_ranking_chart, create_interactive_2d_plot, get_folium_html

def register_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def index():
        # Get measurement type from form or default
        meas_type = request.form.get("meas_type", "clear_nights_brightness")
        meas_type_config = get_meas_type_config(meas_type)
        processor = OregonSQMProcessor(data_dir=project_root / "shared/data")
        raw_dfs = processor.load_raw_data()
        data_df = raw_dfs[meas_type_config['raw_df_key']]
        geocode_df = raw_dfs['geocode'].copy()
        final_data_df = data_df.merge(geocode_df, on="site_name", how="left")
        if meas_type in ['clear_nights_brightness', 'cloudy_nights_brightness']:
            final_data_df['DarkSkyCertified'] = 'NO'
            final_data_df.loc[final_data_df['median_brightness_mag_arcsec2'] > 21.2, 'DarkSkyCertified'] = 'YES'

        # Map
        cmap = create_oregon_map(
            sites_df=final_data_df,
            main_col=meas_type_config['main_col_'],
            legend_order=meas_type_config['legend_order']
        )
        map_html = get_folium_html(cmap)

        # Bar charts
        fig_bar = create_ranking_chart(
            sites_df=final_data_df,
            y_col=meas_type_config['bar_metric'],
            title=meas_type_config['y_col_print']
        )
        fig_bar2 = create_ranking_chart(
            sites_df=final_data_df,
            y_col=meas_type_config['bar_metric'],
            title=meas_type_config['bar_metric'],
            key="bottom_20"
        )

        # Scatter plot (optional)
        scatter_html = None
        scatter_title = ""
        if meas_type != "% clear nights":
            scatter_title = meas_type_config['scatter_title']
            fig_scatter = create_interactive_2d_plot(
                df=final_data_df,
                x_col=meas_type_config['scatter_x'],
                y_col=meas_type_config['scatter_y'],
                vline=meas_type_config['vline']
            )
            scatter_html = fig_scatter.to_html(full_html=False)

        return render_template(
            "index.html",
            meas_type=meas_type,
            meas_type_dict=meas_type_dict,
            legend_str=meas_type_config['legend_str'],
            map_html=map_html,
            fig_bar=fig_bar.to_html(full_html=False),
            fig_bar2=fig_bar2.to_html(full_html=False),
            scatter_html=scatter_html,
            scatter_title=scatter_title
        )
