import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.interpolate import make_interp_spline
import os

# Sample Data (Replace with your full dataset)
df = pd.read_excel(r'Indian_students_stats_country-wise.xlsx')
df = df.iloc[:, :7]
df = pd.melt(df, id_vars=['Sl. No.', 'Country'], var_name='Year', value_name='Value')
df['Year'] = pd.to_datetime(df["Year"], format="%Y")
df['Year'] = df['Year'].dt.strftime('%Y')
df['Value'] = df['Value'].fillna(df['Value'].median())
df.Value = df.Value.astype('int64')

# KPI 1: Bar Plot with Line Plot for Total Students Abroad by Year
total_students = df.groupby('Year')['Value'].sum().reset_index()

bar_trace = go.Bar(
    x=total_students['Year'], 
    y=total_students['Value'], 
    name='Total Students',
    marker=dict(color='royalblue')
)

line_trace = go.Scatter(
    x=total_students['Year'], 
    y=total_students['Value'], 
    mode='lines+markers', 
    name='Total Students (Line)', 
    line=dict(color='orange', width=3)
)

total_students_graph = go.Figure(data=[bar_trace, line_trace])
total_students_graph.update_layout(
    title='Total Students Abroad by Year (Bar + Line)',
    xaxis_title='Year',
    yaxis_title='Total Students',
    template='plotly',
    barmode='group',
    plot_bgcolor='rgb(30, 30, 30)',  # Dark gray background for the plot area
    paper_bgcolor='rgb(30, 30, 30)',  # Dark gray background for the entire figure
    title_font=dict(color='white'),    # White color for title
    font=dict(color='white'),         # White color for text in the chart
    xaxis=dict(
        showgrid=False  # Remove grid lines on x-axis
    ),
    yaxis=dict(
        showgrid=False  # Remove grid lines on y-axis
    )
)


# KPI 2: Bubble Chart for Country-wise Enrollment Share (Top 10 Countries)
country_enrollment = df.groupby('Country')['Value'].sum().reset_index()
country_enrollment['Share'] = (country_enrollment['Value'] / country_enrollment['Value'].sum()) * 100
top_country_enrollment = country_enrollment.sort_values(by='Value', ascending=False).head(10)
bubble_chart = px.scatter(
    top_country_enrollment,
    x='Country',
    y='Share',
    size='Value',
    color='Share',
    hover_name='Country',
    title="Top 10 Countries by Enrollment Share (Bubble Chart)",
    size_max=60,
    color_continuous_scale='Blues'
)

# Update the layout for the Bubble Chart
bubble_chart.update_layout(
    paper_bgcolor='rgb(30, 30, 30)',  # Dark gray background for the entire figure
    plot_bgcolor='rgb(30, 30, 30)',   # Dark gray background for the plot area
    title_font=dict(color='white'),    # White color for title
    font=dict(color='white'),          # White color for text in the chart
    xaxis=dict(
        title='Country',
        showgrid=False  # Remove grid lines on x-axis
    ),
    yaxis=dict(
        title='Enrollment Share (%)',
        showgrid=False  # Remove grid lines on y-axis
    ),
    coloraxis_colorbar=dict(
        title="Share (%)",
        tickvals=[0, max(top_country_enrollment['Share'])],  # Set color bar ticks
        ticktext=["Low", "High"],  # Custom text for the color bar ticks
        tickfont=dict(color='white')  # White color for color bar ticks
    ),
)

# KPI 3: Year-on-Year Growth in Student Enrollment (Dual-axis Line Chart)
# Smooth the Growth Rate
yearly_students = df.groupby('Year')['Value'].sum().reset_index()
yearly_students['Growth Rate'] = yearly_students['Value'].pct_change() * 100
yearly_students['Growth Rate'].fillna(0, inplace=True)

# Temporarily convert 'Year' to numeric for interpolation
x_years = pd.to_numeric(yearly_students['Year'], errors='coerce')
y_growth = yearly_students['Growth Rate']

