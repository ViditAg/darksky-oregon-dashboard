# dash_app/app.py
"""
Dash implementation of Oregon Dark Sky Dashboard
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
from shared.utils.visualizations import (
    create_interactive_2d_plot,
    create_oregon_map_plotly,
    create_ranking_chart
)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__, 
    title="Oregon Dark Sky Dashboard - Dash",
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# Use data saved in shared directory
processor = OregonSQMProcessor(data_dir=project_root / "shared/data")

# here we define the custom CSS styles for various DASH components
custom_styles = {
    'header': {
        'backgroundColor': "white",
        'color': 'white',
        'padding': '10px',
        'marginBottom': '5px',
        'borderRadius': '8px'
    },
    'control_panel': {
        'backgroundColor': '#f0f8ff',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px',
        'border': '1px solid #f0f8ff'
    },
    'help_text': {
        'backgroundColor': 'white',
        'padding': '5px',
        'borderRadius': '8px',
        'border': '2px solid #f0f8ff',
        'textAlign': 'left',
        'marginBottom': '0px'
    }
}

# Header component definition
header_component = html.Div(
    [
        html.Div(
            [
                html.Img(
                    src="/assets/DarkSky_logo.png",
                    style={
                        "height": "60px",
                        "verticalAlign": "middle"
                    }
                ),
                html.Span(
                    "DarkSky Oregon - Night Sky Brightness",
                    style={
                        "fontSize": "2em",
                        "marginLeft": "20px",
                        "verticalAlign": "middle",
                        'backgroundColor': "#1e1e3f", # Header background color
                        "border":  "#1e1e3f",  # Add border
                        "color": "white",
                        "padding": "10px",           # Add padding inside border
                        "borderRadius": "8px"        # Rounded corners
                    }
                )
            ], style={
                "display": "flex",
                "alignItems": "center",
                "padding": "20px 0"
                }
        ),
        html.P(
                [
                    html.A(
                        "DarkSky Oregon",
                        href="https://www.darkskyoregon.org/",
                        target="_blank",
                        style={"color": "blue", "textDecoration": "underline"}
                    ),
                    " has established a network of continuously recording Sky Quality Meters (SQMs) in Oregon to measure the brightness of our night skies at the zenith. This dashboard shows results from our ",
                    html.A(
                        "latest report (Edition #9, 2024)",
                        href="https://static1.squarespace.com/static/64325bb7c8993f109f0e62cb/t/679c8b55f32ba64b8739b9c2/1738312560582/DarkSky_Oregon_SQM_Network_TechnicalReport_Edition_09_v3_cmpress.pdf",
                        target="_blank",
                        style={"color": "blue", "textDecoration": "underline"}
                    )
                ],
                style={"color": "black"}
        )
    ],
    style=custom_styles['header']
)

# Question component definition
question_component = dbc.Col(
    [
        html.Div(
            [
                html.Label(
                    "Select a question?",
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
            style=custom_styles['control_panel']
        )
    ],
    xs=12, # here we set xs to 12 so it takes full width on extra small devices
    md=6  #  here we set md to 6 so it takes 6/12 width on medium and larger devices
)


help_text_component = dbc.Col(
    [
        html.Div(id="help-text", className="small", style=custom_styles['help_text'])
    ],
    xs=12, # here we set xs to 12 so it takes full width on extra small devices
    md=6  # here we set md to 6 so it takes 6/12 width on medium and larger devices
)


map_component = dbc.Col(
    [
        html.Div(
            id='map-chart-title',
            style={'maxWidth': '600px', 'margin': '0 auto'},
            className="h5 mb-1" # margin-top for spacing
        ),
        html.Div(
            id='map-chart-text',
            className="small" # margin-top for spacing
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
    xs=12, # here we set xs to 12 so it takes full width on extra small devices
    md=4 # here we set md to 4 so it takes 4/12 width on medium and larger devices
)


bar_component = dbc.Col(
    [
        html.Div(
            id='bar-chart-title',
            style={'maxWidth': '600px', 'margin': '0 auto'},
            className="h5 mb-1" # margin-top for spacing
        ),
        html.Div(
            id='bar-chart-text',
            className="small" # margin-top for spacing
        ),
        dcc.Graph(
            id='bar-chart',
            style={'height': '900px', 'maxWidth': '600px', 'margin': '0 auto'},
            config={'displayModeBar': True, 'displaylogo': True}
            ),
    ],
    xs=12, # here we set xs to 12 so it takes full width on extra small devices
    md=4 # here we set md to 4 so it takes 4/12 width on medium and larger devices
)


scatter_component = dbc.Col(
    [
        html.Div(
            id="scatter-plot-div",
            children=[
                html.Div(
                    id="scatter-plot-title",
                    className="h5 mb-1",
                    style={'maxWidth': '300px', 'margin': '0 auto'}
                ),
                dcc.Graph(
                    id='scatter-plot',
                    style={'height': '300px', 'maxWidth': '350px', 'margin': '0 auto'},
                    config={'displayModeBar': True, 'displaylogo': True}
                )
            ]
        ),
        
    ],
    xs=12, # here we set xs to 12 so it takes full width on extra small devices
    md=4 # here we set md to 4 so it takes 4/12 width on medium and larger devices
)


footer_component = html.Div(
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
        header_component,
        
        # Control Panel and Help Text
        dbc.Row(
            [
                question_component,
                help_text_component
            ],
            className="mb-4"
        ),
        
        
        # Main visualization columns
        dbc.Row(
            [
                map_component,                
                bar_component,
                scatter_component,
            ],
            className="mb-4"
        ),

        # Footer
        html.Hr(), # Divider Horizontal line
        # Footer content
        footer_component
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


def get_site_info_text(
    df, meas_type, clicked_sites
):
    """
    Generate markdown text for the clicked site(s) based on measurement type.
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
                "{x_bright:.2f}-times brighter than the darkest Night Sky".format(
                    x_bright=row['x_brighter_than_darkest_night_sky']
                ),
                "Bortle level: {bortle}".format(
                    bortle=row['bortle_sky_level']
                ),
                "Median Night Sky Brightness: {mag_arcsec2:.2f} mag/arcsec²".format(
                    mag_arcsec2=row['median_brightness_mag_arcsec2']
                ),
                "Flux Ratio: {flux_ratio:.2f}".format(
                    flux_ratio=row['median_linear_scale_flux_ratio']
                )
            ]: markdown_text.append(html.P(str_, style={"marginBottom": "0px"}))
        
        elif meas_type == "cloudy_nights_brightness":
            markdown_text.append(html.P(""))
            for str_ in [
                "{x_bright:.2f}-times brighter than the darkest Night Sky".format(
                    x_bright=row['x_brighter_than_darkest_night_sky']
                ),
                "Median Night Sky Brightness: {mag_arcsec2:.2f} mag/arcsec²".format(
                    mag_arcsec2=row['median_brightness_mag_arcsec2']
                ),
                "Flux Ratio: {flux_ratio:.2f}".format(
                    flux_ratio=row['median_linear_scale_flux_ratio']
                )
            ]: markdown_text.append(html.P(str_, style={"marginBottom": "0px"}))
            
        elif meas_type == "long_term_trends":
            markdown_text.append(html.P(""))
            for str_ in [
                "Rate of Change in Night Sky Brightness compared to a certified Dark Sky Park: {rate_of_change:.2f}".format(
                    rate_of_change=row['Rate_of_Change_vs_Prineville_Reservoir_State_Park']
                    ),
                "Trendline Slope: {regression_slope_x10000:.2f}".format(
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
                "Ratio Index: {ratio_index:.2f}".format(
                    ratio_index=row['ratio_index']
                ),
                "Difference Index: {difference_index:.2f}".format(
                    difference_index=row['difference_index_mag_arcsec2'])
            ]: markdown_text.append(html.P(str_, style={"marginBottom": "0px"}))
            
        elif meas_type == "% clear nights":
            markdown_text.append(html.P(""))
            for str_ in [
                "Percentage of Clear (no clouds) nights: {clear_nights:.2f}%".format(
                    clear_nights=row['percent_clear_night_samples_all_months']
                )
            ]: markdown_text.append(html.P(str_, style={"marginBottom": "0px"}))
        
    return markdown_text    
    

def get_help_text(meas_type):
    """
    Generate help text based on measurement type.
    """
    help_text_str_list = [
        """Click on a 'marker' or a 'bar' to select a SQM site. The site will be highlighted on the graphics below and 
            it's corresponding measurements will be shown. Also, note how the highlighted site ranks compared to other sites.""",
        """Use the buttons on the top-right corner of each the graphics to zoom, pan, reset or save chart as an image.""",
        """The dashboard will remember your site selection and map view across different questions."""
    ]
    help_text_component_list = [html.Li(t_) for t_ in help_text_str_list]
    
    if meas_type == "clear_nights_brightness":
        str_list = [
        "The darkest Night Sky Location for clear nights based on current data is Hart Mountain.",
        """Bortle scale is a visual measure of night sky brightness,
            ranging from 1 for pristine night skies to 9 at light polluted
            urban night skies""",
        """Median Night Sky Brightness shown in a log scale of Magnitudes/Arcsecond
            squared is a common measure used in astronomy""",
        "Flux Ratio shows a linear scale of night sky brightness.",
        
        ]
    
    elif meas_type == "cloudy_nights_brightness":
       str_list = [
           "The darkest Night Sky Location for cloudy nights based on current data is Crater Lake National Park",
            """Cloudy nights magnify the night sky brightness contrast 
            between pristine and light polluted sites. Cloudy nights at 
            pristine night sky locations are exceedingly dark and are a natural 
            part of the wild ecosystem there.""",
            """Median Night Sky Brightness is in a log scale of Magnitudes/Arcsecond
                squared, a common measure used in astronomy""",
            "Flux Ratio shows a linear scale of night sky brightness.",
        ]
    
    elif meas_type == "long_term_trends":
        str_list = [
            """Only the sites with at least 2 years of data are included to calculate the long-term trends.""",
            """Rate of Change in Night Sky Brightness is compared to Prineville Reservoir State Park which is a certified Dark Sky Park.""",
            """Trendline Slope is calculated from regression fit of change over time scaled by a factor of 10000""",
        ]
        
    elif meas_type == "milky_way_visibility":
        str_list = [
            """Ratio Index: Ratio of Night Sky Brightness between Milky Way and nearby sky""",
            """Difference Index: Difference in Night Sky Brightness between Milky Way and nearby sky"""
        ]
        
    elif meas_type == "% clear nights":
        str_list = [
            """Percentage of Clear nights mean the nights without any clouds in the night sky""",
            """Measurement at each site is averaged over all months of the year"""
        ]
    
    metric_component_list = [html.Li(t_) for t_ in str_list]

    return html.Div(
        [
            html.B("Help guide"),
            html.Ul(help_text_component_list),
            html.B("Measurements explained: "),
            html.Ul(metric_component_list)
        ]
    )


# Callbacks for interactivity (mirroring Streamlit logic)
@app.callback(
    [
        Output('oregon-map', 'figure'),
        Output('site-info-div', 'children'),
        Output("map-chart-title", "children"),
        Output("map-chart-text", 'children'),
        Output('bar-chart', 'figure'),
        Output('bar-chart-title', 'children'),
        Output('bar-chart-text', 'children'),
        Output('scatter-plot-div', 'style'),
        Output('scatter-plot', 'figure'),
        Output('scatter-plot-title', 'children'),
        Output("help-text", "children")
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
    
    ### Load data processed for the selected measurement type
    final_data_df = processor.load_processed_data(
        data_key=meas_type_configs['data_key'],
        bar_chart_col=meas_type_configs['bar_chart']['bar_chart_y_col']
        )
    
    # Generate help text based on measurement type
    help_text = get_help_text(meas_type=meas_type)
    
    # Create map graphics
    ## Create map title
    map_chart_title = "SQM measurement site map"
    ## Text to explain map markers
    map_chart_text = "Note: all locations shown in the map below are approximated for privacy."
    ## Determine color column for map based on measurement type
    if meas_type in ["clear_nights_brightness", "cloudy_nights_brightness"]:
        color_col = meas_type_configs['scatter_plot']['scatter_x_col']
    else:
        color_col = meas_type_configs['bar_chart']['bar_chart_y_col']
    # call function to generate `go.Figure` map object
    cmap = create_oregon_map_plotly(
        sites_df=final_data_df,
        color_col=color_col,
        zoom=map_zoom,
        map_center=map_center,
        highlight_sites=clicked_sites
        )
    
    # Generate site info text if a site is clicked
    if clicked_sites is None:
        site_info_text = "" # No site selected
    else:    
        site_info_text = get_site_info_text(
            df=final_data_df,
            meas_type=meas_type,
            clicked_sites=clicked_sites
        )
    
    # Create bar chart graphics
    ## bar chart title
    bar_chart_title = meas_type_configs['bar_chart']['bar_chart_title']
    ## Text to explain x-axis scale
    bar_chart_text = "Note: the x-axis is shown in {0} scale".format(
        meas_type_configs['bar_chart']['bar_chart_yicks']['tickmode']
        )
    ## Create ranking chart using custom function based on Plotly
    fig_bar = create_ranking_chart(
        sites_df=final_data_df,
        configs=meas_type_configs['bar_chart'],
        clicked_sites=clicked_sites
    )    
    
    # Create scatter plot if applicable
    if meas_type in ["clear_nights_brightness", "cloudy_nights_brightness"]:
        # Show scatter plot title
        scatter_plot_title = meas_type_configs['scatter_plot']['scatter_plot_title']
        
        # a style to show the scatter plot div when applicable
        fig_scatter_style = {'display': 'block'}
        
        vline_ = 21.2 if meas_type == "clear_nights_brightness" else None
        
        # Create scatter plot using custom function based on Plotly
        fig_scatter = create_interactive_2d_plot(
            df=final_data_df,
            configs=meas_type_configs['scatter_plot'],
            clicked_sites=clicked_sites,
            vline=vline_
        )
        
    else:
        # Hide scatter plot title
        scatter_plot_title = ""
        
        # Hide scatter plot div
        fig_scatter_style = {'display': 'none'}

        # Create empty scatter plot
        fig_scatter = go.Figure()
    
    return (
        cmap,
        site_info_text,
        map_chart_title,
        map_chart_text,
        fig_bar, 
        bar_chart_title,
        bar_chart_text,
        fig_scatter_style,
        fig_scatter,
        scatter_plot_title,
        help_text
    )


# Run the Dash app when the script is executed directly from the command line
if __name__ == "__main__":
    # Start the server
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8050
    )