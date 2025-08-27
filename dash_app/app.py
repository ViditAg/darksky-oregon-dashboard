# dash_app/app.py (Continued)
"""
Complete Dash implementation of Oregon Dark Sky Dashboard
"""

import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import sys
from pathlib import Path

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent / "shared"))
from utils.data_processing import OregonSQMProcessor

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.title = "Oregon Dark Sky Dashboard - Dash"

# Load data
def load_data():
    """Load processed data"""
    sites_path = Path("shared/data/processed/sites_master.json")
    if sites_path.exists():
        return pd.read_json(sites_path)
    else:
        return pd.DataFrame(columns=['site_name', 'latitude', 'longitude', 'median_brightness_mag_arcsec2'])

sites_df = load_data()

# Custom CSS styles
custom_styles = {
    'header': {
        'backgroundColor': '#1e3a8a',
        'color': 'white',
        'padding': '20px',
        'marginBottom': '20px',
        'borderRadius': '8px'
    },
    'control_panel': {
        'backgroundColor': '#f8f9fa',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px',
        'border': '1px solid #dee2e6'
    },
    'metric_card': {
        'backgroundColor': 'white',
        'padding': '15px',
        'borderRadius': '8px',
        'border': '1px solid #dee2e6',
        'textAlign': 'center',
        'marginBottom': '10px'
    }
}

# App layout
app.layout = dbc.Container([
    # Header
    html.Div([
        html.H1("🌌 Oregon Dark Sky Dashboard", className="text-center mb-2"),
        html.P("Dash Implementation - Interactive Light Pollution Visualization", 
               className="text-center text-muted")
    ], style=custom_styles['header']),
    
    # Control Panel
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Dashboard Controls", className="mb-3"),
                
                # Night type selection
                html.Div([
                    html.Label("Measurement Type:", className="form-label fw-bold"),
                    dcc.RadioItems(
                        id='night-type-radio',
                        options=[
                            {'label': ' Clear Nights', 'value': 'clear'},
                            {'label': ' Cloudy Nights', 'value': 'cloudy'}
                        ],
                        value='clear',
                        inline=True,
                        className="mt-2"
                    )
                ], className="mb-3"),
                
                # Metric selection
                html.Div([
                    html.Label("Bar Chart Metric:", className="form-label fw-bold"),
                    dcc.Dropdown(
                        id='metric-dropdown',
                        options=[
                            {'label': 'Sky Brightness (mag/arcsec²)', 'value': 'brightness'},
                            {'label': 'Bortle Scale', 'value': 'bortle'},
                            {'label': 'Light Pollution Ratio', 'value': 'pollution_ratio'},
                            {'label': 'Annual Change (%)', 'value': 'annual_change'}
                        ],
                        value='brightness',
                        className="mt-1"
                    )
                ], className="mb-3"),
                
                # Sort options
                html.Div([
                    html.Label("Sort Order:", className="form-label fw-bold"),
                    dcc.RadioItems(
                        id='sort-radio',
                        options=[
                            {'label': ' Best to Worst', 'value': 'desc'},
                            {'label': ' Worst to Best', 'value': 'asc'}
                        ],
                        value='desc',
                        inline=True,
                        className="mt-2"
                    )
                ])
            ], style=custom_styles['control_panel'])
        ], width=12)
    ]),
    
    # Key Metrics Row
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4(id="total-sites-metric", className="text-primary mb-1"),
                html.P("Total Monitoring Sites", className="mb-0 text-muted")
            ], style=custom_styles['metric_card'])
        ], width=3),
        dbc.Col([
            html.Div([
                html.H4(id="darkest-site-metric", className="text-success mb-1"),
                html.P("Darkest Measured Sky", className="mb-0 text-muted")
            ], style=custom_styles['metric_card'])
        ], width=3),
        dbc.Col([
            html.Div([
                html.H4(id="certified-sites-metric", className="text-info mb-1"),
                html.P("Dark Sky Certified Sites", className="mb-0 text-muted")
            ], style=custom_styles['metric_card'])
        ], width=3),
        dbc.Col([
            html.Div([
                html.H4(id="avg-change-metric", className="text-warning mb-1"),
                html.P("Average Annual Change", className="mb-0 text-muted")
            ], style=custom_styles['metric_card'])
        ], width=3)
    ], className="mb-4"),
    
    # Main visualization row
    dbc.Row([
        # Map column
        dbc.Col([
            html.H5("🗺️ Interactive Oregon Map", className="mb-3"),
            dcc.Graph(id='oregon-map', style={'height': '600px'}),
            html.Div(id='map-legend', className="mt-2")
        ], width=8),
        
        # Bar chart column
        dbc.Col([
            html.H5("📊 Site Rankings", className="mb-3"),
            dcc.Graph(id='ranking-chart', style={'height': '600px'})
        ], width=4)
    ], className="mb-4"),
    
    # Data table section
    dbc.Row([
        dbc.Col([
            html.H5("📋 Site Data Explorer", className="mb-3"),
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dcc.Input(
                            id="site-search",
                            type="text",
                            placeholder="Search sites...",
                            className="form-control"
                        )
                    ], width=6),
                    dbc.Col([
                        dcc.Checklist(
                            id="show-all-columns",
                            options=[{'label': ' Show All Columns', 'value': 'all'}],
                            value=[],
                            inline=True
                        )
                    ], width=6)
                ], className="mb-3")
            ]),
            dash_table.DataTable(
                id='sites-table',
                columns=[],
                data=[],
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                page_current=0,
                page_size=15,
                style_cell={
                    'textAlign': 'left',
                    'fontSize': 14,
                    'fontFamily': 'Arial'
                },
                style_header={
                    'backgroundColor': '#1e3a8a',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8f9fa'
                    }
                ]
            )
        ], width=12)
    ]),
    
    # Footer
    html.Hr(),
    html.Div([
        html.P([
            "Framework: Dash | Data Source: DarkSky Oregon SQM Network Technical Report Edition #9 | ",
            html.A("GitHub Repository", href="#", target="_blank", className="text-decoration-none")
        ], className="text-center text-muted")
    ])
], fluid=True)