# Use spline interpolation for smoothing
x_smooth = np.linspace(x_years.min(), x_years.max(), 500)  # Smooth range
spline = make_interp_spline(x_years, y_growth, k=3)  # Cubic spline interpolation
y_smooth = spline(x_smooth)

# Create Animated Smooth Line Chart
fig_smooth = go.Figure()

# Add an Initial Empty Line
fig_smooth.add_trace(go.Scatter(
    x=x_smooth,
    y=[None] * len(x_smooth),  # Start with no visible data
    mode='lines',
    line=dict(color='orange', width=3),
    name='Smoothed Growth Rate (%)',
))

# Add Animation Frames
fig_smooth.frames = [
    go.Frame(
        data=[
            go.Scatter(
                x=x_smooth[:k],
                y=y_smooth[:k],
                mode='lines',
                line=dict(color='orange', width=3),
                name='Smoothed Growth Rate (%)',
            )
        ],
        name=f"Frame {k}"
    )
    for k in range(1, len(x_smooth) + 1, 10)  # Increment for smoother animation
]

# Define custom tick text for x-axis (convert numeric back to string format)
x_ticks = np.arange(int(x_years.min()), int(x_years.max()) + 1)
x_ticktext = [str(year) for year in x_ticks]

# Update Layout with Animation Controls and Custom Tick Text
fig_smooth.update_layout(
    title="Year-on-Year Growth (Smoothed Animated Line Plot)",
    xaxis=dict(
        title="Year",
        tickvals=x_ticks,  # Set the positions of the ticks
        ticktext=x_ticktext,  # Set the labels for the ticks
        tickformat="%Y",  # Ensure years are shown in full numeric format without commas
        showgrid=False  # Remove grid lines from x-axis
    ),
    yaxis=dict(
        title="Growth Rate (%)",
        showgrid=False  # Remove grid lines from y-axis
    ),
    template='plotly',
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        buttons=[dict(
            label="Play",
            method="animate",
            args=[None, {
                "frame": {"duration": 30, "redraw": True},
                "fromcurrent": True
            }]
        ),
        dict(
            label="Pause",
            method="animate",
            args=[[None], {
                "frame": {"duration": 0, "redraw": False},
                "mode": "immediate"
            }])],
    )],
    plot_bgcolor='rgb(30, 30, 30)',  # Dark gray background for the plot area
    paper_bgcolor='rgb(30, 30, 30)',  # Dark gray background for the entire figure
    title_font=dict(color='white'),    # White color for title
    font=dict(color='white'),          # White color for text in the chart
)


# KPI 4: Animated Bullet Chart for Market Share of Top 5 Countries
top_5_countries = country_enrollment.sort_values(by='Share', ascending=False).head(5)
market_share = top_5_countries['Share'].sum()

bullet_chart = go.Figure(go.Indicator(
    mode="gauge+number",
    value=0,  # Set your desired value here
    gauge={
        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},  # Axis ticks color to white
        'steps': [
            {'range': [0, market_share], 'color': "lightgreen"},
            {'range': [market_share, 100], 'color': "lightgray"},
        ],
        'bar': {'color': "green"}
    },
    title={'text': "Market Share of Top 5 Countries", 'font': {'size': 24, 'color': 'white'}},  # Title font color set to white
    number={'font': {'color': 'white', 'size': 30}}  # Set number color to white and size
))


# KPI 5: 
# Step 1: Calculate Diversity Index for each country
df['Share'] = df.groupby('Country')['Value'].transform(lambda x: x / x.sum())
df['Share^2'] = df['Share'] ** 2
diversity_index_df = df.groupby('Country')['Share^2'].sum().reset_index()
diversity_index_df['Diversity Index'] = 1 - diversity_index_df['Share^2']
diversity_index_df = diversity_index_df[['Country', 'Diversity Index']]

# KPI 6:
# Step 1: Calculate the sum of students in 2020 and 2021
students_2020_2021 = df[df['Year'].isin(['2020', '2021'])].groupby('Country')['Value'].sum().reset_index()

# Step 2: Calculate the average number of students in 2018 and 2019
students_2018_2019 = df[df['Year'].isin(['2018', '2019'])].groupby('Country')['Value'].mean().reset_index()

