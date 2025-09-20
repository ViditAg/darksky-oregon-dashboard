# dash_app/app.py
"""
Complete Dash implementation of Oregon Dark Sky Dashboard
"""
import sys
import time
from pathlib import Path
import dash
from dash import State, dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


# local import
# Add project root to path so 'shared' package is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from shared.utils.configs import get_meas_type_config, meas_type_dict
from shared.utils.data_processing import OregonSQMProcessor
from shared.utils.visualizations import create_interactive_2d_plot, create_oregon_map_plotly, create_ranking_chart

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
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
        # dcc.Store is used to store intermediate values that can be shared between callbacks
        # Initialize map zoom parameter with default value 6
        dcc.Store(
            id='map-zoom-store', # component id
            data=5 # property data (initial zoom level)
            ),
        # Initialize map center parameter with default Oregon center
        dcc.Store(
            id='map-center-store', # component id
            data=[44.0, -121.0] # property data (initial center coordinates)
        ),
        # Initialize clicked sites parameter with None
        dcc.Store(
            id='clicked-sites-store', # component id
            data=None # property data (initially no site clicked)
        ),
        
        # Header
        html.Div(
            [
                html.H1(
                    "Dark Sky Oregon - Night Sky Brightness at the Zenith",
                    className="text-center mb-2"
                ),
                html.P(
                        [
                            
                            "Dark Sky Oregon ",
                            html.A(
                                "(see website)",
                                href="https://www.darkskyoregon.org/",
                                target="_blank",
                                style={"color": "cyan", "textDecoration": "underline"}
                            ),
                            " has established a network of continuously recording Sky Quality Meters (SQMs) in Oregon to measure the brightness of our night skies, due to both man-made artificial light and natural light. Here we show results from their ",
                            html.A(
                                "latest report (Edition #9, 2024)",
                                href="https://static1.squarespace.com/static/64325bb7c8993f109f0e62cb/t/679c8b55f32ba64b8739b9c2/1738312560582/DarkSky_Oregon_SQM_Network_TechnicalReport_Edition_09_v3_cmpress.pdf",
                                target="_blank",
                                style={"color": "cyan", "textDecoration": "underline"}
                            )
                        ],
                        style={"color": "white"}
                )
            ],
            style=custom_styles['header']
        ),
        

        # Main visualization columns
        dbc.Row(
            [
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
                                ),
                                html.Button(
                                    "Refresh",
                                    id="refresh-btn",
                                    n_clicks=0, # initial click count
                                    className="btn btn-primary mb-3" # Bootstrap button classes
                                )
                            ],
                            style={**custom_styles['control_panel'], 'width': '100%'}
                        )
                    ],
                    width=2
                ),
                # Map column
                dbc.Col(
                    [
                        html.H5(
                            "SQM measurement site map",
                            className="mb-3"
                        ),
                        html.P(
                            """
                            Click on a SQM site on the map to see its night sky brightness measurement
                             and how it ranks compared to other sites. While selecting the next site
                             you may need to click the site again for the app to re-load. You can also
                             zoom/pan the map and the app will remember your view across different 
                             questions."""
                             ),
                        dcc.Graph(
                            id='oregon-map',
                            style={'height': '400px', 'width': '100%'}
                        ),
                        html.Div(
                            id='site-info-div',
                            className="mt-1" # margin-top for spacing
                        )
                    ],
                    #width=4
                ),
                
                # Bar chart column
                dbc.Col(
                    [
                        html.Div(
                            id='bar-chart-title',
                            style={'maxWidth': '600px', 'margin': '0 auto'},
                            className="h5 mb-3" # margin-top for spacing
                        ),
                        html.Div(
                            id='bar-chart-text',
                            style={'maxWidth': '600px', 'margin': '0 auto'},
                            className="mt-1" # margin-top for spacing
                        ),
                        dcc.Graph(
                            id='bar-chart',
                            style={'height': '1000px', 'maxWidth': '600px', 'margin': '0 auto'},
                            config={'displayModeBar': True}
                            ),
                    ],
                    #width=3
                ),
                
                # Scatter plot column
                dbc.Col(
                    [
                        html.Div(
                            id="scatter-plot-div",
                            children=[
                                html.Div(
                                    id="scatter-plot-title",
                                    className="h5 text-center mb-3",
                                    style={'maxWidth': '300px', 'margin': '0 auto'}
                                ),
                                html.P(
                                    """
                                    Hover over data-points to see the values. 
                                    Use the buttons just like the ranking chart.
                                    """,
                                    style={'maxWidth': '300px', 'margin': '0 auto'}
                                ),
                                dcc.Graph(
                                    id='scatter-plot',
                                    style={'height': '300px', 'maxWidth': '350px', 'margin': '0 auto'},
                                    config={'displayModeBar': True}
                                )
                            ]
                        )
                    ],
                    #width=2
                )
            ],
            className="mb-4"
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
                    " Repository: ",
                    html.A(
                        "https://github.com/ViditAg/darksky-oregon-dashboard",
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
    fluid=True  # <-- this enables full-width layout
)


