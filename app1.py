# import plotly.express as px
# import pandas as pd
# from dash import Dash, html, dcc, callback, Output, Input

# # Load the data
# df = pd.read_csv(r'Dashboard_overseas_education\Data\Students_data.csv')

# # Rename columns for consistency
# df.rename(columns={ 
#     'College or Institution Type': 'College/Institution_Type',
#     'College or Institution Name': 'College/Institution_Name',
#     'Undergraduate Full-Time': 'Undergraduate_Full-Time',
#     'Undergraduate Part-Time': 'Undergraduate_Part-Time',
#     'Graduate Full-Time': 'Graduate_Full-Time',
#     'Graduate Part-Time': 'Graduate_Part-Time'
# }, inplace=True)

# # Convert to datetime and extract the year for display
# df['Year'] = pd.to_datetime(df['Year'], format='%Y')
# df['Year'] = df['Year'].dt.strftime('%Y')

# # Calculate total students
# df['Total_Students'] = (
#     df['Undergraduate_Full-Time'] +
#     df['Undergraduate_Part-Time'] +
#     df['Graduate_Full-Time'] +
#     df['Graduate_Part-Time']
# )

# # Initialize the Dash app
# app = Dash(__name__)

# # Layout of the app
# app.layout = html.Div([
#     html.H1("Interactive Enrollment Dashboard", style={"textAlign": "center"}),

#     # Filter Dropdown
#     html.Div([
#         html.Label("Select Institution Type:"),
#         dcc.Dropdown(
#             id='institution-type-filter',
#             options=[{'label': i, 'value': i} for i in df['College/Institution_Type'].unique()],
#             value=df['College/Institution_Type'].unique()[0],
#             clearable=False
#         )
#     ], style={"width": "50%", "margin": "auto"}),

#     # KPI Graphs
#     html.Div([
#         dcc.Graph(id='enrollment-distribution'),
#         dcc.Graph(id='yearly-trends'),
#         dcc.Graph(id='full-part-ratio'),
#         dcc.Graph(id='program-preference')  # New KPI Graph for Program Preference Rate
#     ])
# ])

# # Callbacks for interactivity
# @app.callback(
#     [Output('enrollment-distribution', 'figure'),
#      Output('yearly-trends', 'figure'),
#      Output('full-part-ratio', 'figure'),
#      Output('program-preference', 'figure')],  # Output for new KPI
#     [Input('institution-type-filter', 'value')]
# )
# def update_graphs(selected_institution_type):
#     # Filter data based on selected institution type
#     filtered_df = df[df['College/Institution_Type'] == selected_institution_type]

#     # KPI 1: Advanced Enrollment Distribution by Institution Type (Sunburst Chart)
#     grouped_df = df.groupby('College/Institution_Type').agg({
#         'Undergraduate_Full-Time': 'sum',
#         'Undergraduate_Part-Time': 'sum',
#         'Graduate_Full-Time': 'sum',
#         'Graduate_Part-Time': 'sum'
#     }).reset_index()

#     # Calculate total students for each institution type
#     grouped_df['Total_Students'] = (
#         grouped_df['Undergraduate_Full-Time'] +
#         grouped_df['Undergraduate_Part-Time'] +
#         grouped_df['Graduate_Full-Time'] +
#         grouped_df['Graduate_Part-Time']
#     )

#     # Calculate the percentage of students in each institution type
#     total_students = grouped_df['Total_Students'].sum()
#     grouped_df['Percentage'] = (grouped_df['Total_Students'] / total_students) * 100

#     # Sunburst chart for enrollment distribution
#     sunburst_fig = px.sunburst(
#         grouped_df,
#         path=['College/Institution_Type'],
#         values='Percentage',
#         title="Enrollment Distribution by Institution Type"
#     )

#     # KPI 2: Animated Enrollment Trends by Year (Dot Plot with Animation)
#     yearly_trends = filtered_df.groupby('Year').sum().reset_index()
#     yearly_trends['Total_Students'] = (
#         yearly_trends['Undergraduate_Full-Time'] +
#         yearly_trends['Undergraduate_Part-Time'] +
#         yearly_trends['Graduate_Full-Time'] +
#         yearly_trends['Graduate_Part-Time']
#     )

#     # Year-over-Year Growth Calculation
#     yearly_trends['YoY_Growth'] = yearly_trends['Total_Students'].pct_change() * 100
#     yearly_trends = yearly_trends.dropna(subset=['YoY_Growth'])