# Step 3: Merge the two dataframes (students_2020_2021 and students_2018_2019) to calculate the impact
impact_df = pd.merge(students_2020_2021, students_2018_2019, on='Country', suffixes=('_2020_2021', '_2018_2019'))

# Step 4: Calculate the impact
impact_df['Impact (%)'] = ((impact_df['Value_2020_2021'] - impact_df['Value_2018_2019']) / impact_df['Value_2018_2019']) * 100

impact_df = impact_df[impact_df.Value_2020_2021>2000]
# Sort the dataframe by 'value_2020_2021' in descending order
impact_df = impact_df.sort_values(by='Value_2020_2021', ascending=False).head(15)

# Step 5: Create a 3D scatter plot for the impact visualization
country_impact_graph = go.Figure(data=[go.Scatter3d(
    x=impact_df['Country'],  # Country names will be placed on the X-axis
    y=impact_df['Impact (%)'],  # Impact percentage on the Y-axis
    z=[0] * len(impact_df),  # Set Z-axis values as zero to start the bars from the bottom
    mode='markers+lines',  # Use both markers and lines to simulate bars
    marker=dict(
        size=15,
        color=impact_df['Value_2020_2021'],  # Color bars based on the number of students
        colorscale='Viridis',  # Color scale for better visualization
        opacity=0.7
    ),
    line=dict(
        width=3  # Line width for bar edges
    )
)])

# Update layout for the 3D chart
country_impact_graph.update_layout(
    scene=dict(
        xaxis_title='Country',
        yaxis_title='Impact (%)',
        zaxis_title='Start from Zero',
        camera_eye=dict(x=0.2, y=1.25, z=1.25),  # Adjust the camera view angle as necessary
        
        # Customize the x, y, and z axes
        xaxis=dict(
            title_font=dict(color='silver'),  # Color of axis title
            tickfont=dict(color='silver'),  # Color of axis tick labels
            # showgrid=True,  # Show grid lines
            # gridcolor='gray',  # Color of the gridlines
            zeroline=False  # Disable the zero line
        ),
        yaxis=dict(
            title_font=dict(color='silver'),  # Color of axis title
            tickfont=dict(color='silver'),  # Color of axis tick labels
            # showgrid=True,  # Show grid lines
            # gridcolor='gray',  # Color of the gridlines
            zeroline=False  # Disable the zero line
        ),
        zaxis=dict(
            title_font=dict(color='white'),  # Color of axis title
            tickfont=dict(color='white'),  # Color of axis tick labels
            # showgrid=True,  # Show grid lines
            # gridcolor='gray',  # Color of the gridlines
            zeroline=False  # Disable the zero line
        )
    ),
    height=600,  # Adjust the height as necessary
    paper_bgcolor='rgb(30, 30, 30)',  # Darker gray background for the chart paper
    plot_bgcolor='rgb(30, 30, 30)'    # Darker gray background for the plot area
)



#KPI 7: 
# Separate data for 2018 and 2022 (treating 'Year' as a string)
data_2018 = df[df['Year'] == '2018'][['Country', 'Value']].rename(columns={'Value': 'value_2018'})
data_2022 = df[df['Year'] == '2022'][['Country', 'Value']].rename(columns={'Value': 'value_2022'})

# Merge 2018 and 2022 data
merged_data = pd.merge(data_2018, data_2022, on='Country', how='inner')

# Filter countries with at least 10,00 students in 2018
filtered_data = merged_data[(merged_data['value_2018'] >= 200) & (merged_data['value_2018'] <= 12000)]

# Calculate Growth Rate and Emerging Country Score
filtered_data['Growth Rate (%)'] = ((filtered_data['value_2022'] - filtered_data['value_2018']) / filtered_data['value_2018']) * 100
filtered_data['Emerging Country Score'] = filtered_data['Growth Rate (%)'] / filtered_data['value_2018']
filtered_data= filtered_data[filtered_data['Growth Rate (%)']>1]



