# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                options=[
                                    {'label': 'All Sites', 'value': 'ALL'},
                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                    ],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True), 

                                html.Br(), 


                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                min=0, 
                                max=10000, 
                                step=1000,
                                marks={0: '0',
                                2500: '2500',
                                5000: '5000',
                                7500: '7500',
                                10000: '10000'},
                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):

    filtered_df = spacex_df

    if selected_site == 'ALL':
        # Count total successes for all sites
        filtered_df = filtered_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(filtered_df, values='class',  names='Launch Site', title="Total Successful Launches by Site")
    else:
        # Filter data for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site].reset_index()
        filtered_df = filtered_df.groupby('class').sum().reset_index()
        filtered_df['class'] = filtered_df['class'].replace({1: 'Success', 0: 'Failure'})

        fig = px.pie(filtered_df, values='Unnamed: 0',  names='class', title=f"Success vs. Failure for {selected_site}")

    # Customize the appearance of the pie chart
    fig.update_traces(textinfo='percent+label')
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Callback function to update the scatter plot based on dropdown and slider inputs
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter_plot(selected_site, payload_range):
    # Filter the data based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # Check if 'ALL' sites are selected or a specific site
    if selected_site == 'ALL':
        # Show data for all sites
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title="Outcome vs. Payload for All Sites",
            labels={'class': 'Mission Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        )
    else:
        # Filter data for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title=f"Payload vs. Outcome for {selected_site}",
            labels={'class': 'Mission Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        )

    # Customize the layout and return the figure
    fig.update_layout(
        xaxis_title="Payload Mass (kg)",
        yaxis_title="Mission Outcome",
        yaxis=dict(tickvals=[0, 1], ticktext=['Failure', 'Success']),
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
