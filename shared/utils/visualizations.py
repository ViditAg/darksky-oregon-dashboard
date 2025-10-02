"""
Create interactive maps and charts using Plotly for the Dark Sky Oregon Dashboard

Primary functions:
1. create_oregon_map_plotly: Create an interactive map of Oregon with site markers using Plotly.
2. create_oregon_map_folium: Create an interactive map of Oregon with site markers using Folium.
3. create_ranking_chart: Create a bar chart ranking sites by a specified metric.
4. create_interactive_2d_plot : Create an interactive 2D scatter plot.
"""

# importing neccessary libraries
import pandas as pd
import plotly.graph_objects as go
import folium

#### Ranking Chart Visualization ####
def create_ranking_chart(
	sites_df: pd.DataFrame,
	configs: dict,
	clicked_sites: list[str] | None = None
) -> go.Figure:
	"""
	Create interactive Plotly bar chart for site rankings.

	Parameters
	----------
	sites_df : pd.DataFrame
		DataFrame containing site data.
	configs : dict
		Configuration dictionary for the measurement type.
	clicked_sites : list[str], optional
		List of site names to highlight. Default is None.
	
	Returns
	-------
	go.Figure
		Plotly Figure object for the ranking bar chart.
	"""
	# Extract configurations
	y_col = configs.get('bar_chart_y_col')
	y_label = configs.get('bar_chart_y_label')
	y_tick_type = configs['bar_chart_yicks'].get('tickmode', 'linear')
	y_tick_vals = configs['bar_chart_yicks'].get('tickvals', None)
	y_tick_text = configs['bar_chart_yicks'].get('ticktext', None)
	
	# Drop rows with missing values for the metric or site name
	chart_data = sites_df.dropna(subset=[y_col, 'site_name']).copy()
	
	# Sort data
	chart_data.sort_values(y_col, ascending=True, inplace=True)
	
	# Get bar colors from color_rgba column
	bar_colors = chart_data['color_rgba'].tolist()

	# when no site is clicked, use the color_rgba for border color and width 1
	marker_line_color = bar_colors
	marker_line_width = [1 for _ in chart_data["site_name"]]

	# Create marker styles for the clicked site
	# if a site is clicked, change its border color to cyan and increase border width to 8
	if clicked_sites is not None:
		marker_line_color = [
			"cyan" if site in clicked_sites else marker_line_color[i] for i, site in enumerate(chart_data["site_name"])
		]
		marker_line_width = [
			8 if site in clicked_sites else marker_line_width[i] for i, site in enumerate(chart_data["site_name"])
		]
		

	# Create the bar chart figure
	fig = go.Figure(
		data=go.Bar(
			y=chart_data['site_name'], # names of sites on y-axis
			x=chart_data[y_col], # metric values on x-axis
			orientation='h', # horizontal bars
			hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<extra></extra>', # show site name and value on hover
			marker_color=bar_colors,
			marker_line_color=marker_line_color,
			marker_line_width=marker_line_width,
		)
	)
	
	# Update layout for better appearance
	fig.update_layout(
		autosize=True,
		plot_bgcolor="aliceblue",
		xaxis_side="bottom",
		height=max(400, len(chart_data) * 13),
		margin=dict(l=0, r=0, t=40, b=0),
		showlegend=False,
		xaxis=dict(
			title_font=dict(size=18),
			tickfont=dict(size=20),
			type=y_tick_type,
			tickvals=y_tick_vals,
			ticktext=y_tick_text,
		),
		yaxis=dict(
			title=y_label,
			title_font=dict(size=20),
			tickfont=dict(size=12),
			dtick=1,
		)
	)

	return fig