# Create the figure using Plotly
fig = px.choropleth(
    filtered_data,
    locations="Country",  # Country column for the location
    locationmode="country names",  # Use full country names
    color="Emerging Country Score",  # Color based on Emerging Country Score
    hover_name="Country",  # Show country names on hover
    hover_data={
        "value_2018": "Students in 2018",
        "value_2022": "Students in 2022",
        "Growth Rate (%)": ":.2f",
        "Emerging Country Score": ":.6f"
    },
    color_continuous_scale="Blues",  # Use a light color scale
    
    projection="natural earth",  # Use natural earth projection for the map
)

fig.update_layout(
    geo=dict(
        projection_scale=1,  # Zoom in a little bit to make the countries clearer
        showland=True,  # Show the land
        landcolor="black",  # Black land color for night effect
        subunitcolor="white",  # White borders for countries
        showcoastlines=True,
        coastlinecolor="black",  # Coastline color in black for space effect
        showlakes=False,  # No lakes (keep it dark)
        projection_type="natural earth"
    ),
    title_font=dict(size=20, color='white', family='Arial'),  # Reduced title size
    font=dict(color='white'),  # White font for other text
    plot_bgcolor="rgba(0,0,0,0)",  # Transparent background for the plot area
    paper_bgcolor="rgba(0,0,0,0)",  # Transparent background for the entire chart
    margin=dict(l=0, r=0, t=20, b=0),  # Reduced margins for the plot
)

# Add glow effect to the data points to simulate light bubbles
fig.update_traces(marker=dict(line=dict(color='rgba(0,0,0,0.7)', width=0.5), opacity=0.9))

# KPI 8:
# Calculate Average Students per Country
average_students = (
    df.groupby("Country")["Value"]
    .mean()
    .reset_index()
    .rename(columns={"Value": "Average Students"})
)

# Create Sunburst Chart
sunburst_fig = px.sunburst(
    average_students,
    path=["Country"],
    values="Average Students",
    color="Average Students",
    color_continuous_scale=px.colors.sequential.Plasma,
    title="Average Students Per Country"
)

# Update the layout for the Sunburst Chart
sunburst_fig.update_layout(
    paper_bgcolor='rgb(30, 30, 30)',  # Dark gray background for the entire chart
    plot_bgcolor='rgb(30, 30, 30)',   # Dark gray background for the plot area
    title_font=dict(color='white'),    # White color for title
    font=dict(color='white'),          # White color for text in the chart
    coloraxis_colorbar=dict(
        title="Average Students",      # Color bar title
        tickvals=[0, max(average_students['Average Students'])],  # Set color bar ticks
        ticktext=["Low", "High"],      # Custom text for the color bar ticks
        tickfont=dict(color='white')   # White color for color bar ticks
    ),
    hoverlabel=dict(
        bgcolor="rgba(0, 0, 0, 0.8)",  # Semi-transparent black background for hover labels
        font=dict(color="white")        # White font color for hover labels
    )
)

# Set hover template to display Average Students as integer
sunburst_fig.update_traces(
    hovertemplate='<b>%{label}</b><br>' +  # Show the label (Country name)
                  'Average Students: %{value:.0f}'  # Display the value as an integer (no decimals)
)

# Show the figure
# sunburst_fig.show()


# KPI 9: GSMI - Index
# Function to calculate Growth Rate
def calculate_growth_rate(df):
    # Sort the data by 'Country' and 'Year' to ensure correct order
    df = df.sort_values(by=['Country', 'Year'])

    # Calculate the Growth Rate as percentage change
    df['Growth Rate'] = df.groupby(['Country'])['Value'].pct_change() * 100
    return df

# Ensure Growth Rate is calculated before the callback
df = calculate_growth_rate(df)