#     animated_line_fig = px.line(
#         yearly_trends,
#         x='Year',
#         y='YoY_Growth',
#         title="Year-over-Year Enrollment Growth (Animated Line Chart)",
#         labels={'Year': 'Enrollment Year', 'YoY_Growth': 'Year-over-Year Growth (%)'},
#         animation_frame='Year',
#         markers=True
#     )

#     # KPI 3: Full-Time vs Part-Time Ratio (Bar Chart showing Ratio)
#     filtered_df['Full-Time'] = filtered_df['Undergraduate_Full-Time'] + filtered_df['Graduate_Full-Time']
#     filtered_df['Part-Time'] = filtered_df['Undergraduate_Part-Time'] + filtered_df['Graduate_Part-Time']
#     ratio_df = filtered_df.groupby('Year')[['Full-Time', 'Part-Time']].sum().reset_index()
#     ratio_df['Full-Time to Part-Time Ratio'] = ratio_df['Full-Time'] / ratio_df['Part-Time']

#     ratio_fig = px.bar(
#         ratio_df, x='Year', y='Full-Time to Part-Time Ratio', 
#         title="Full-Time to Part-Time Enrollment Ratio", 
#         labels={'Full-Time to Part-Time Ratio': 'Full-Time to Part-Time Ratio'},
#         color='Full-Time to Part-Time Ratio',
#     )

#     # KPI 4: Program Preference Rate (Undergraduate vs. Graduate) - Radar Chart
#     preference_df = filtered_df.groupby('Year').sum().reset_index()
#     preference_df['Undergraduate_Preference_Rate'] = (preference_df['Undergraduate_Full-Time'] + preference_df['Undergraduate_Part-Time']) / preference_df['Total_Students'] * 100
#     preference_df['Graduate_Preference_Rate'] = (preference_df['Graduate_Full-Time'] + preference_df['Graduate_Part-Time']) / preference_df['Total_Students'] * 100

#     # Prepare for Radar chart (Polar plot)
#     preference_df_melted = preference_df.melt(id_vars="Year", value_vars=['Undergraduate_Preference_Rate', 'Graduate_Preference_Rate'], var_name="Program Type", value_name="Preference Rate")

#     # Customizing the Radar chart
#     radar_fig = px.line_polar(
#         preference_df_melted, 
#         r="Preference Rate", 
#         theta="Year", 
#         color="Program Type", 
#         line_close=True, 
#         title="Program Preference Rate (Undergraduate vs Graduate)",
#         markers=True
#     )

#     # Enhance chart appearance: make it more colorful and visually appealing
#     radar_fig.update_traces(
#         line=dict(width=4),  # Increase line width
#         marker=dict(size=8)  # Larger markers for emphasis
#     )

#     # Customize layout for better presentation
#     radar_fig.update_layout(
#         polar=dict(
#             radialaxis=dict(
#                 visible=True,
#                 range=[0, 100],  # Range from 0% to 100%
#                 tickfont=dict(size=14, color='black')  # Ticks font size and color
#             ),
#             angularaxis=dict(
#                 tickfont=dict(size=14, color='black')  # Angular ticks font size and color
#             )
#         ),
#         title_font=dict(size=20, color='navy'),  # Title font size and color
#         legend=dict(
#             title="Program Type",
#             font=dict(size=14),
#             borderwidth=1
#         ),
#         plot_bgcolor='white'  # Background color for the plot area
#     )

#     return sunburst_fig, animated_line_fig, ratio_fig, radar_fig

# # Run the app
# if __name__ == '__main__':
#     app.run_server(debug=True)







# import plotly.express as px
# import plotly.graph_objects as go
# import pandas as pd
# from dash import Dash, html, dcc, callback, Output, Input
# import numpy as np

# # Load the data
# df = pd.read_csv(r'C:\Users\DELL\Desktop\Dashboard_overseas_education\Data\Students_data.csv')

# # Rename columns for consistency
# df.rename(columns={ 
#     'College or Institution Type': 'College/Institution_Type',
#     'College or Institution Name': 'College/Institution_Name',
#     'Undergraduate Full-Time': 'Undergraduate_Full-Time',
#     'Undergraduate Part-Time': 'Undergraduate_Part-Time',
#     'Graduate Full-Time': 'Graduate_Full-Time',
#     'Graduate Part-Time': 'Graduate_Part-Time'
# }, inplace=True)

# # Convert to datetime and extract the year for display
# df['Year'] = pd.to_datetime(df['Year'], format='%Y')
# df['Year'] = df['Year'].dt.strftime('%Y')

