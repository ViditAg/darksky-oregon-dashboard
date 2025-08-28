# importing neccessary libraries
import pandas as pd
import folium
import plotly.graph_objects as go
from streamlit import metric


#### Ranking Chart Visualization ####
def create_ranking_chart(
	sites_df: pd.DataFrame,
	y_col: str,
	hlines: list[float] = None,
	vlines: list[float] = None,
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
	# Assign colors for bars
	colors = _get_bar_colors(chart_data)
	# Create the bar chart
	fig = _build_ranking_bar_chart(chart_data, y_col, colors)
	# Add horizontal and vertical lines if specified
	if hlines:
		for y in hlines:
			fig.add_shape(
				type="line", x0=0, x1=1, y0=y, y1=y, xref="paper", yref="y", line=dict(color="red", dash="dash")
			)
	if vlines:
		for x in vlines:
			fig.add_shape(
				type="line", x0=x, x1=x, y0=0, y1=1, xref="x", yref="paper", line=dict(color="blue", dash="dot")
			)
	
	return fig

def _prepare_chart_data(sites_df: pd.DataFrame, y_col: str) -> pd.DataFrame:
	"""Filter and sort the DataFrame for charting."""
	# Drop rows with missing values for the metric or site name
	chart_data = sites_df.dropna(subset=[y_col, 'site_name']).copy()
	# Sort by metric (brightness is ascending, others descending)
	ascending = True if y_col == 'median_brightness_mag_arcsec2' else False
	return chart_data.sort_values(y_col, ascending=ascending)

def _get_bar_colors(chart_data: pd.DataFrame) -> list:
	"""Assign colors to bars based on dark sky status."""
	return [
		'darkgreen' if status != 'None' else 'lightblue'
		for status in chart_data.get('dark_sky_status', ['None'] * len(chart_data))
	]

def _build_ranking_bar_chart(
	chart_data: pd.DataFrame,
	y_col: str,
	colors: list,
) -> go.Figure:
	"""Build the Plotly bar chart for site rankings."""
	# Create the bar chart
	fig = go.Figure(
		data=go.Bar(
			y=chart_data['site_name'],
			x=chart_data[y_col],
			orientation='h',
			marker=dict(color=colors),
			text=chart_data[y_col].round(2),
			textposition='outside',
			hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<extra></extra>'
		)
	)
	fig.update_layout(
		title='Site-to-Site Comparison',
		xaxis_title=y_col,
		yaxis_title='Monitoring Site',
		height=max(400, len(chart_data) * 20),
		margin=dict(l=200, r=50, t=50, b=50),
		showlegend=False
	)
	
	return fig

	#### Generic Interactive 2D Scatter Plot ####
	
def create_interactive_2d_plot(
	df: pd.DataFrame,
	x_col: str,
	y_col: str,
	color_col: str | None = None,
	size_col: str | None = None,
	hover_cols: list[str] | None = None,
	title: str | None = None,
	log_x: bool = False,
	log_y: bool = False,
	hlines: list[float] = None,
	vlines: list[float] = None,
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
	color_col : str, optional
		Column for point color grouping.
	size_col : str, optional
		Column for point sizing.
	hover_cols : list[str], optional
		Additional columns to include in hover.
	title : str, optional
		Figure title (auto-generated if None).
	trendline : bool, optional
		Add OLS trendline. Default False.
	log_x : bool, optional
		Log scale for x-axis. Default False.
	log_y : bool, optional
		Log scale for y-axis. Default False.

	Returns
	-------
	go.Figure
		Plotly scatter figure.
	"""
	import plotly.express as px

	if x_col not in df.columns or y_col not in df.columns:
		raise ValueError("x_col or y_col not found in DataFrame")

	hover_data = [c for c in (hover_cols or []) if c in df.columns and c not in (x_col, y_col)]

	fig = px.scatter(
		df,
		x=x_col,
		y=y_col,
		color=color_col,
		size=size_col,
		hover_data=hover_data,
		title=title or f"{y_col} vs {x_col}",
		log_x=log_x,
		log_y=log_y,
	)

	fig.update_layout(
		margin=dict(l=60, r=30, t=60, b=60),
		legend_title=color_col if color_col else None,
	)
	# Add horizontal and vertical lines if specified
	if hlines:
		for y in hlines:
			fig.add_shape(type="line", x0=fig.layout.xaxis.range[0] if fig.layout.xaxis.range else min(df[x_col]),
						  x1=fig.layout.xaxis.range[1] if fig.layout.xaxis.range else max(df[x_col]),
						  y0=y, y1=y, xref="x", yref="y", line=dict(color="red", dash="dash"))
	if vlines:
		for x in vlines:
			fig.add_shape(type="line", x0=x, x1=x,
						  y0=fig.layout.yaxis.range[0] if fig.layout.yaxis.range else min(df[y_col]),
						  y1=fig.layout.yaxis.range[1] if fig.layout.yaxis.range else max(df[y_col]),
						  xref="x", yref="y", line=dict(color="blue", dash="dot"))
	return fig

#### Dash / Flask Helper Utilities ####
# Dash integration (lazy import)
try:
	from dash import dcc  # Dash 2.x
except ImportError:
	try:
		import dash_core_components as dcc  # Dash 1.x fallback
	except ImportError:
		dcc = None  # If Dash not installed

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
	night_type: str = "clear"
) -> folium.Map:
	"""
	Create interactive Folium map for Oregon sites. Usable in Streamlit and Jupyter.

	Parameters
	----------
	sites_df : pd.DataFrame
		DataFrame containing site data.
	night_type : str, optional
		Type of night ('clear' or 'cloudy'), by default "clear".

	Returns
	-------
	folium.Map
		Folium Map object with site markers.
	"""
	# Select brightness column and title
	brightness_col = 'median_brightness_mag_arcsec2' if night_type == "clear" else 'cloudy_median_brightness'
	title_suffix = "Clear Nights" if night_type == "clear" else "Cloudy Nights"
	# Filter valid data
	map_data = sites_df.dropna(subset=['latitude', 'longitude', brightness_col])
	# Create base map
	m = folium.Map(location=[44.0, -121.0], zoom_start=7, tiles='OpenStreetMap')
	# Add site markers
	for _, row in map_data.iterrows():
		_add_site_marker(m, row, brightness_col, title_suffix)
	return m

def _add_site_marker(
	m: folium.Map,
	row: pd.Series,
	brightness_col: str,
	title_suffix: str
):
	"""Add a CircleMarker for a site to the map."""
	brightness = row[brightness_col]
	color = _get_marker_color(brightness)
	popup_html = f"""
	<div style='width: 250px;'>
		<h4>{row['site_name']}</h4>
		<p><strong>{title_suffix} Brightness:</strong> {brightness:.2f} mag/arcsec²</p>
		<p><strong>Bortle Scale:</strong> {row.get('bortle_scale', 'N/A')}</p>
		<p><strong>Dark Sky Status:</strong> {row.get('dark_sky_status', 'None')}</p>
		<p><strong>Region:</strong> {row.get('region', 'Unknown')}</p>
	</div>
	"""
	folium.CircleMarker(
		location=[row['latitude'], row['longitude']],
		radius=8 if row.get('dark_sky_status', 'None') != 'None' else 6,
		popup=folium.Popup(popup_html, max_width=300),
		color='black',
		fillColor=color,
		weight=2,
		fillOpacity=0.8,
		tooltip=f"{row['site_name']}: {brightness:.2f} mag/arcsec²"
	).add_to(m)

def _get_marker_color(brightness: float) -> str:
	"""Return color for marker based on brightness value."""
	if pd.isna(brightness):
		return 'gray'
	elif brightness >= 21.5:
		return 'darkgreen'
	elif brightness >= 21.2:
		return 'green'
	elif brightness >= 20.0:
		return 'yellow'
	elif brightness >= 19.0:
		return 'orange'
	else:
		return 'red'


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

# # Optional: Dash-specific wrapper for Folium map
# try:
# 	import dash_html_components as html
# 	def folium_map_dash_component(
# 		map_obj: folium.Map,
# 		width: str = "100%",
# 		height: str = "500px"
# 	):
# 		"""
# 		Return a Dash html.Iframe component with the Folium map.

# 		Parameters
# 		----------
# 		map_obj : folium.Map
# 			Folium map object.
# 		width : str, optional
# 			Width of the iframe. Defaults to "100%".
# 		height : str, optional
# 			Height of the iframe. Defaults to "500px".

# 		Returns
# 		-------
# 		html.Iframe
# 			Dash HTML Iframe component with the map.
# 		"""
# 		return html.Iframe(srcDoc=get_folium_html(map_obj, width, height), width=width, height=height)
# except ImportError:
# 	pass
# # defining functions to create visualizations