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

# Optional: Dash-specific wrapper for Folium map
try:
	import dash_html_components as html
	def folium_map_dash_component(
		map_obj: folium.Map,
		width: str = "100%",
		height: str = "500px"
	):
		"""
		Return a Dash html.Iframe component with the Folium map.

		Parameters
		----------
		map_obj : folium.Map
			Folium map object.
		width : str, optional
			Width of the iframe. Defaults to "100%".
		height : str, optional
			Height of the iframe. Defaults to "500px".

		Returns
		-------
		html.Iframe
			Dash HTML Iframe component with the map.
		"""
		return html.Iframe(srcDoc=get_folium_html(map_obj, width, height), width=width, height=height)
except ImportError:
	pass
# defining functions to create visualizations

# importing neccessary libraries
import pandas as pd
import folium
import plotly.graph_objects as go
from streamlit import metric


#### Ranking Chart Visualization ####
def create_ranking_chart(
	sites_df: pd.DataFrame,
	metric: str,
	night_type: str = "clear"
) -> go.Figure:
	"""
	Create interactive Plotly bar chart for site rankings.

	Parameters
	----------
	sites_df : pd.DataFrame
		DataFrame containing site data.
	metric : str
		Metric to rank sites by ('brightness', 'bortle', 'pollution_ratio', 'annual_change').
	night_type : str, optional
		Type of night ('clear' or 'cloudy'), by default "clear".

	Returns
	-------
	go.Figure
		Plotly Figure object for the ranking bar chart.
	"""
	# Map metric to column name
	y_col = _get_metric_column(metric, night_type)
	# Prepare and sort data
	chart_data = _prepare_chart_data(sites_df, y_col)
	# Assign colors for bars
	colors = _get_bar_colors(chart_data)
	# Create the bar chart
	fig = _build_ranking_bar_chart(chart_data, y_col, colors, metric, night_type)
	return fig

def _get_metric_column(metric: str, night_type: str) -> str:
	"""Return the column name for the selected metric and night type."""
	metric_mapping = {
		'brightness': 'median_brightness_mag_arcsec2' if night_type == 'clear' else 'cloudy_median_brightness',
		'bortle': 'bortle_scale',
		'X_brighter': 'x_brighter_than_darkest',
		'annual_change': 'annual_percent_change'
	}
	return metric_mapping.get(metric, 'median_brightness_mag_arcsec2')

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
	metric: str,
	night_type: str
) -> go.Figure:
	"""Build the Plotly bar chart for site rankings."""
	# Create the bar chart
	fig = go.Figure(data=go.Bar(
		y=chart_data['site_name'],
		x=chart_data[y_col],
		orientation='h',
		marker=dict(color=colors),
		text=chart_data[y_col].round(2),
		textposition='outside',
		hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<extra></extra>'
	))
	# Set chart titles
	title_map = {
		'brightness': f'Sky Brightness ({night_type.title()} Nights)',
		'bortle': 'Bortle Dark-Sky Scale',
		'pollution_ratio': 'Light Pollution Ratio',
		'annual_change': 'Annual Change (%)'
	}
	fig.update_layout(
		title=title_map.get(metric, 'Site Comparison'),
		xaxis_title=f'{title_map.get(metric, "Value")}',
		yaxis_title='Monitoring Site',
		height=max(400, len(chart_data) * 20),
		margin=dict(l=200, r=50, t=50, b=50),
		showlegend=False
	)
	return fig

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


