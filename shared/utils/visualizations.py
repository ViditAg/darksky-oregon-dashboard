# functions to define visualizations

# importing neccessary libraries
import pandas as pd
import folium
import plotly.graph_objects as go
from streamlit import metric


#### Ranking Chart Visualization ####
def create_ranking_chart(
	sites_df: pd.DataFrame,
	y_col: str,
	title: str,
	key: str = "top_20"
) -> go.Figure:
	"""
	Create interactive Plotly bar chart for site rankings.

	Parameters
	----------
	sites_df : pd.DataFrame
		DataFrame containing site data.
	y_col : str
		Column name to rank sites by for e.g. 'median_brightness', 'x_brighter_than_darkest_night_sky'.

	Returns
	-------
	go.Figure
		Plotly Figure object for the ranking bar chart.
	"""
	# Prepare and sort data
	chart_data = _prepare_chart_data(sites_df, y_col)
	# Limit to top 30 by metric (ascending)
	if key == "bottom_20":
		chart_data_cut = chart_data.sort_values(y_col, ascending=True).head(20)
	else:
		chart_data_cut = chart_data.sort_values(y_col, ascending=True).tail(20)
	
	if y_col == "ratio_index":
		xlim_ = [0.9, chart_data[y_col].max()]
	else:
		xlim_ = [0, chart_data[y_col].max()]
	
	# Create the bar chart
	fig = _build_ranking_bar_chart(
		chart_data_cut, y_col, title=title, xlim=xlim_
	)
	return fig

def _prepare_chart_data(
		sites_df: pd.DataFrame,
		y_col: str
	) -> pd.DataFrame:
	"""Filter and sort the DataFrame for charting."""
	# Drop rows with missing values for the metric or site name
	chart_data = sites_df.dropna(subset=[y_col, 'site_name']).copy()

	return chart_data.sort_values(y_col, ascending=True)


def _build_ranking_bar_chart(
	chart_data: pd.DataFrame,
	y_col: str,
	title: str,
	xlim: tuple
) -> go.Figure:
	"""Build the Plotly bar chart for site rankings."""
	# Create the bar chart
	fig = go.Figure(
		data=go.Bar(
			y=chart_data['site_name'],
			x=chart_data[y_col],
			orientation='h',
			hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<extra></extra>'
		)
	)
	fig.update_layout(
		title=title,
		xaxis_range=xlim,
		xaxis_side="top",
		height=max(400, len(chart_data) * 20),
		margin=dict(l=100, r=0, t=0, b=50),
		showlegend=False,
		xaxis=dict(title_font=dict(size=18), tickfont=dict(size=10)),
		yaxis=dict(title_font=dict(size=18), tickfont=dict(size=10))
	)
	
	return fig

	#### Generic Interactive 2D Scatter Plot ####
	

def create_interactive_2d_plot(
	df: pd.DataFrame,
	x_col: str,
	y_col: str,
	hover_cols: list[str] | None = None,
	vline: None = None,
) -> go.Figure:
	"""
	Create an interactive 2D scatter plot with Plotly.

	Parameters
	----------
	df : pd.DataFrame
		Input DataFrame.
	x_col : str
		Column for x-axis.
	y_col : str
		Column for y-axis.
	hover_cols : list[str], optional
		Additional columns to include in hover.
	vline : float, optional
		Vertical line to add at a specific x-value. Default 21.2.

	Returns
	-------
	go.Figure
		Plotly scatter figure.
	"""
	import plotly.express as px

	if x_col not in df.columns or y_col not in df.columns:
		raise ValueError("x_col or y_col not found in DataFrame")

	hover_data = ['site_name',x_col, y_col]

	fig = px.scatter(
		df,
		x=x_col,
		y=y_col,
		hover_data=hover_data,
	)

	# Set a small default height and width for the scatter plot
	fig.update_layout(
		margin=dict(l=60, r=30, t=60, b=60),
		height=400,
		width=400,
		xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
		yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14))
	)

	if vline:
		fig.add_shape(
			type="line",
			x0=vline,
			x1=vline,
			y0=fig.layout.yaxis.range[0] if fig.layout.yaxis.range else min(df[y_col]),
			y1=fig.layout.yaxis.range[1] if fig.layout.yaxis.range else max(df[y_col]),
			xref="x", yref="y", line=dict(color="black", dash="dash")
		)
		# Add annotation text at the top of the vline
		fig.add_annotation(
			x=vline,
			y=fig.layout.yaxis.range[1] if fig.layout.yaxis.range else max(df[y_col]),
			text="Threshold for Dark-Sky Places Certification",
			showarrow=False,
			yshift=0,
			font=dict(size=12, color="black"),
			xanchor="center"
		)
	return fig