# Callbacks for interactivity
@app.callback(
    [Output('total-sites-metric', 'children'),
     Output('darkest-site-metric', 'children'),
     Output('certified-sites-metric', 'children'),
     Output('avg-change-metric', 'children')],
    [Input('night-type-radio', 'value')]
)
def update_metrics(night_type):
    """Update key metrics based on selected night type"""
    if sites_df.empty:
        return "0", "N/A", "0", "N/A"
    
    # Total sites with coordinates
    total_sites = len(sites_df.dropna(subset=['latitude', 'longitude']))
    
    # Darkest sky measurement
    brightness_col = 'median_brightness_mag_arcsec2' if night_type == 'clear' else 'cloudy_median_brightness'
    if brightness_col in sites_df.columns:
        darkest_brightness = sites_df[brightness_col].max()
        darkest_metric = f"{darkest_brightness:.2f} mag/arcsec²"
    else:
        darkest_metric = "N/A"
    
    # Certified dark sky sites
    certified_sites = len(sites_df[sites_df.get('dark_sky_status', 'None') != 'None'])
    
    # Average annual change
    if 'annual_percent_change' in sites_df.columns:
        avg_change = sites_df['annual_percent_change'].mean()
        change_metric = f"{avg_change:.1f}%"
    else:
        change_metric = "N/A"
    
    return str(total_sites), darkest_metric, str(certified_sites), change_metric