#### 2D Scatter Plot Visualization ####
def create_interactive_2d_plot(
	df: pd.DataFrame,
	configs: dict,
	clicked_sites: list[str] | None = None,
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

	x_col = configs.get('scatter_x_col')
	y_col = configs.get('scatter_y_col')
	x_label = configs.get('scatter_x_label')
	y_label = configs.get('scatter_y_label')

	# Create marker styles for the clicked site
	if clicked_sites is not None:
		marker_line_color = [
			"black" if site in clicked_sites else "white" for site in df["site_name"]
		]
		marker_line_width = [
			5 if site in clicked_sites else 1 for site in df["site_name"]
		]
	else:
		marker_line_color = df['color_rgba']
		marker_line_width = [1 for _ in df["site_name"]]

	fig = go.Figure(
    	data=go.Scatter(
        	x=df[x_col],
        	y=df[y_col],
        	mode='markers',
        	marker=dict(
            	color=df['color_rgba'],
            	size=15,
				line=dict(
					color=marker_line_color,
					width=marker_line_width
				)
        	),
            hovertext=df['site_name']
    	)
		)
	
	if clicked_sites is not None:
		selected_df = df[df['site_name'].isin(clicked_sites)]
		fig.add_trace(go.Scatter(
			x=selected_df[x_col],
			y=selected_df[y_col],
			mode='markers',
			marker=dict(color='cyan', size=20),
			hovertext=selected_df['site_name'],
		))


	fig.update_layout(
    	plot_bgcolor="aliceblue",
  		showlegend=False,
		margin=dict(l=0, r=0, t=40, b=0),
		autosize=True,
		height=300,
		#width=450,
		xaxis=dict(
			title=x_label,
			title_font=dict(size=18),
			tickfont=dict(size=14)
		),
		yaxis=dict(
			title=y_label,
			title_font=dict(size=18),
			tickfont=dict(size=14)
		)
	)

	if vline:
		fig.add_shape(
			type="line",
			x0=vline,
			x1=vline,
			y0=0,
			y1=max(df[y_col])+1,
			xref="x", yref="y", line=dict(color="black", dash="dash")
		)
		# Add annotation text at the top of the vline
		fig.add_annotation(
			x=vline,
			y=max(df[y_col])+1,
			text="""Dark-Sky Qualified <br> if >= {0} mag/arcsec²""".format(vline),
			showarrow=False,
			yshift=0,
			xshift=-60,
			font=dict(size=12, color="black"),
			xanchor="center"
		)
	return fig


######## Oregon Map Visualization ########
def create_oregon_map_plotly(
	sites_df,
	map_center=[44.0, -121.0],
	zoom=6,
	color_col='median_brightness_mag_arcsec2',
	highlight_sites=None
) -> go.Figure:
	"""
	Create interactive Plotly map for Oregon sites. Usable in Dash.
	Parameters
	----------
	sites_df : pd.DataFrame
		DataFrame containing site data.		
	"""
	
	# Group by lat/lon and aggregate site names
	def get_color_for_group(group, color_col):
    	# Get color_rgba from the row with the highest metric
		idx = group[color_col].idxmax()
		return group.loc[idx, 'color_rgba']
	
	grouped = sites_df.groupby(
		['latitude', 'longitude']
		).apply(
		lambda g: pd.Series(
			{
		'site_name': g['site_name'].tolist(),
		'color_rgba': get_color_for_group(g, color_col),
			}
		),
		include_groups=False # False to avoid adding group keys to the index
	).reset_index()

	grouped['site_text'] = grouped['site_name'].apply(lambda x: ", ".join(x))
	grouped['marker_size'] = 15
	
	if highlight_sites is not None:
		# update grouped['color_rgba'] and grouped['marker_size']	
		# for each row check if any site in the list group['site_name'] is in highlight_sites
		# if yes, set color to cyan and size to 15
		masker = grouped['site_name'].apply(
			lambda x: any(site in highlight_sites for site in x)
		)
		grouped.loc[masker, 'color_rgba'] = 'cyan'
		grouped.loc[masker, 'marker_size'] = 20

	fig = go.Figure(
		go.Scattermapbox(
			lat=grouped['latitude'],
			lon=grouped['longitude'],
			mode='markers',
			marker=dict(
				color=grouped['color_rgba'],
				size=grouped['marker_size'],
				opacity=1
			),
			text=grouped['site_text'],
			customdata=grouped['site_name'],  # Pass site name for clickData
			hoverinfo='text'
		)
	)

	fig.update_layout(
		autosize=True,
		mapbox=dict(
			style='open-street-map',
			center=dict(lat=map_center[0], lon=map_center[1]),
			zoom=zoom
		),
		margin=dict(l=0, r=0, t=0, b=0),
		height=400,
		#width=600,
	)

	return fig


def create_oregon_map_folium(
	sites_df: pd.DataFrame,
	main_col: str,
	zoom: int = 6,
	map_center: list[float] = [44.0, -121.0],
	highlight_sites: list | None = None,
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
		location=map_center,
		zoom_start=zoom,
		tiles='OpenStreetMap'
		)
	
	# Add site markers
	for (lat, lon), group in sites_df.groupby(['latitude', 'longitude']):
		# Determine marker color and style
		color_ = group[group[main_col]==group[main_col].max()]['color_rgba'].values[0]
		# Determine edge color and width
		edge_color_ = color_
		edge_width_ = 1
		if (highlight_sites is not None) and (highlight_sites[0] in group["site_name"].values):
			edge_color_ = "cyan"
			edge_width_ = 5

		tooltip_str = ""
		for _, row in group.iterrows():
			tooltip_str += f"{row['site_name']}<br>"

		folium.CircleMarker(
			location=[lat, lon],
			radius=7,
			#popup=folium.Popup(popup_html, max_width=300),
			fillColor=color_,
			color=edge_color_,
			weight=edge_width_,
			fillOpacity=1,
			tooltip=tooltip_str
		).add_to(m)

	return m