# Initialize Dash App with Bootstrap dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div([

    # Row 1: GSMI KPI Indicator, Diversity Ratio, and Market Share
    html.Div([
        # GSMI KPI Indicator
        html.Div([
            html.H1("GSMI KPI Indicator", style={
                'textAlign': 'center',
                'font-size': '24px',
                'font-weight': 'bold',
                'color': '#333333',
                'background': 'linear-gradient(90deg, #4e54c8, #8f94fb)',
                'border-radius': '8px',
                'padding': '10px',
                'margin-bottom': '20px'
            }),
            html.Div([
                html.Label("Select Country:", style={
                    'font-weight': 'bold',
                    'font-size': '16px',
                    'color': '#4e54c8',
                }),
                # Advanced Custom Dropdown Component
                dcc.Dropdown(
                    id='gsmi-country-dropdown',
                    options=[{'label': country, 'value': country} for country in df['Country'].unique()],
                    value='USA',
                    style={
                        'width': '90%',
                        'margin': '10px auto',
                        'border-radius': '12px',
                        'border': '2px solid #8f94fb',
                        'padding': '8px',
                        'font-size': '14px',
                        'box-shadow': '0px 4px 8px rgba(0, 0, 0, 0.2)',
                        'background-color': '#ffffff',  # Dark background color
                        'color': '#333333',  # White text color
                        'transition': 'all 0.3s ease',  # Smooth transitions
                    },
                    placeholder='Select Country...',
                    searchable=True,
                    optionHeight=35,
                ),
            ], style={'margin-bottom': '20px', 'textAlign': 'center'}),
            html.Div([
            dcc.Graph(id='gsmi-bullet-chart', style={'height': '300px'})
        ], style={
            'background-color': '#333333',  # Dark background color
            # 'padding': '20px',  # Optional padding around the graph
            'border-radius': '10px',  # Optional rounded corners
            'box-shadow': '0px 4px 8px rgba(0, 0, 0, 0.3)',  # Optional shadow effect for depth
        })
        ], style={
            'flex': '1',
            'padding': '20px',
            'border-radius': '12px',
            'box-shadow': '0px 10px 15px rgba(0, 0, 0, 0.3)',
            'margin-right': '15px',
            'background': "rgba(0, 0, 0, 0)",
            'width': '32%',
            'color': '#ffffff'
        }),

        # Diversity Ratio
        html.Div([
            html.H3("Diversity Index Chart", style={
                'font-weight': 'bold',
                'font-size': '24px',
                'textAlign': 'center',
                'color': '#ffffff',
                'background': 'linear-gradient(90deg, #11998e, #38ef7d)',
                'border-radius': '8px',
                'padding': '10px',
                'margin-bottom': '20px'
            }),
            # Advanced Custom Dropdown for Diversity Ratio
            dcc.Dropdown(
                id='diversity-country-dropdown',
                options=[{'label': country, 'value': country} for country in diversity_index_df['Country'].unique()],
                value=diversity_index_df['Country'].iloc[0],
                style={
                    'width': '90%',
                    'margin': '10px auto',
                    'border-radius': '12px',
                    'border': '2px solid #38ef7d',
                    'padding': '8px',
                    'font-size': '14px',
                    'box-shadow': '0px 4px 8px rgba(0, 0, 0, 0.2)',
                    'background-color': '#ffffff',  # Dark background color
                    'color': '#333333',  # White text color
                    'transition': 'all 0.3s ease',  # Smooth transitions
                },
                searchable=True
            ),
            html.Div([dcc.Graph(id='diversity-index-chart', style={'height': '300px'})])
        ], style={
            'flex': '1',
            'padding': '20px',
            'border-radius': '12px',
            'box-shadow': '0px 10px 15px rgba(0, 0, 0, 0.3)',
            'margin-right': '15px',
            'background': "rgba(0, 0, 0, 0)",
            'width': '32%',
            'color': '#ffffff'
        }),

        # Market Share of Top 5 Countries
        html.Div([
            html.H3("Market Share", style={
                'font-weight': 'bold',
                'font-size': '24px',
                'textAlign': 'center',
                'color': '#ffffff',
                'background': 'rgba(0, 0, 0, 0)',
                'border-radius': '8px',
                'padding': '10px',
                'margin-bottom': '20px'
            }),
            html.Div([dcc.Graph(id='market_share', figure=bullet_chart, style={'height': '300px'})]),
            dcc.Interval(id='interval', interval=100, n_intervals=1)
        ], style={
            'flex': '1',
            'padding': '20px',
            'border-radius': '12px',
            'box-shadow': '0px 10px 15px rgba(0, 0, 0, 0.3)',
            'background': 'rgba(0, 0, 0, 0)',
            'width': '32%',
            'color': '#ffffff'
        })
    ], style={
        'display': 'flex',
        'flex-direction': 'row',
        'justify-content': 'space-between',
        'align-items': 'stretch',
        'margin-bottom': '30px'
    }),