@app.callback(
    Output('map-zoom-store', 'data'),
    Output('map-center-store', 'data'),
    [
        Input('oregon-map', 'relayoutData'),
        Input('refresh-btn', 'n_clicks')
    ],
    [
        State('map-zoom-store', 'data'),
        State('map-center-store', 'data')
    ]
)
def update_zoom_and_center(relayoutData, refresh_click, current_zoom, current_center):
    ctx = callback_context
    if not ctx.triggered:
        return current_zoom, current_center
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'oregon-map' and relayoutData:
        zoom = relayoutData['mapbox.zoom'] if 'mapbox.zoom' in relayoutData and relayoutData['mapbox.zoom'] is not None else current_zoom
        center = [relayoutData['mapbox.center']['lat'], relayoutData['mapbox.center']['lon']] if 'mapbox.center' in relayoutData and relayoutData['mapbox.center'] is not None else current_center
        
        return zoom, center
    
    elif trigger_id == 'refresh-btn':
        return 5, [44.0, -121.0]
    
    return current_zoom, current_center


@app.callback(
    Output('clicked-sites-store', 'data'),
    Output('oregon-map', 'clickData'),
    Output('bar-chart', 'clickData'),
    Output('scatter-plot', 'clickData'),
    [
        Input('oregon-map', 'clickData'),
        Input('bar-chart', 'clickData'),
        Input('scatter-plot', 'clickData'),
        Input('refresh-btn', 'n_clicks')
    ],
    [State('clicked-sites-store', 'data')]
)
def update_clicked_sites(map_click, bar_click, scatter_click, refresh_click, current_clicked):
    ctx = callback_context
    if not ctx.triggered:
        return current_clicked,  None, None, None
    

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'oregon-map' and map_click:
        return map_click['points'][0]['customdata'], None, None, None
    
    elif trigger_id == 'bar-chart' and bar_click:
        return [bar_click['points'][0]['y']], None, None, None
    elif trigger_id == 'scatter-plot' and scatter_click:
        return [scatter_click['points'][0]['hovertext']], None, None, None
    elif trigger_id == 'refresh-btn':
        return None, None, None, None
    
    return current_clicked, None, None, None


def get_site_info_text(df, meas_type, clicked_sites):
    """
    """
    site_row = df[df["site_name"].isin(clicked_sites)]
    markdown_text = []
    for i, row in site_row.iterrows():
        markdown_text.append(html.B("{0}".format(row["site_name"])))
        
        if meas_type in ["", "clear_nights_brightness"]:
            if row['DarkSkyCertified'] == 'YES':
                markdown_text.append(" - Dark Sky Certified")
            if (row['DarkSkyQualified'] == 'YES') and (row['DarkSkyCertified'] == 'NO'):
                markdown_text.append(" - Dark Sky Qualified")
            
            markdown_text.append(html.P(""))
            for str_ in [
                "{x_bright:.2f}-times brighter than the darkest Night Sky (Hart Mountain)".format(
                    x_bright=row['x_brighter_than_darkest_night_sky']
                ),
                "Bortle Scale (1: Excellent dark sky - 9:  Inner-city sky): {bortle}".format(
                    bortle=row['bortle_sky_level']
                ),
                "Median Night Sky Brightness (log scale): {mag_arcsec2:.2f} mag/arcsec²".format(
                    mag_arcsec2=row['median_brightness_mag_arcsec2']
                ),
                "Flux Ratio (Night Sky Brightness converted to a linear scale): = {flux_ratio:.2f}".format(
                    flux_ratio=row['median_linear_scale_flux_ratio']
                )
            ]: markdown_text.append(html.P(str_, style={"marginBottom": "0px"}))
        
        elif meas_type == "cloudy_nights_brightness":
            markdown_text.append(html.P(""))
            for str_ in [
                "{x_bright:.2f}-times brighter than the darkest Night Sky (Crater Lake)".format(
                    x_bright=row['x_brighter_than_darkest_night_sky']
                ),
                "Median Night Sky Brightness (log scale): {mag_arcsec2:.2f} mag/arcsec²".format(
                    mag_arcsec2=row['median_brightness_mag_arcsec2']
                ),
                "Flux Ratio (Night Sky Brightness converted to a linear scale): = {flux_ratio:.2f}".format(
                    flux_ratio=row['median_linear_scale_flux_ratio']
                )
            ]: markdown_text.append(html.P(str_, style={"marginBottom": "0px"}))
            
        elif meas_type == "long_term_trends":
            markdown_text.append(html.P(""))
            for str_ in [
                "Rate of Change in Night Sky Brightness vs Prineville Reservoir State Park - a certified Dark Sky Park: {rate_of_change:.2f}".format(
                    rate_of_change=row['Rate_of_Change_vs_Prineville_Reservoir_State_Park']
                    ),
                "Trendline Slope (regression fit of change over time scaled by a factor of 10000): {regression_slope_x10000:.2f}".format(
                    regression_slope_x10000=row['Regression_Line_Slope_x_10000']
                    ),
                "Percentage Change in Night Sky Brightness per year: {percent_change:.2f}%".format(
                    percent_change=row['Percent_Change_per_year']
                    ),
                "Number of Years of Data: {num_years}".format(
                    num_years=row['Number_of_Years_of_Data']
                    )
            ]: markdown_text.append(html.P(str_, style={"marginBottom": "0px"}))
            
        elif meas_type == "milky_way_visibility":
            markdown_text.append(html.P(""))
            for str_ in [
                "Ratio Index (ratio of brightness of Milky Way to the surrounding sky): {ratio_index:.2f}".format(
                    ratio_index=row['ratio_index']
                ),
                "Difference Index (difference in brightness between Milky Way and surrounding sky): {difference_index:.2f}".format(
                    difference_index=row['difference_index_mag_arcsec2'])
            ]: markdown_text.append(html.P(str_, style={"marginBottom": "0px"}))
            
        elif meas_type == "% clear nights":
            markdown_text.append(html.P(""))
            for str_ in [
                "Percentage of Clear (no clouds) nights averaged over all months in the year: {clear_nights:.2f}%".format(
                    clear_nights=row['percent_clear_night_samples_all_months']
                )
            ]: markdown_text.append(html.P(str_, style={"marginBottom": "0px"}))
        
        markdown_text.append(
            html.P(
                "Site Elevation: {elevation:.0f} meters".format(elevation=row['Elevation_in_meters'])
            )
        )
    return markdown_text    
    


