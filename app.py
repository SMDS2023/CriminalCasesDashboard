"""
Criminal Cases Dashboard
A Dash application for visualizing criminal case data
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime

# Initialize the Dash app with custom styling
app = dash.Dash(__name__, 
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# CRITICAL: Define server for deployment
server = app.server

# App title for browser tab
app.title = "Criminal Cases Dashboard"

# Sample data structure - replace with your actual data loading
# You'll need to replace this with your actual data source
def load_data():
    """
    Load criminal cases data
    Replace this function with your actual data loading logic
    """
    # Sample data - replace with your actual data
    sample_data = {
        'case_id': ['CC001', 'CC002', 'CC003', 'CC004', 'CC005'],
        'case_type': ['Theft', 'Assault', 'Fraud', 'Burglary', 'Vandalism'],
        'date_reported': ['2024-01-15', '2024-01-20', '2024-02-01', '2024-02-10', '2024-02-15'],
        'status': ['Open', 'Closed', 'Under Investigation', 'Open', 'Closed'],
        'district': ['North', 'South', 'East', 'West', 'Central']
    }
    
    df = pd.DataFrame(sample_data)
    df['date_reported'] = pd.to_datetime(df['date_reported'])
    return df

# Load the data
df = load_data()

# Define the app layout with professional styling
app.layout = html.Div([
    # Header section
    html.Div([
        html.H1("Criminal Cases Dashboard", 
                style={
                    'textAlign': 'center',
                    'color': '#2c3e50',
                    'marginBottom': '30px',
                    'fontFamily': 'Arial, sans-serif'
                }),
        
        html.P("Interactive visualization of criminal case data",
               style={
                   'textAlign': 'center',
                   'color': '#7f8c8d',
                   'fontSize': '18px',
                   'marginBottom': '40px'
               })
    ], style={'padding': '20px'}),
    
    # Controls section
    html.Div([
        html.Div([
            html.Label("Case Status:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='status-filter',
                options=[{'label': 'All', 'value': 'all'}] + 
                        [{'label': status, 'value': status} for status in df['status'].unique()],
                value='all',
                style={'marginBottom': '20px'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'paddingRight': '20px'}),
        
        html.Div([
            html.Label("Case Type:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='type-filter',
                options=[{'label': 'All', 'value': 'all'}] + 
                        [{'label': case_type, 'value': case_type} for case_type in df['case_type'].unique()],
                value='all',
                style={'marginBottom': '20px'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'paddingLeft': '20px'})
    ], style={'padding': '0 40px'}),
    
    # Charts section
    html.Div([
        # First row of charts
        html.Div([
            dcc.Graph(id='case-type-chart', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px'}),
        
        html.Div([
            dcc.Graph(id='status-chart', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px'}),
        
        # Second row - timeline chart
        html.Div([
            dcc.Graph(id='timeline-chart', style={'height': '400px'})
        ], style={'width': '100%', 'padding': '20px'}),
        
        # Data table
        html.Div([
            html.H3("Case Details", style={'textAlign': 'center', 'marginBottom': '20px'}),
            dash_table.DataTable(
                id='cases-table',
                columns=[{"name": col.replace('_', ' ').title(), "id": col} for col in df.columns],
                data=df.to_dict('records'),
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#ecf0f1'},
                page_size=10
            )
        ], style={'padding': '20px'})
    ])
], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

# Callback for updating charts based on filters
@app.callback(
    [Output('case-type-chart', 'figure'),
     Output('status-chart', 'figure'),
     Output('timeline-chart', 'figure'),
     Output('cases-table', 'data')],
    [Input('status-filter', 'value'),
     Input('type-filter', 'value')]
)
def update_dashboard(selected_status, selected_type):
    """
    Update all dashboard components based on filter selections
    """
    # Filter data based on selections
    filtered_df = df.copy()
    
    if selected_status != 'all':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    if selected_type != 'all':
        filtered_df = filtered_df[filtered_df['case_type'] == selected_type]
    
    # Case type distribution chart
    case_type_counts = filtered_df['case_type'].value_counts()
    case_type_fig = px.bar(
        x=case_type_counts.index,
        y=case_type_counts.values,
        title="Cases by Type",
        labels={'x': 'Case Type', 'y': 'Number of Cases'},
        color=case_type_counts.values,
        color_continuous_scale='Blues'
    )
    case_type_fig.update_layout(showlegend=False)
    
    # Status distribution chart
    status_counts = filtered_df['status'].value_counts()
    status_fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Cases by Status"
    )
    
    # Timeline chart
    timeline_data = filtered_df.groupby(filtered_df['date_reported'].dt.date).size().reset_index()
    timeline_data.columns = ['date', 'count']
    
    timeline_fig = px.line(
        timeline_data,
        x='date',
        y='count',
        title="Cases Over Time",
        labels={'date': 'Date Reported', 'count': 'Number of Cases'}
    )
    timeline_fig.update_traces(line=dict(color='#e74c3c', width=3))
    
    return case_type_fig, status_fig, timeline_fig, filtered_df.to_dict('records')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