# # Calculate total students
# df['Total_Students'] = (
#     df['Undergraduate_Full-Time'] +
#     df['Undergraduate_Part-Time'] +
#     df['Graduate_Full-Time'] +
#     df['Graduate_Part-Time']
# )

# # Calculate Graduate to Undergraduate Conversion Rate
# df['Graduate_to_Undergraduate_Conversion_Rate'] = (
#     (df['Graduate_Full-Time'] + df['Graduate_Part-Time']) /
#     (df['Undergraduate_Full-Time'] + df['Undergraduate_Part-Time']) * 100
# )

# # Initialize the Dash app
# app = Dash(__name__)

# # Layout of the app
# app.layout = html.Div([
#     html.H1("Interactive Enrollment Dashboard", style={"textAlign": "center", "color": "#004A7C", "font-size": "32px"}),  # Updated title color and size

#     # Filter Dropdown
#     html.Div([
#         html.Label("Select Institution Type:", style={"font-size": "18px", "font-weight": "bold", "color": "#333"}),
#         dcc.Dropdown(
#             id='institution-type-filter',
#             options=[{'label': i, 'value': i} for i in df['College/Institution_Type'].unique()],
#             value=df['College/Institution_Type'].unique()[0],
#             clearable=False,
#             style={'font-size': '16px', 'padding': '10px', 'width': '50%', 'margin': 'auto', 'backgroundColor': '#f0f0f0'}
#         )
#     ], style={"width": "50%", "margin": "auto"}),

#     # KPI Graphs
#     html.Div([
#         dcc.Graph(id='enrollment-distribution'),
#         dcc.Graph(id='yearly-trends'),
#         dcc.Graph(id='full-part-ratio'),
#         dcc.Graph(id='program-preference'),
#         dcc.Graph(id='conversion-rate')  # New KPI graph  
#     ], style={'backgroundColor': '#f7f7f7', 'padding': '20px'})
# ])

# # Callbacks for interactivity
# @app.callback(
#     [Output('enrollment-distribution', 'figure'),
#      Output('yearly-trends', 'figure'),
#      Output('full-part-ratio', 'figure'),
#      Output('program-preference', 'figure'),
#      Output('conversion-rate', 'figure')],  # Output for the new KPI  
#     [Input('institution-type-filter', 'value')]
# )
# def update_graphs(selected_institution_type):
#     # Filter data based on selected institution type
#     filtered_df = df[df['College/Institution_Type'] == selected_institution_type]

#     # KPI 1: Advanced Enrollment Distribution by Institution Type (Sunburst Chart)
#     grouped_df = df.groupby('College/Institution_Type').agg({
#         'Undergraduate_Full-Time': 'sum',
#         'Undergraduate_Part-Time': 'sum',
#         'Graduate_Full-Time': 'sum',
#         'Graduate_Part-Time': 'sum'
#     }).reset_index()

#     # Calculate total students for each institution type
#     grouped_df['Total_Students'] = (
#         grouped_df['Undergraduate_Full-Time'] +
#         grouped_df['Undergraduate_Part-Time'] +
#         grouped_df['Graduate_Full-Time'] +
#         grouped_df['Graduate_Part-Time']
#     )

#     # Calculate the percentage of students in each institution type
#     total_students = grouped_df['Total_Students'].sum()
#     grouped_df['Percentage'] = (grouped_df['Total_Students'] / total_students) * 100

#     # Sunburst chart for enrollment distribution
#     sunburst_fig = px.sunburst(
#         grouped_df,
#         path=['College/Institution_Type'],
#         values='Percentage',
#         title="Enrollment Distribution by Institution Type",
#         color='Percentage',  # Adding color to represent percentage
#         color_continuous_scale='Blues'  # Color scale
#     )
#     sunburst_fig.update_layout(
#         plot_bgcolor='white',  # White background for clarity
#         title_font=dict(size=20, color='navy'),
#         margin=dict(t=50, b=50, l=50, r=50)
#     )

#     # KPI 2: Animated Enrollment Trends by Year (Dot Plot with Animation)
#     yearly_trends = filtered_df.groupby('Year').sum().reset_index()
#     yearly_trends['Total_Students'] = (
#         yearly_trends['Undergraduate_Full-Time'] +
#         yearly_trends['Undergraduate_Part-Time'] +
#         yearly_trends['Graduate_Full-Time'] +
#         yearly_trends['Graduate_Part-Time']
#     )

#     # Year-over-Year Growth Calculation
#     yearly_trends['YoY_Growth'] = yearly_trends['Total_Students'].pct_change() * 100
#     yearly_trends = yearly_trends.dropna(subset=['YoY_Growth'])

