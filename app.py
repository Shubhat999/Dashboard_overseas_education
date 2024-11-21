import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# Sample Data (Replace with your full dataset)
df = pd.read_excel(r'Indian_students_stats_country-wise.xlsx')
df = df.iloc[:, :7]
df = pd.melt(df, id_vars=['Sl. No.', 'Country'], var_name='Year', value_name='Value')
df['Year'] = pd.to_datetime(df["Year"], format="%Y")
df['Year'] = df['Year'].dt.strftime('%Y')
df['Value'] = df['Value'].fillna(df['Value'].median())
df.Value = df.Value.astype('int64')

# KPI 1: Animated Bar Plot with Line Plot for Total Students Abroad by Year
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
    barmode='group'
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

# KPI 3: Year-on-Year Growth in Student Enrollment (Dual-axis Line Chart)
yearly_students = df.groupby('Year')['Value'].sum().reset_index()
yearly_students['Growth Rate'] = yearly_students['Value'].pct_change() * 100

fig_growth = go.Figure()
fig_growth.add_trace(go.Scatter(
    x=yearly_students['Year'],
    y=yearly_students['Value'],
    mode='lines+markers',
    name='Total Students',
    line=dict(color='royalblue'),
    yaxis='y1'
))
fig_growth.add_trace(go.Scatter(
    x=yearly_students['Year'],
    y=yearly_students['Growth Rate'],
    mode='lines+markers',
    name='Growth Rate',
    line=dict(color='orange'),
    yaxis='y2'
))

fig_growth.update_layout(
    title="Year-on-Year Growth in Student Enrollment (Dual-axis)",
    xaxis_title="Year",
    yaxis=dict(title="Total Students", titlefont=dict(color='royalblue'), tickfont=dict(color='royalblue')),
    yaxis2=dict(title="Growth Rate (%)", titlefont=dict(color='orange'), tickfont=dict(color='orange'), overlaying='y', side='right'),
    template='plotly'
)

# KPI 4: Animated Bullet Chart for Market Share of Top 5 Countries
top_5_countries = country_enrollment.sort_values(by='Share', ascending=False).head(5)
market_share = top_5_countries['Share'].sum()

bullet_chart = go.Figure(go.Indicator(
    mode="gauge+number",
    value=0,
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

impact_df = impact_df[impact_df.Value_2020_2021>10000]
# Sort the dataframe by 'value_2020_2021' in descending order
impact_df = impact_df.sort_values(by='Value_2020_2021', ascending=False)

# Step 5: Create a graph for the impact visualization
country_impact_graph = {
    'data': [{
        'x': impact_df['Country'],
        'y': impact_df['Impact (%)'],
        'type': 'bar',
        'name': 'Impact of Global Events',
        'marker': {'color': 'orange'}
    }],
    'layout': {
        'title': 'Impact of Global Events (COVID-19) by Country',
        'xaxis': {'title': 'Country'},
        'yaxis': {'title': 'Impact (%)'},
        'height': 300  # Adjust the height as necessary
    }
}

# Step 2: Dash App Layout
app = dash.Dash(__name__)

app.layout = html.Div([

    # Row 1: Total Students and Country Enrollment Bubble Chart
    html.Div([ 
        html.Div([dcc.Graph(id='total_students', figure=total_students_graph)], 
                 style={'width': '48%', 'display': 'inline-block', 'margin-right': '2%'}),
        html.Div([dcc.Graph(id='country_enrollment_bubble', figure=bubble_chart)], 
                 style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),

    # Row 2: Year Growth and Market Share Charts
    html.Div([
        html.Div([dcc.Graph(id='year_growth', figure=fig_growth)], 
                 style={'width': '48%', 'display': 'inline-block', 'margin-right': '2%'}),
        html.Div([
            dcc.Graph(id='market_share', figure=bullet_chart),
            dcc.Interval(id='interval', interval=300, n_intervals=5)
        ], style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),

    # Row 3: Diversity Index Chart, Dropdown, and Country-wise Impact Graph
    html.Div([

        # Left side: Diversity Index Chart and Dropdown
        html.Div([
            html.Label("Select Country:", style={'font-weight': 'bold', 'font-size': '12px'}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in diversity_index_df['Country'].unique()],
                value=diversity_index_df['Country'].iloc[0],
                style={
                    'width': '90%',
                    'font-size': '12px',
                    'padding': '5px'
                }
            ),
            dcc.Graph(id='diversity-index-chart', style={'height': '300px'})  # Reduced height
        ], style={'width': '48%', 'display': 'inline-block', 'margin-right': '2%'}),

        # Right side: Country-wise Impact of Global Events (COVID-19)
        html.Div([
            html.Label("Impact of Global Events (COVID-19) by Country:", style={'font-weight': 'bold', 'font-size': '14px'}),
            dcc.Graph(
                id='country-impact-graph',
                figure=country_impact_graph,
                style={'height': '300px'}  # Adjust height as necessary
            )
        ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '2%'}),

    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),

])





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
    return bullet_chart

@app.callback(
    Output('diversity-index-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_diversity_index_chart(selected_country):
    # Filter the diversity index for the selected country
    filtered_data = diversity_index_df[diversity_index_df['Country'] == selected_country]

    if filtered_data.empty:
        # Provide a default value and message if no data is found
        value = 0
        title_text = f"No Data Available for {selected_country}"
    else:
        value = filtered_data['Diversity Index'].iloc[0]
        title_text = f"Diversity Index for {selected_country}"

    # Advanced Gauge Chart for Diversity Index
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
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
        title={'text': title_text, 'font': {'size': 24}}
    ))

    # Update chart layout
    fig.update_layout(
        template="plotly",
        height=400,
        margin=dict(t=50, b=30, l=20, r=20),
    )
    return fig


if __name__ == '__main__':
    # Get the PORT from the environment variables (default to 8050 if not set)
    port = int(os.environ.get("PORT", 5000))
    # Run the server on the correct port and bind to 0.0.0.0
    app.run_server(debug=True, host="0.0.0.0", port=port)