@app.callback(
    [Output('oregon-map', 'figure'),
     Output('map-legend', 'children')],
    [Input('night-type-radio', 'value')]
)
def update_map(night_type):
    """Update map based on selected night type"""
    if sites_df.empty:
        return {}, html.Div()
    
    # Select brightness column
    brightness_col = 'median_brightness_mag_arcsec2' if night_type == 'clear' else 'cloudy_median_brightness'
    
    # Filter data with valid coordinates and brightness
    map_data = sites_df.dropna(subset=['latitude', 'longitude', brightness_col]).copy()
    
    if map_data.empty:
        return {}, html.Div("No data available for mapping")
    
    # Create color categories
    def categorize_brightness(brightness):
        if pd.isna(brightness):
            return 'No Data'
        elif brightness >= 21.5:
            return 'Pristine (≥21.5)'
        elif brightness >= 21.2:
            return 'Excellent (≥21.2)'
        elif brightness >= 20.0:
            return 'Good (≥20.0)'
        elif brightness >= 19.0:
            return 'Fair (≥19.0)'
        else:
            return 'Poor (<19.0)'
    
    map_data['brightness_category'] = map_data[brightness_col].apply(categorize_brightness)
    map_data['size'] = map_data.get('dark_sky_status', 'None').apply(
        lambda x: 15 if x != 'None' else 10
    )
    
    # Create scatter mapbox
    fig = px.scatter_mapbox(
        map_data,
        lat='latitude',
        lon='longitude',
        color='brightness_category',
        size='size',
        hover_name='site_name',
        hover_data={
            brightness_col: ':.2f',
            'bortle_scale': True,
            'dark_sky_status': True,
            'region': True,
            'brightness_category': False,
            'size': False
        },
        color_discrete_map={
            'Pristine (≥21.5)': '#1a5490',
            'Excellent (≥21.2)': '#2d7d32',
            'Good (≥20.0)': '#f9a825',
            'Fair (≥19.0)': '#ff8f00',
            'Poor (<19.0)': '#d32f2f',
            'No Data': '#757575'
        },
        zoom=6,
        center=dict(lat=44.0, lon=-121.0),
        mapbox_style='open-street-map',
        title=f"Oregon Light Pollution Map - {night_type.title()} Nights"
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    # Create legend
    legend = html.Div([
        html.P("Brightness Categories:", className="fw-bold mb-2"),
        html.Div([
            html.Span("🟦", style={'marginRight': '5px'}), "Pristine (≥21.5 mag/arcsec²)", html.Br(),
            html.Span("🟢", style={'marginRight': '5px'}), "Excellent (≥21.2 mag/arcsec²)", html.Br(),
            html.Span("🟡", style={'marginRight': '5px'}), "Good (≥20.0 mag/arcsec²)", html.Br(),
            html.Span("🟠", style={'marginRight': '5px'}), "Fair (≥19.0 mag/arcsec²)", html.Br(),
            html.Span("🔴", style={'marginRight': '5px'}), "Poor (<19.0 mag/arcsec²)"
        ], className="small text-muted")
    ])
    
    return fig, legend

@app.callback(
    Output('ranking-chart', 'figure'),
    [Input('night-type-radio', 'value'),
     Input('metric-dropdown', 'value'),
     Input('sort-radio', 'value')]
)
def update_ranking_chart(night_type, metric, sort_order):
    """Update ranking bar chart"""
    if sites_df.empty:
        return {}
    
    # Metric mapping
    metric_mapping = {
        'brightness': 'median_brightness_mag_arcsec2' if night_type == 'clear' else 'cloudy_median_brightness',
        'bortle': 'bortle_scale',
        'pollution_ratio': 'x_brighter_than_darkest',
        'annual_change': 'annual_percent_change'
    }
    
    y_col = metric_mapping.get(metric, 'median_brightness_mag_arcsec2')
    
    if y_col not in sites_df.columns:
        return {}
    
    # Filter and sort data
    chart_data = sites_df.dropna(subset=[y_col, 'site_name']).copy()
    
    # Determine sort order (brightness is inverse - higher mag = darker = better)
    if metric == 'brightness':
        ascending = (sort_order == 'asc')  # For brightness, asc means worst to best
    else:
        ascending = (sort_order == 'asc')
    
    chart_data = chart_data.sort_values(y_col, ascending=ascending).head(20)  # Top 20
    
    # Color mapping
    colors = ['#2d7d32' if status != 'None' else '#1976d2' 
              for status in chart_data.get('dark_sky_status', ['None'] * len(chart_data))]
    
    # Create horizontal bar chart
    fig = go.Figure(data=go.Bar(
        y=chart_data['site_name'],
        x=chart_data[y_col],
        orientation='h',
        marker=dict(color=colors),
        text=chart_data[y_col].round(2),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<extra></extra>'
    ))
    
    # Update layout
    title_map = {
        'brightness': f'Sky Brightness - {night_type.title()} Nights',
        'bortle': 'Bortle Dark-Sky Scale',
        'pollution_ratio': 'Light Pollution Ratio (vs Darkest)',
        'annual_change': 'Annual Brightness Change (%)'
    }
    
    fig.update_layout(
        title=title_map.get(metric, 'Site Rankings'),
        xaxis_title=title_map.get(metric, "Value"),
        yaxis_title='',
        height=600,
        margin=dict(l=200, r=50, t=50, b=50),
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('sites-table', 'columns'),
    Output('sites-table', 'data'),
    [Input('show-all-columns', 'value'),
     Input('site-search', 'value'),
     Input('night-type-radio', 'value')]
)
def update_table(show_all, search_term, night_type):
    """Update data table"""
    if sites_df.empty:
        return [], []
    
    # Determine columns to show
    if 'all' in show_all:
        columns = [{"name": col, "id": col} for col in sites_df.columns]
        display_df = sites_df.copy()
    else:
        essential_cols = ['site_name', 'median_brightness_mag_arcsec2', 'bortle_scale', 
                         'dark_sky_status', 'region', 'latitude', 'longitude']
        available_cols = [col for col in essential_cols if col in sites_df.columns]
        columns = [{"name": col.replace('_', ' ').title(), "id": col} for col in available_cols]
        display_df = sites_df[available_cols].copy()
    
    # Apply search filter
    if search_term:
        display_df = display_df[
            display_df['site_name'].str.contains(search_term, case=False, na=False)
        ]
    
    return columns, display_df.to_dict('records')

# Run app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)