#     animated_line_fig = px.line(
#     yearly_trends,
#     x='Year',
#     y='YoY_Growth',
#     title="Year-over-Year Enrollment Growth (Animated Line Chart)",
#     labels={'Year': 'Enrollment Year', 'YoY_Growth': 'Year-over-Year Growth (%)'},
#     animation_frame='Year',
#     markers=True,
#     line_shape='linear',  # Smooth line
#     line_dash_sequence=['solid'],  # Line style
#     color_discrete_sequence=px.colors.qualitative.Bold  # Colorful palette
# )

#     # Customize marker size and layout
#     animated_line_fig.update_traces(
#         marker=dict(size=12, symbol='circle', line=dict(width=2, color='DarkSlateGrey')),  # Large colorful dots
#         line=dict(width=3),  # Thicker line for emphasis
#     )

#     animated_line_fig.update_layout(
#         plot_bgcolor='white',
#         title_font=dict(size=24, color='navy'),
#         margin=dict(t=60, b=60, l=60, r=60),
#         xaxis=dict(
#             title_font=dict(size=18),
#             tickfont=dict(size=14),
#             gridcolor='lightgrey',
#         ),
#         yaxis=dict(
#             title_font=dict(size=18),
#             tickfont=dict(size=14),
#             gridcolor='lightgrey',
#         ),
#         legend=dict(font=dict(size=12)),
#     )




#     # KPI 3: Full-Time vs Part-Time Ratio (Bubble Chart showing Ratio and Student Growth)
#     filtered_df['Full-Time'] = filtered_df['Undergraduate_Full-Time'] + filtered_df['Graduate_Full-Time']
#     filtered_df['Part-Time'] = filtered_df['Undergraduate_Part-Time'] + filtered_df['Graduate_Part-Time']
#     ratio_df = filtered_df.groupby('Year')[['Full-Time', 'Part-Time']].sum().reset_index()
#     ratio_df['Full-Time to Part-Time Ratio'] = ratio_df['Full-Time'] / ratio_df['Part-Time']

#     # Bubble chart for Full-Time vs Part-Time Ratio with Total Students Size
#     bubble_chart_fig = px.scatter(
#         ratio_df, 
#         x='Year', 
#         y='Full-Time to Part-Time Ratio', 
#         size='Full-Time',  # Bubble size based on full-time students
#         color='Year',  # Different color for each year
#         title="Full-Time vs Part-Time Enrollment Ratio with Student Growth", 
#         labels={'Full-Time to Part-Time Ratio': 'Full-Time to Part-Time Ratio'},
#         color_continuous_scale=px.colors.sequential.Viridis  # Color scale for better clarity
#     )
#     bubble_chart_fig.update_layout(
#         plot_bgcolor='white',
#         title_font=dict(size=20, color='navy'),
#         margin=dict(t=50, b=50, l=50, r=50),
#         xaxis_title="Year",
#         yaxis_title="Full-Time to Part-Time Ratio",
#         showlegend=True
#     )

#     # KPI 4: Program Preference Rate (Undergraduate vs. Graduate) - Radar Chart
#     preference_df = filtered_df.groupby('Year').sum().reset_index()
#     preference_df['Undergraduate_Preference_Rate'] = (preference_df['Undergraduate_Full-Time'] + preference_df['Undergraduate_Part-Time']) / preference_df['Total_Students'] * 100
#     preference_df['Graduate_Preference_Rate'] = (preference_df['Graduate_Full-Time'] + preference_df['Graduate_Part-Time']) / preference_df['Total_Students'] * 100

#     # Prepare for Radar chart (Polar plot)
#     preference_df_melted = preference_df.melt(id_vars="Year", value_vars=['Undergraduate_Preference_Rate', 'Graduate_Preference_Rate'], var_name="Program Type", value_name="Preference Rate")

#     # Customizing the Radar chart
#     radar_fig = px.line_polar(
#         preference_df_melted, 
#         r="Preference Rate", 
#         theta="Year", 
#         color="Program Type", 
#         line_close=True, 
#         title="Program Preference Rate (Undergraduate vs Graduate)",
#         markers=True,
#         color_discrete_sequence=["#00BFFF", "#FF6347"]  # Color choices for the programs
#     )

#     # Enhance chart appearance: make it more colorful and visually appealing
#     radar_fig.update_traces(
#         line=dict(width=4),  # Increase line width
#         marker=dict(size=8)  # Larger markers for emphasis
#     )