# Callbacks for interactivity (mirroring Streamlit logic)
@app.callback(
    [
        Output('oregon-map', 'figure'),
        Output('site-info-div', 'children'),
        Output('bar-chart', 'figure'),
        Output('bar-chart-title', 'children'),
        Output('bar-chart-text', 'children'),
        Output('scatter-plot-div', 'style'),
        Output('scatter-plot', 'figure'),
        Output('scatter-plot-title', 'children')
    ],
    [
        Input('meas-type-radio', 'value'),
        State('map-zoom-store', 'data'),
        State('map-center-store', 'data'),
        Input('clicked-sites-store', 'data')
    ]
)
def update_dashboard(
    meas_type,
    map_zoom,
    map_center,
    clicked_sites
):
    """
    Update map and ranking chart based on selected measurement type

    Parameters:
    - meas_type: The selected measurement type

    Returns:
    - A tuple containing the updated map figure and ranking chart figure
    """
    # data-table based on selected measurement type
    meas_type_configs = get_meas_type_config(meas_type)

    # Initialize processor and load data
    processor = OregonSQMProcessor(data_dir=project_root / "shared" / "data")
    # Load raw data
    final_data_df = processor.load_processed_data(
        data_key=meas_type_configs['data_key'],
        bar_chart_col=meas_type_configs['bar_chart_y_col']
        )
    
    if meas_type == "clear_nights_brightness":
        color_col = meas_type_configs['scatter_x_col']
    else:
        color_col = meas_type_configs['bar_chart_y_col']
    
    # Create Oregon map
    cmap = create_oregon_map_plotly(
        sites_df=final_data_df,
        color_col=color_col,
        zoom=map_zoom,
        map_center=map_center,
        highlight_sites=clicked_sites
        )

    if clicked_sites is None:
        site_info_text = ""
    else:    
        site_info_text = get_site_info_text(
            df=final_data_df,
            meas_type=meas_type,
            clicked_sites=clicked_sites
        )
    
    # Create ranking chart using custom function based on Plotly
    fig_bar = create_ranking_chart(
            sites_df=final_data_df,
            y_col=meas_type_configs['bar_chart_y_col'],
            y_label=meas_type_configs['bar_chart_y_label'],
            clicked_sites=clicked_sites
        )

    bar_chart_text = "Hover over bars to see {0}. Use the buttons on the top-right of the chart to zoom, pan, reset or save chart as an image".format(
        meas_type_configs['bar_chart_text']
        )
    # Create scatter plot if applicable
    if meas_type != "% clear nights":
        # a style to show the scatter plot div when applicable
        fig_scatter_style = {'display': 'block'}
        # Create scatter plot using custom function based on Plotly
        fig_scatter = create_interactive_2d_plot(
                df=final_data_df,
                x_col=meas_type_configs['scatter_x_col'],
                y_col=meas_type_configs['scatter_y_col'],
                x_label=meas_type_configs['scatter_x_label'],
                y_label=meas_type_configs['scatter_y_label'],
                vline=meas_type_configs['vline'],
                clicked_sites=clicked_sites
            )
        
    else:
        # Create empty scatter plot
        fig_scatter = go.Figure()
        # Hide scatter plot div
        fig_scatter_style = {'display': 'none'}
    
    return (
        cmap,
        site_info_text,
        fig_bar, 
        meas_type_configs['bar_chart_title'], 
        bar_chart_text,
        fig_scatter_style,
        fig_scatter,
        meas_type_configs['scatter_plot_title']
    )


# Run the Dash app when the script is executed directly from the command line
if __name__ == "__main__":
    # Start the server
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8050
    )