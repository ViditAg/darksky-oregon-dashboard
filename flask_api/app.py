# Flask implementation
# flask_api/app.py
"""
Flask API implementation of Oregon Dark Sky Dashboard
"""
"""
Flask implementation of the Oregon Dark Sky Dashboard

This app loads all site and measurement data from CSVs using OregonSQMProcessor, sets up Flask routes, and renders the dashboard UI:
    - Loads site and measurement data from CSVs
    - Provides API endpoints for site data, metrics, map, and ranking chart
    - Renders the main dashboard page and handles user requests
    - Returns JSON or HTML responses for all dashboard features
"""


from flask import Flask, render_template, jsonify, request
import json
from shared.utils.data_processing import OregonSQMProcessor
from shared.utils.visualizations import create_oregon_map, create_ranking_chart, get_folium_html, get_plotly_html

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Use shared processor for all data
processor = OregonSQMProcessor()
raw_dfs = processor.load_raw_data()

# API Routes

@app.route('/')
def index():
    """Main dashboard page (placeholder)"""
    return '<h2>Oregon Dark Sky Dashboard API (Flask)</h2><p>See /api/sites, /api/metrics, /api/map, /api/ranking</p>'


@app.route('/api/sites')
def get_sites():
    """Get all sites data (from shared utils)"""
    sites_df = raw_dfs['sites']
    search = request.args.get('search', '')
    if search:
        filtered_df = sites_df[sites_df['site_name'].str.contains(search, case=False, na=False)]
    else:
        filtered_df = sites_df
    sites_data = filtered_df.to_dict(orient='records')
    return jsonify({'sites': sites_data, 'total_count': len(sites_data)})


@app.route('/api/metrics')
def get_metrics():
    """Get key dashboard metrics (from shared utils)"""
    sites_df = raw_dfs['sites']
    total_sites = len(sites_df.dropna(subset=['latitude', 'longitude']))
    brightness_col = 'median_brightness_mag_arcsec2'
    darkest_brightness = float(sites_df[brightness_col].max()) if brightness_col in sites_df.columns else None
    certified_sites = len(sites_df[sites_df.get('dark_sky_status', 'None') != 'None'])
    avg_change = float(sites_df['annual_percent_change'].mean()) if 'annual_percent_change' in sites_df.columns else None
    return jsonify({
        'total_sites': total_sites,
        'darkest_brightness': darkest_brightness,
        'certified_sites': certified_sites,
        'avg_annual_change': avg_change
    })


@app.route('/api/map')
def get_map_data():
    """Generate map visualization using shared utils"""
    sites_df = raw_dfs['sites']
    folium_map = create_oregon_map(sites_df, main_col='median_brightness_mag_arcsec2', legend_order=['green', 'yellow', 'red'])
    html_map = get_folium_html(folium_map)
    return html_map


@app.route('/api/ranking')
def get_ranking_data():
    """Generate ranking chart using shared utils"""
    sites_df = raw_dfs['sites']
    fig = create_ranking_chart(sites_df, y_col='median_brightness_mag_arcsec2', title='Sky Brightness Ranking')
    return get_plotly_html(fig)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)