#     # Customize layout for better presentation
#     radar_fig.update_layout(
#         polar=dict(
#             radialaxis=dict(
#                 visible=True,
#                 range=[0, 100],  # Range from 0% to 100%
#                 tickfont=dict(size=14, color='black')  # Ticks font size and color
#             ),
#             angularaxis=dict(
#                 tickfont=dict(size=14, color='black')  # Angular ticks font size and color
#             )
#         ),
#         title_font=dict(size=20, color='navy'),
#         plot_bgcolor='white',
#         margin=dict(t=50, b=50, l=50, r=50)
#     )

#     # KPI 5 : Add Graduate to Undergraduate Conversion Rate Graph (Animated Heatmap or 3D Surface)
#     conversion_df = filtered_df.groupby('Year')[['Graduate_to_Undergraduate_Conversion_Rate']].mean().reset_index()

#     Year = conversion_df['Year']
#     conversionRatePctg  = conversion_df['Graduate_to_Undergraduate_Conversion_Rate']
#     Density = np.array([conversionRatePctg] * len(Year))  # Simulated for surface appearance

#     conversion_fig_3d = go.Figure(data=[go.Surface(
#         z=Density,
#         x=Year,
#         y=conversionRatePctg,
#         colorscale='Plasma',
#         showscale=True,
#     )])

#     conversion_fig_3d.update_layout(
#         title="Graduate to Undergraduate Conversion Rate (3D Perspective)",
#         title_font=dict(size=24, color='darkblue'),
#         scene=dict(
#             xaxis=dict(title='Year'),
#             yaxis=dict(title='Conversion Rate (%)'),
#             zaxis=dict(title='Density'),
#         ),
#         margin=dict(t=60, b=60, l=60, r=60),
#     )

    

#     return sunburst_fig, animated_line_fig, bubble_chart_fig, radar_fig , conversion_fig_3d

# # Run the app
# if __name__ == '__main__':
#     app.run_server(debug=True)











import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
import numpy as np

# Load the data
df = pd.read_csv(r'Students_data.csv')

# Rename columns for consistency
df.rename(columns={ 
    'College or Institution Type': 'College/Institution_Type',
    'College or Institution Name': 'College/Institution_Name',
    'Undergraduate Full-Time': 'Undergraduate_Full-Time',
    'Undergraduate Part-Time': 'Undergraduate_Part-Time',
    'Graduate Full-Time': 'Graduate_Full-Time',
    'Graduate Part-Time': 'Graduate_Part-Time'
}, inplace=True)

# Convert to datetime and extract the year for display
df['Year'] = pd.to_datetime(df['Year'], format='%Y')
df['Year'] = df['Year'].dt.strftime('%Y')

# Calculate total students
df['Total_Students'] = (
    df['Undergraduate_Full-Time'] +
    df['Undergraduate_Part-Time'] +
    df['Graduate_Full-Time'] +
    df['Graduate_Part-Time']
)

# Calculate Graduate to Undergraduate Conversion Rate
df['Graduate_to_Undergraduate_Conversion_Rate'] = (
    (df['Graduate_Full-Time'] + df['Graduate_Part-Time']) /
    (df['Undergraduate_Full-Time'] + df['Undergraduate_Part-Time']) * 100
)

# Initialize the Dash app
app = Dash(__name__)