def figure_to_dash_component(
	fig: go.Figure,
	graph_id: str = "interactive-2d-plot",
	**graph_kwargs
):
	"""
	Return a Dash dcc.Graph for the given figure.

	Parameters
	----------
	fig : go.Figure
		Plotly figure.
	graph_id : str, optional
		Component id. Default 'interactive-2d-plot'.
	graph_kwargs : dict
		Additional kwargs passed to dcc.Graph.

	Returns
	-------
	dcc.Graph
		Dash graph component.

	Raises
	------
	ImportError
		If Dash is not installed.
	"""
	if dcc is None:
		raise ImportError("Dash is not installed. Install with 'pip install dash'.")
	return dcc.Graph(id=graph_id, figure=fig, **graph_kwargs)

def figure_html_for_flask(
	fig: go.Figure,
	full_page: bool = False,
	title: str = "Interactive Plot"
) -> str:
	"""
	Return HTML snippet or full page HTML for embedding a Plotly figure in Flask.

	Parameters
	----------
	fig : go.Figure
		Plotly figure.
	full_page : bool, optional
		Wrap in full HTML document. Default False.
	title : str, optional
		Page title if full_page True.

	Returns
	-------
	str
		HTML string.
	"""
	html_fragment = get_plotly_html(fig)
	if not full_page:
		return html_fragment
	return f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title></head><body>{html_fragment}</body></html>"

######## Oregon Map Visualization ########

def create_oregon_map(
	sites_df: pd.DataFrame,
	main_col: str,
	legend_order: list[str]
) -> folium.Map:
	"""
	Create interactive Folium map for Oregon sites. Usable in Streamlit and Jupyter.

	Parameters
	----------
	sites_df : pd.DataFrame
		DataFrame containing site data.
	main_col : str
		Column name for main data values.
	legend_order : list[str]
		Order of legend categories.
	Returns
	-------
	folium.Map
		Folium Map object with site markers.
	"""
	# Create base map
	m = folium.Map(
		location=[44.0, -121.0],
		zoom_start=6,
		tiles='OpenStreetMap'
		)
	# get values to set color for markers on the map
	th_up = sites_df[main_col].quantile(0.75)
	th_down = sites_df[main_col].quantile(0.25)
	# Add site markers
	for i, row in sites_df.iterrows():
		if pd.isna(row[main_col]): color_ = 'gray'
		elif row[main_col] >= th_up: color_ = legend_order[2]
		elif row[main_col] >= th_down: color_ = legend_order[1]
		else: color_ = legend_order[0]
		_add_site_marker(
			m, row, main_col=main_col, color_=color_
		)

	return m

def _add_site_marker(
	m: folium.Map,
	row: pd.Series,
	main_col: str,
	color_: str
):
	"""Add a CircleMarker for a site to the map."""
	#get all columns from series and show the metrics in pop-up
	# use the main column as primary thing 

	popup_html_cols = [
		col for col in row.index.tolist() if col not in ['site_name', 'latitude', 'longitude']
		]
	popup_html = f"""
	<div style='width: 250px; font-size: 12px;'>
		<h4 style='font-size: 14px; margin: 0 0 4px 0;'>{row['site_name']}</h4>
	"""
	for col in popup_html_cols:
		popup_html += f"<p style='margin:0; padding:0;'><strong>{col}:</strong> {row[col]}</p>"

	popup_html += """</div>"""

	folium.CircleMarker(
		location=[row['latitude'], row['longitude']],
		radius=7,
		popup=folium.Popup(popup_html, max_width=300),
		fillColor=color_,
		color=color_,  # set edge color same as fill
		weight=0,      # no border
		fillOpacity=0.8,
		tooltip=f"{row['site_name']}: {row[main_col] :.2f}"
	).add_to(m)
	

def get_folium_html(
	map_obj: folium.Map,
	width: str = "100%",
	height: str = "500px"
) -> str:
	"""
	Return HTML representation of a Folium map for Flask or Dash.

	Parameters
	----------
	map_obj : folium.Map
		Folium map object.
	width : str, optional
		Width of the map in HTML/CSS units. Defaults to "100%".
	height : str, optional
		Height of the map in HTML/CSS units. Defaults to "500px".

	Returns
	-------
	str
		HTML string for embedding the map.
	"""
	html = map_obj._repr_html_()
	html = html.replace('width:100%;', f'width:{width};').replace('height:100%;', f'height:{height};')
	return html

def get_plotly_html(fig: go.Figure) -> str:
	"""
	Return HTML representation of a Plotly figure for Flask or other web frameworks.

	Parameters
	----------
	fig : go.Figure
		Plotly Figure object.

	Returns
	-------
	str
		HTML string for embedding the figure.
	"""
	return fig.to_html(full_html=False)

