# Flask implementation
# flask_api/app.py
"""
Flask API implementation of Oregon Dark Sky Dashboard
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../shared')))
from utils.visualizations import create_oregon_map, create_ranking_chart, get_folium_html, get_plotly_html
from pathlib import Path

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent / "shared"))
from utils.data_processing import OregonSQMProcessor

from utils.visualizations import create_oregon_map, create_ranking_chart, get_folium_html, get_plotly_html

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Load data globally
def load_data():
    """Load processed data"""
    sites_path = Path("shared/data/processed/sites_master.json")
    if sites_path.exists():
        return pd.read_json(sites_path)
    else:
        return pd.DataFrame()

sites_df = load_data()

# API Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/sites')
def get_sites():
    """Get all sites data"""
    night_type = request.args.get('night_type', 'clear')
    search = request.args.get('search', '')
    
    # Filter data
    filtered_df = sites_df.copy()
    
    if search:
        filtered_df = filtered_df[
            filtered_df['site_name'].str.contains(search, case=False, na=False)
        ]
    
    # Convert to JSON-serializable format
    sites_data = []
    for idx, row in filtered_df.iterrows():
        site_data = {
            'site_name': row.get('site_name', 'Unknown'),
            'latitude': float(row['latitude']) if pd.notna(row.get('latitude')) else None,
            'longitude': float(row['longitude']) if pd.notna(row.get('longitude')) else None,
            'median_brightness_mag_arcsec2': float(row['median_brightness_mag_arcsec2']) if pd.notna(row.get('median_brightness_mag_arcsec2')) else None,
            'bortle_scale': int(row['bortle_scale']) if pd.notna(row.get('bortle_scale')) else None,
            'dark_sky_status': row.get('dark_sky_status', 'None'),
            'region': row.get('region', 'Unknown'),
            'x_brighter_than_darkest': float(row['x_brighter_than_darkest']) if pd.notna(row.get('x_brighter_than_darkest')) else None,
            'annual_percent_change': float(row['annual_percent_change']) if pd.notna(row.get('annual_percent_change')) else None
        }
        sites_data.append(site_data)
    
    return jsonify({
        'sites': sites_data,
        'total_count': len(sites_data)
    })

@app.route('/api/metrics')
def get_metrics():
    """Get key dashboard metrics"""
    night_type = request.args.get('night_type', 'clear')
    
    # Calculate metrics
    total_sites = len(sites_df.dropna(subset=['latitude', 'longitude']))
    
    brightness_col = 'median_brightness_mag_arcsec2' if night_type == 'clear' else 'cloudy_median_brightness'
    if brightness_col in sites_df.columns:
        darkest_brightness = float(sites_df[brightness_col].max()) if not sites_df[brightness_col].isna().all() else None
    else:
        darkest_brightness = None
    
    certified_sites = len(sites_df[sites_df.get('dark_sky_status', 'None') != 'None'])
    
    if 'annual_percent_change' in sites_df.columns:
        avg_change = float(sites_df['annual_percent_change'].mean()) if not sites_df['annual_percent_change'].isna().all() else None
    else:
        avg_change = None
    
    return jsonify({
        'total_sites': total_sites,
        'darkest_brightness': darkest_brightness,
        'certified_sites': certified_sites,
        'avg_annual_change': avg_change
    })

@app.route('/api/map')
def get_map_data():
    """Generate map visualization data"""
    night_type = request.args.get('night_type', 'clear')
    
    brightness_col = 'median_brightness_mag_arcsec2' if night_type == 'clear' else 'cloudy_median_brightness'
    
    # Filter data with valid coordinates and brightness
    map_data = sites_df.dropna(subset=['latitude', 'longitude', brightness_col]).copy()
    
    if map_data.empty:
        return jsonify({'error': 'No data available for mapping'})
    
    # Create Plotly figure
    fig = px.scatter_mapbox(
        map_data,
        lat='latitude',
        lon='longitude',
        color='median_brightness_mag_arcsec2',
        size=[15 if status != 'None' else 10 for status in map_data.get('dark_sky_status', ['None'] * len(map_data))],
        hover_name='site_name',
        hover_data=[brightness_col, 'bortle_scale', 'dark_sky_status', 'region'],
        color_continuous_scale='Viridis_r',
        zoom=6,
        center=dict(lat=44.0, lon=-121.0),
        mapbox_style='open-street-map',
        title=f"Oregon Light Pollution Map - {night_type.title()} Nights"
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/ranking')
def get_ranking_data():
    """Generate ranking chart data"""
    night_type = request.args.get('night_type', 'clear')
    metric = request.args.get('metric', 'brightness')
    sort_order = request.args.get('sort_order', 'desc')
    limit = int(request.args.get('limit', 20))
    
    # Metric mapping
    metric_mapping = {
        'brightness': 'median_brightness_mag_arcsec2' if night_type == 'clear' else 'cloudy_median_brightness',
        'bortle': 'bortle_scale',
        'pollution_ratio': 'x_brighter_than_darkest',
        'annual_change': 'annual_percent_change'
    }
    
    y_col = metric_mapping.get(metric, 'median_brightness_mag_arcsec2')
    
    if y_col not in sites_df.columns:
        return jsonify({'error': f'Column {y_col} not found'})
    
    # Filter and sort data
    chart_data = sites_df.dropna(subset=[y_col, 'site_name']).copy()
    
    # Determine sort order
    if metric == 'brightness':
        ascending = (sort_order == 'asc')
    else:
        ascending = (sort_order == 'asc')
    
    chart_data = chart_data.sort_values(y_col, ascending=ascending).head(limit)
    
    # Create bar chart
    colors = ['#2d7d32' if status != 'None' else '#1976d2' 
              for status in chart_data.get('dark_sky_status', ['None'] * len(chart_data))]
    
    fig = go.Figure(data=go.Bar(
        y=chart_data['site_name'],
        x=chart_data[y_col],
        orientation='h',
        marker=dict(color=colors),
        text=chart_data[y_col].round(2),
        textposition='outside'
    ))
    
    title_map = {
        'brightness': f'Sky Brightness - {night_type.title()} Nights',
        'bortle': 'Bortle Dark-Sky Scale',
        'pollution_ratio': 'Light Pollution Ratio',
        'annual_change': 'Annual Change (%)'
    }
    
    fig.update_layout(
        title=title_map.get(metric, 'Site Rankings'),
        xaxis_title=title_map.get(metric, "Value"),
        yaxis_title='',
        height=600,
        margin=dict(l=200, r=50, t=50, b=50),
        showlegend=False
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)