# Define the layout
app.layout = html.Div(
    [
        # Title
        html.H1(
            "Interactive Enrollment Dashboard",
            style={
                "textAlign": "center",
                "color": "#00BFFF",  # Neon blue color
                "fontSize": "36px",
                "marginBottom": "20px",
                "textShadow": "0 0 8px #00BFFF, 0 0 16px #00BFFF",  # Glow effect
            },
        ),

        # Dropdown Filter
        html.Div(
            [
                html.Label(
                    "Select Institution Type:",
                    style={
                        "fontSize": "18px",
                        "fontWeight": "bold",
                        "color": "#00BFFF",  # Neon blue for labels
                        "marginBottom": "10px",
                        "textShadow": "0 0 8px #00BFFF",  # Glow effect
                    },
                ),
                dcc.Dropdown(
                    id="institution-type-filter",
                    options=[
                        {"label": i, "value": i}
                        for i in df["College/Institution_Type"].unique()
                    ],
                    value=df["College/Institution_Type"].unique()[0],
                    clearable=False,
                    style={
                        "fontSize": "16px",
                        "padding": "10px",
                        "width": "100%",
                        "backgroundColor": "#000000",  # Black background for dropdown
                        "color": "black",  # Neon blue text
                        "border": "1px solid #00BFFF",  # Blue border
                        "boxShadow": "0 0 8px #00BFFF",  # Glow around dropdown
                    },
                ),
            ],
            style={"width": "50%", "margin": "0 auto", "marginBottom": "30px"},
        ),

        # KPI Graphs - Row 1
        html.Div(
            [
                html.Div(
                    dcc.Graph(
                        id="enrollment-distribution",
                        config={"displayModeBar": False},
                        style={"backgroundColor": "rgba(0, 0, 0, 0)"},
                    ),
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "border": "1px solid #00BFFF",  # Blue border
                        "boxShadow": "0 0 8px #00BFFF",  # Glow around graph container
                        "borderRadius": "10px",
                        "padding": "10px",
                    },
                ),
                html.Div(
                    dcc.Graph(
                        id="yearly-trends",
                        config={"displayModeBar": False},
                        style={"backgroundColor": "rgba(0, 0, 0, 0)"},
                    ),
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "border": "1px solid #00BFFF",  # Blue border
                        "boxShadow": "0 0 8px #00BFFF",  # Glow around graph container
                        "borderRadius": "10px",
                        "padding": "10px",
                    },
                ),
            ],
            style={"display": "flex", "justifyContent": "space-between", "padding": "20px"},
        ),

        # KPI Graphs - Row 2
        html.Div(
            [
                html.Div(
                    dcc.Graph(
                        id="full-part-ratio",
                        config={"displayModeBar": False},
                        style={"backgroundColor": "rgba(0, 0, 0, 0)"},
                    ),
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "border": "1px solid #00BFFF",  # Blue border
                        "boxShadow": "0 0 8px #00BFFF",  # Glow around graph container
                        "borderRadius": "10px",
                        "padding": "10px",
                    },
                ),
                html.Div(
                    dcc.Graph(
                        id="program-preference",
                        config={"displayModeBar": False},
                        style={"backgroundColor": "rgba(0, 0, 0, 0)"},
                    ),
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "border": "1px solid #00BFFF",  # Blue border
                        "boxShadow": "0 0 8px #00BFFF",  # Glow around graph container
                        "borderRadius": "10px",
                        "padding": "10px",
                    },
                ),
            ],
            style={"display": "flex", "justifyContent": "space-between", "padding": "20px"},
        ),

        # Conversion Rate Graph
        html.Div(
            dcc.Graph(
                id="conversion-rate",
                config={"displayModeBar": False},
                style={"backgroundColor": "rgba(0, 0, 0, 0)"},
            ),
            style={
                "backgroundColor": "rgba(0, 0, 0, 0)",  # Transparent container
                "padding": "20px",
                "margin": "20px auto",
                "border": "1px solid #00BFFF",  # Blue border
                "boxShadow": "0 0 8px #00BFFF",  # Glow effect
                "borderRadius": "10px",
            },
        ),
    ],
    style={
        "backgroundColor": "#000428",  # Gradient-like dark blue
        "backgroundImage": "linear-gradient(45deg, #000428, #004e92)",  # Shining blue gradient
        "padding": "20px",
    },
)

