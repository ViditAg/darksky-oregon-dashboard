# dash_app/app.py (Continued)
"""
Complete Dash implementation of Oregon Dark Sky Dashboard
"""


import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
from shared.utils.data_processing import OregonSQMProcessor
from shared.utils.visualizations import create_oregon_map, create_ranking_chart, get_folium_html, get_plotly_html
import plotly.graph_objects as go

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.title = "Oregon Dark Sky Dashboard - Dash"

def load_data():
sites_df = load_data()

# Use shared processor for all data
processor = OregonSQMProcessor()
raw_dfs = processor.load_raw_data()
sites_df = raw_dfs['sites']

# Custom CSS styles
custom_styles = {
    'header': {
        'backgroundColor': '#1e3a8a',
        'color': 'white',
"""
Dash implementation of the Oregon Dark Sky Dashboard

This app loads all site and measurement data from CSVs using OregonSQMProcessor, sets up the Dash layout, and defines all callbacks for interactivity:
    - Loads site and measurement data from CSVs
    - Provides controls for night type, metric selection, and sorting
    - Displays key statistics, interactive map, and ranking chart
    - Shows a searchable, filterable data table of all sites
    - Handles all Dash callback logic for UI updates
"""
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


# Callbacks for interactivity (using shared modules)
@app.callback(
    [Output('total-sites-metric', 'children'),
     Output('darkest-site-metric', 'children'),
     Output('certified-sites-metric', 'children'),
     Output('avg-change-metric', 'children')],
    [Input('night-type-radio', 'value')]
)
def update_metrics(night_type):
    if sites_df.empty:
        return "0", "N/A", "0", "N/A"
    total_sites = len(sites_df.dropna(subset=['latitude', 'longitude']))
    brightness_col = 'median_brightness_mag_arcsec2'
    darkest_brightness = sites_df[brightness_col].max() if brightness_col in sites_df.columns else None
    darkest_metric = f"{darkest_brightness:.2f} mag/arcsec²" if darkest_brightness else "N/A"
    certified_sites = len(sites_df[sites_df.get('dark_sky_status', 'None') != 'None'])
    avg_change = sites_df['annual_percent_change'].mean() if 'annual_percent_change' in sites_df.columns else None
    change_metric = f"{avg_change:.1f}%" if avg_change else "N/A"
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
    
    # Use Plotly for map visualization (modularized)
    # You can replace this with a Plotly map or static image as needed
    return {}, html.Div("Map visualization is modularized; see shared/utils/visualizations.py")

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
    
    # Use the shared create_ranking_chart for Dash
    # Removed erroneous call to create_ranking_chart outside function scope