# dash_app/app.py
"""
Complete Dash implementation of Oregon Dark Sky Dashboard
"""
import sys
from pathlib import Path
import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# local import
# Add project root to path so 'shared' package is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from shared.utils.configs import get_meas_type_config, meas_type_dict
from shared.utils.data_processing import OregonSQMProcessor
from shared.utils.visualizations import create_interactive_2d_plot, create_oregon_map, create_ranking_chart, get_folium_html, get_plotly_html

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
)
# Set the title for the app
app.title = "Oregon Dark Sky Dashboard - Dash"

# Use data saved in shared directory
processor = OregonSQMProcessor(data_dir=project_root / "shared/data")
raw_dfs = processor.load_raw_data()

# here we define the custom CSS styles for various DASH components
custom_styles = {
    'header': {
        'backgroundColor': "#263C77",
        'color': 'white',
"""
Dash implementation of the Oregon Dark Sky Dashboard

This app loads all site and measurement data from CSVs using OregonSQMProcessor, sets up the Dash layout, and defines all callbacks for interactivity:
    - Loads site and measurement data from CSVs
    - Provides controls for selecting measurement type
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


# this is the main layout of the app created using Dash Bootstrap Components
app.layout = dbc.Container(
    [
        # Header
        html.Div(
            [
                html.H1(
                    "Dark Sky Oregon - Skyglow Dashboard",
                    className="text-center mb-2"
                ),
                html.A(
                    "Visit Dark Sky Oregon Website",
                    href="https://www.darkskyoregon.org/",
                    target="_blank",
                    className="d-block text-center mb-2",
                    style={"color": "white"}
                )
            ],
            style=custom_styles['header']
        ),
        # Control Panel (mirroring Streamlit sidebar)
        dbc.Col(
            [
                html.Div(
                    [
                        html.Label(
                            "Question?",
                            className="form-label fw-bold"
                        ),
                        dcc.RadioItems(
                            id='meas-type-radio',
                            options=[{'label': meas_type_dict[k]['Question_text'], 'value': k} for k in meas_type_dict.keys()],
                            value='clear_nights_brightness',
                            className="mb-3"
                        )
                    ],
                    style={**custom_styles['control_panel'], 'width': '100%'}
                )
            ],
            width=12
        ),
        # Main visualization row``
        dbc.Row(
            [
                # Map column
                dbc.Col(
                    [
                        html.H5(
                            "SQM measurement site map",
                            className="mb-3"
                        ),
                        html.Iframe(
                            id='oregon-map',
                            style={'height': '400px', 'width': '100%'}
                        ),
                        html.Div(
                            id='map-legend',
                            className="mt-2"
                        )
                    ],
                    # width=8 removed; if this is dbc.Col, width is valid. If html.Div, use style.
                ),
                # Bar chart column
                dbc.Col(
                    [
                        html.H5(
                            "Worst 20 sites",
                            className="mb-3"
                        ),
                        dcc.Graph(
                            id='ranking-chart-top20',
                            style={'height': '400px'})
                    ],
                    # width=4 removed; if this is dbc.Col, width is valid. If html.Div, use style.
                )
            ],
            className="mb-4"
        ),

        # second visualization row
        dbc.Row(
            [
                # Scatter Plot column
                dbc.Col(
                    [
                        html.H5(
                            "Scatter Plot",
                            className="mb-3"
                        ),
                        html.Div(
                            id="scatter-plot-title",
                            className="text-center mb-3"
                        ),
                        html.Div(
                            id="scatter-plot-div",
                            children=[
                                dcc.Graph(
                                    id='scatter-plot',
                                    style={'height': '400px'}
                                )
                            ]
                        )
                    ],
                    # width=4 removed; if this is dbc.Col, width is valid. If html.Div, use style.
                ),
                # Bar chart column
                dbc.Col(
                    [
                        html.H5(
                            "Pristine 20 sites",
                            className="mb-3"
                        ),
                        dcc.Graph(
                            id='ranking-chart-bottom20',
                            style={'height': '400px'}
                        )
                    ],
                    # width=4 removed; if this is dbc.Col, width is valid. If html.Div, use style.
                )
            ]
        ),

        # Footer
        html.Hr(), # Divider Horizontal line
        # Footer content
        html.Div(
            [
                html.P(
                    [
                    "Framework: Dash | Data Source: ",
                    html.A(
                        "DarkSky Oregon SQM Network Technical Report Edition #9",
                        href="https://static1.squarespace.com/static/64325bb7c8993f109f0e62cb/t/679c8b55f32ba64b8739b9c2/1738312560582/DarkSky_Oregon_SQM_Network_TechnicalReport_Edition_09_v3_cmpress.pdf",
                        target="_blank"
                    ),
                    html.A(
                        "Repository: https://github.com/ViditAg/darksky-oregon-dashboard",
                        href="https://github.com/ViditAg/darksky-oregon-dashboard",
                        target="_blank",
                        className="text-decoration-none"
                    )
                    ],
                    className="text-center text-muted"
                )
            ],
            style={'width': '100%'}
        )   
    ],
    className="mb-4" # this parameter adds margin-bottom spacing of 1.5rem 
)

  
# Callbacks for interactivity (mirroring Streamlit logic)
@app.callback(
    [
        Output('oregon-map', 'srcDoc'),
        Output('map-legend', 'children'),
        Output('ranking-chart-top20', 'figure'),
        Output('ranking-chart-bottom20', 'figure'),
        Output('scatter-plot', 'figure'),
        Output('scatter-plot-div', 'style'),
        Output('scatter-plot-title', 'children')
    ],
    [Input('meas-type-radio', 'value')]
)
def update_dashboard(meas_type):
    """
    Update map and ranking chart based on selected measurement type

    Parameters:
    - meas_type: The selected measurement type

    Returns:
    - A tuple containing the updated map figure and ranking chart figure
    """
    # data-table based on selected measurement type
    meas_type_config = get_meas_type_config(meas_type)
    # read data into data-frame
    data_df = raw_dfs[meas_type_config['raw_df_key']]
    # read geocode data into data-frame
    geocode_df = raw_dfs['geocode'].copy()
    # merge data-frames
    final_data_df = data_df.merge(geocode_df, on="site_name", how="left")
    # add a column for DarkSky certification
    if meas_type in ['clear_nights_brightness', 'cloudy_nights_brightness']:
        final_data_df['DarkSkyCertified'] = 'NO'
        final_data_df.loc[final_data_df['median_brightness_mag_arcsec2'] > 21.2, 'DarkSkyCertified'] = 'YES'

    
    # Create Oregon map using custom function based on Folium
    cmap = create_oregon_map(
        sites_df=final_data_df,
        main_col=meas_type_config['main_col_'],
        legend_order=meas_type_config['legend_order']
    )

    # For Dash, we convert the Folium map to HTML
    map_fig = get_folium_html(cmap)

    # Create ranking chart using custom function based on Plotly
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
    scatterplot_tuple = None
    if meas_type != "% clear nights":
        scatter_title = meas_type_config['scatter_title']
        fig_scatter_style = {'display': 'block'}
        fig_scatter = create_interactive_2d_plot(
            df=final_data_df,
            x_col=meas_type_config['scatter_x'],
            y_col=meas_type_config['scatter_y'],
            vline=meas_type_config['vline']
        )
    else:
        scatter_title = ""
        fig_scatter = go.Figure()
        fig_scatter_style = {'display': 'none'}
    
    return map_fig, meas_type_config['legend_str'], fig_bar, fig_bar2, fig_scatter, fig_scatter_style, scatter_title


# Run the Dash app when the script is executed directly from the command line
if __name__ == "__main__":
    # Start the server
    app.run(debug=True)