# Callbacks for interactivity
@app.callback(
    [Output('enrollment-distribution', 'figure'),
     Output('yearly-trends', 'figure'),
     Output('full-part-ratio', 'figure'),
     Output('program-preference', 'figure'),
     Output('conversion-rate', 'figure')],  # Output for the new KPI  
    [Input('institution-type-filter', 'value')]
)
def update_graphs(selected_institution_type):
    # Filter data based on selected institution type
    filtered_df = df[df['College/Institution_Type'] == selected_institution_type]

    # KPI 1: Advanced Enrollment Distribution by Institution Type (Sunburst Chart)
    grouped_df = df.groupby('College/Institution_Type').agg({
        'Undergraduate_Full-Time': 'sum',
        'Undergraduate_Part-Time': 'sum',
        'Graduate_Full-Time': 'sum',
        'Graduate_Part-Time': 'sum'
    }).reset_index()

    # Calculate total students for each institution type
    grouped_df['Total_Students'] = (
        grouped_df['Undergraduate_Full-Time'] +
        grouped_df['Undergraduate_Part-Time'] +
        grouped_df['Graduate_Full-Time'] +
        grouped_df['Graduate_Part-Time']
    )

    # Calculate the percentage of students in each institution type
    total_students = grouped_df['Total_Students'].sum()
    grouped_df['Percentage'] = (grouped_df['Total_Students'] / total_students) * 100

    sunburst_fig = px.sunburst(
    grouped_df,
    path=['College/Institution_Type'],
    values='Percentage',
    title="Enrollment Distribution by Institution Type",
    color='Percentage',  # Adding color to represent percentage
    color_continuous_scale='Blues'  # Color scale
)

    # Update layout for a gray-black background
    sunburst_fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent plot area
        paper_bgcolor='black',  # Entire figure's background set to black
        title_font=dict(size=20, color='white'),  # White title font
        font=dict(color='white'),  # White font for all text
        margin=dict(t=50, b=50, l=50, r=50),  # Margins around the chart
    )

    # Add color to sunburst sections and make it pop against the dark background
    sunburst_fig.update_traces(
        marker=dict(line=dict(color='gray', width=0.5))  # Light gray borders for clarity
    )

    # KPI 2: Animated Enrollment Trends by Year (Dot Plot with Animation)
    

    # Group by 'Year' and calculate total students
    yearly_trends = filtered_df.groupby('Year').sum().reset_index()

    # Calculate Total Students
    yearly_trends['Total_Students'] = (
        yearly_trends['Undergraduate_Full-Time'] +
        yearly_trends['Undergraduate_Part-Time'] +
        yearly_trends['Graduate_Full-Time'] +
        yearly_trends['Graduate_Part-Time']
    )

    # Year-over-Year Growth Calculation
    yearly_trends['YoY_Growth'] = yearly_trends['Total_Students'].pct_change() * 100

    # Drop rows with NaN YoY Growth
    yearly_trends = yearly_trends.dropna(subset=['YoY_Growth'])

    # Ensure the DataFrame index is reset properly
    yearly_trends.reset_index(drop=True, inplace=True)

    # Animated smooth line graph
    animated_line_fig = go.Figure(
        data=[go.Scatter(
            x=yearly_trends['Year'],
            y=yearly_trends['YoY_Growth'],
            mode='lines+markers',
            name="YoY Growth",
            line=dict(color='navy', width=3, shape='spline'),  # Smooth curve with spline
            marker=dict(size=12, symbol='circle', color='DarkSlateGrey')  # Adjusted marker size and color
        )]
    )

    # Add smooth animation frame for each year
    frames = [go.Frame(
        data=[go.Scatter(
            x=yearly_trends['Year'][:k],
            y=yearly_trends['YoY_Growth'][:k],
            mode='lines+markers',
            line=dict(color='navy', width=3, shape='spline'),
            marker=dict(size=12, symbol='circle', color='DarkSlateGrey')
        )],
        name=str(yearly_trends['Year'][k-1])
    ) for k in range(1, len(yearly_trends) + 1)]

    # Adding the frames to the figure
    animated_line_fig.frames = frames

    # Update Layout
    animated_line_fig.update_layout(
        title="Year-over-Year Enrollment Growth (Animated Smooth Line)",
        xaxis=dict(
            title="Enrollment Year",
            showgrid=False  # Remove grid lines for x-axis
        ),
        yaxis=dict(
            title="YoY Growth (%)",
            showgrid=False  # Remove grid lines for y-axis
        ),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(
                label="Play",
                method="animate",
                args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True)]
            )]
        )],
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 191, 255, 0.5)',

        title_font=dict(size=18, color='navy'),
        margin=dict(t=30, b=30, l=30, r=30),
        xaxis_title_font=dict(size=18),
        yaxis_title_font=dict(size=18),
    )




    # KPI 3: Full-Time vs Part-Time Ratio (Bubble Chart showing Ratio and Student Growth)
    filtered_df['Full-Time'] = filtered_df['Undergraduate_Full-Time'] + filtered_df['Graduate_Full-Time']
    filtered_df['Part-Time'] = filtered_df['Undergraduate_Part-Time'] + filtered_df['Graduate_Part-Time']
    ratio_df = filtered_df.groupby('Year')[['Full-Time', 'Part-Time']].sum().reset_index()
    ratio_df['Full-Time to Part-Time Ratio'] = ratio_df['Full-Time'] / ratio_df['Part-Time']

    # Bubble chart for Full-Time vs Part-Time Ratio with Total Students Size
    bubble_chart_fig = px.scatter(
        ratio_df, 
        x='Year', 
        y='Full-Time to Part-Time Ratio', 
        size='Full-Time',  # Bubble size based on full-time students
        color='Year',  # Different color for each year
        title="Full-Time vs Part-Time Enrollment Ratio with Student Growth", 
        labels={'Full-Time to Part-Time Ratio': 'Full-Time to Part-Time Ratio'},
        color_continuous_scale=px.colors.sequential.Viridis  # Color scale for better clarity
    )
    bubble_chart_fig.update_layout(
    plot_bgcolor='rgba(173, 216, 230, 1)',  # Light blue color for the plot area
    paper_bgcolor='rgba(173, 216, 230, 0.9)',  # Slightly transparent light blue for the entire figure
    title_font=dict(size=20, color='navy'),
    margin=dict(t=50, b=50, l=50, r=50),
    xaxis_title="Year",
    yaxis_title="Full-Time to Part-Time Ratio",
    showlegend=False,
    xaxis=dict(showgrid=False),  # Remove x-axis grid lines
    yaxis=dict(showgrid=False)   # Remove y-axis grid lines
    )



    # KPI 4: Program Preference Rate (Undergraduate vs. Graduate) - Radar Chart
    preference_df = filtered_df.groupby('Year').sum().reset_index()
    preference_df['Undergraduate_Preference_Rate'] = (preference_df['Undergraduate_Full-Time'] + preference_df['Undergraduate_Part-Time']) / preference_df['Total_Students'] * 100
    preference_df['Graduate_Preference_Rate'] = (preference_df['Graduate_Full-Time'] + preference_df['Graduate_Part-Time']) / preference_df['Total_Students'] * 100

    # Prepare for Radar chart (Polar plot)
    preference_df_melted = preference_df.melt(id_vars="Year", value_vars=['Undergraduate_Preference_Rate', 'Graduate_Preference_Rate'], var_name="Program Type", value_name="Preference Rate")

    # Customizing the Radar chart
    radar_fig = px.line_polar(
        preference_df_melted, 
        r="Preference Rate", 
        theta="Year", 
        color="Program Type", 
        line_close=True, 
        title="Program Preference Rate (Undergraduate vs Graduate)",
        markers=True,
        color_discrete_sequence=["#00BFFF", "#FF6347"]  # Color choices for the programs
    )

    # Enhance chart appearance: make it more colorful and visually appealing
    radar_fig.update_traces(
        line=dict(width=4),  # Increase line width
        marker=dict(size=8),  # Larger markers for emphasis
        fill='toself',  # Fill the area under the lines to make the chart more colorful
        opacity=0.3  # Adjust opacity of the filled area for a softer effect
    )

    # Customize layout for better presentation
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],  # Range from 0% to 100%
                tickfont=dict(size=14, color='black')  # Ticks font size and color
            ),
            angularaxis=dict(
                tickfont=dict(size=14, color='white')  # Angular ticks font size and color
            )
        ),
        title_font=dict(size=20, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        margin=dict(t=50, b=50, l=50, r=50),
        legend=dict(
            font=dict(color='white')  # Set legend font color to white
        )
    )

    # KPI 5 : Add Graduate to Undergraduate Conversion Rate Graph (Animated Heatmap or 3D Surface)
    conversion_df = filtered_df.groupby('Year')[['Graduate_to_Undergraduate_Conversion_Rate']].mean().reset_index()

    Year = conversion_df['Year']
    conversionRatePctg  = conversion_df['Graduate_to_Undergraduate_Conversion_Rate']
    Density = np.array([conversionRatePctg] * len(Year))  # Simulated for surface appearance

    conversion_fig_3d = go.Figure(data=[go.Surface(
        z=Density,
        x=Year,
        y=conversionRatePctg,
        colorscale='Plasma',
        showscale=True,
    )])

    conversion_fig_3d.update_layout(
        title="Graduate to Undergraduate Conversion Rate (3D Perspective)",
        title_font=dict(size=24, color='darkblue'),
        scene=dict(
            xaxis=dict(title='Year'),
            yaxis=dict(title='Conversion Rate (%)'),
            zaxis=dict(title='Density'),
        ),
        margin=dict(t=60, b=60, l=60, r=60),
        paper_bgcolor='rgba(240, 248, 255, 0.8)',  # Light blue with transparency (lighter background)
        plot_bgcolor='rgba(240, 248, 255, 0.8)',   # Light blue plot background
    )


    

    return sunburst_fig, animated_line_fig, bubble_chart_fig, radar_fig , conversion_fig_3d



if __name__ == '__main__':
    # Get the PORT from the environment variables (default to 8050 if not set)
    port = int(os.environ.get("PORT", 8050))
    # Run the server on the correct port and bind to 0.0.0.0
    app.run_server(debug=False, host="0.0.0.0", port=port)