# Styling for other rows remains consistent with the above improvements
# Continue applying similar styling enhancements to Row 2, Row 3, and Row 4 as needed,

    # Row 2: Total Students and Country Enrollment Bubble Chart
    html.Div([
        html.Div([
            html.H2("Total Students", style={'font-weight': 'bold', 'font-size': '18px'}),
            dcc.Graph(id='total_students', figure=total_students_graph)
        ], style={'width': '48%', 'display': 'inline-block', 'margin-right': '2%', 'border': '1px solid #ddd', 'border-radius': '8px'}),

        html.Div([
            html.H2("Country Enrollment Bubble Chart", style={'font-weight': 'bold', 'font-size': '18px'}),
            dcc.Graph(id='country_enrollment_bubble', figure=bubble_chart)
        ], style={'width': '48%', 'display': 'inline-block', 'border': '1px solid #ddd', 'border-radius': '8px'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),

            # Row 3: Year Growth and Sunburst Chart
        html.Div([
            html.Div([
                html.H2("Smoothed Animated Line Plot for Growth Rate (%)",
                        style={'font-weight': 'bold', 'font-size': '18px', 'text-align': 'center'}),
                dcc.Graph(
                    id='smoothed_growth_animated', 
                    figure=fig_smooth,
                    style={'height': '400px'}
                )
            ], style={
                'width': '48%', 
                'display': 'inline-block', 
                'border': '1px solid #ddd', 
                'border-radius': '8px', 
                'box-shadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding': '10px',
                'margin-right': '2%'  # Aligns with the second item in the row
            }),

            html.Div([
                html.H2("Average Students Per Country (Sunburst)", 
                        style={'font-weight': 'bold', 'font-size': '18px', 'text-align': 'center'}),
                dcc.Graph(
                    id='sunburst-chart', 
                    figure=sunburst_fig,
                    style={'height': '400px'}
                )
            ], style={
                'width': '48%', 
                'display': 'inline-block', 
                'border': '1px solid #ddd', 
                'border-radius': '8px',
                'box-shadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding': '10px'
            })
        ], style={
            'display': 'flex', 
            'justify-content': 'space-between', 
            'margin-bottom': '20px'
        }),


    # Row 4: Animated Map and Impact of Global Events
    html.Div([
        html.Div([
            html.H2("Emerging Countries Enrollment Map", style={'font-weight': 'bold', 'font-size': '18px'}),
            dcc.Graph(id='animated_map', figure=fig, style={'height': '600px', 'width': '100%'})
        ], style={'width': '48%', 'display': 'inline-block', 'border': '1px solid #ddd', 'border-radius': '8px'}),

        html.Div([
            html.H2("Impact of Global Events (COVID-19) by Country", style={'font-weight': 'bold', 'font-size': '18px'}),
            dcc.Graph(id='country-impact-graph', figure=country_impact_graph, style={'height': '600px'})
        ], style={'width': '48%', 'display': 'inline-block', 'border': '1px solid #ddd', 'border-radius': '8px', 'margin-left': '2%'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-top': '20px'}),

], style={'background': 'linear-gradient(180deg, #121212, #1a1a1d, #212121)', 'padding': '20px'})







# Step 3: Callbacks
@app.callback(
    Output('market_share', 'figure'),
    [Input('interval', 'n_intervals')]
)
def animate_bullet_chart(n):
    current_value = min((market_share * n) / 50, market_share)
    bullet_chart = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_value,
        gauge={
            'axis': {'range': [None, 100]},
            'steps': [
                {'range': [0, market_share], 'color': "lightgreen"},
                {'range': [market_share, 100], 'color': "lightgray"},
            ],
            'bar': {'color': "green"}
        },
        title={'text': "Market Share of Top 5 Countries"}
    ))
    # Update the layout to ensure all fonts are white and background is transparent
    bullet_chart.update_layout(
    paper_bgcolor="rgba(0, 0, 0, 0)",  # This changes the background of the paper (chart's outer area)
    plot_bgcolor="rgba(0, 0, 0, 0)",   # This changes the background of the actual plot area
    title_font={'color': 'white'},  # Title font color set to white
    font={'color': 'white'},  # Set all font (including number) color to white for consistency
    # tickfont={'color': 'white'},  # Set tick font color to white
    width=600,  # Set the width of the chart (increase this value for a larger width)
    height=400,  # Set the height of the chart (increase this value for a larger height)
    margin={'t': 50, 'b': 50, 'l': 40, 'r': 40}  # Adjust margins to make the chart fit better
)

    return bullet_chart

@app.callback(
    [Output('diversity-index-chart', 'figure'),
     Output('gsmi-bullet-chart', 'figure')],
    [Input('diversity-country-dropdown', 'value'),
     Input('gsmi-country-dropdown', 'value')]
)
def update_charts(diversity_country, gsmi_country):
    # ----- Diversity Index Chart Logic -----
    diversity_data = diversity_index_df[diversity_index_df['Country'] == diversity_country]

    if diversity_data.empty:
        diversity_value = 0
        diversity_title = f"No Data Available for {diversity_country}"
    else:
        diversity_value = diversity_data['Diversity Index'].iloc[0]
        diversity_title = f"Diversity Index for {diversity_country}"

    diversity_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=diversity_value,
        delta={'reference': 0.5, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.5], 'color': "lightcoral"},
                {'range': [0.5, 0.8], 'color': "lightblue"},
                {'range': [0.8, 1], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.8
            }
        },
        title={'text': diversity_title, 'font': {'size': 24}},
        number={'font': {'color': 'white'}}
    ))
    # Change the background color of the entire plot (graph area)
    diversity_fig.update_layout(
    paper_bgcolor="rgba(0, 0, 0, 0)",  # This changes the background of the paper (chart's outer area)
    plot_bgcolor="rgba(0, 0, 0, 0)",   # This changes the background of the actual plot area
    title_font={'color': 'white'},  # You can also change the font color of the title
    font={'color': 'white'},
    )


    # ----- GSMI Chart Logic -----
    gsmi_data = df[df['Country'] == gsmi_country]

    if 'Growth Rate' not in gsmi_data.columns:
        return diversity_fig, go.Figure()  # Return an empty GSMI figure if no data

    # Ensure Year column is numeric
    gsmi_data['Year'] = pd.to_numeric(gsmi_data['Year'], errors='coerce')
    gsmi_data = gsmi_data.dropna(subset=['Year'])

    latest_year = gsmi_data['Year'].max()
    latest_data = gsmi_data[gsmi_data['Year'] == latest_year]
    growth_rate = latest_data['Growth Rate'].iloc[0] if not latest_data.empty else 0

    gsmi_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=growth_rate,
        delta={'reference': 0, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-50, 0], 'color': "lightcoral"},
                {'range': [0, 50], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.8
            }
        },
        title={'text': f"GSMI Growth Rate for {gsmi_country} ({latest_year})", 'font': {'size': 24}},
        number={'font': {'color': 'white'}}
    ))
    # Change the background color of the entire plot (graph area)
    gsmi_fig.update_layout(
    paper_bgcolor="rgba(0, 0, 0, 0)",  # This changes the background of the paper (chart's outer area)
    plot_bgcolor="rgba(0, 0, 0, 0)",   # This changes the background of the actual plot area
    title_font={'color': 'white'},  # You can also change the font color of the title
    font={'color': 'white'},
)

    return diversity_fig, gsmi_fig


if __name__ == '__main__':
    # Get the PORT from the environment variables (default to 8050 if not set)
    port = int(os.environ.get("PORT", 5000))
    # Run the server on the correct port and bind to 0.0.0.0
    app.run_server(debug=True, host="0.0.0.0", port=port)
