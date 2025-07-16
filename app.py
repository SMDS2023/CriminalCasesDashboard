"""
Criminal Cases Dashboard - Customized for Actual Data
A Dash application for visualizing criminal case data from cases.csv
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime

# Initialize the Dash app
app = dash.Dash(__name__, 
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# CRITICAL: Define server for deployment
server = app.server

# App title for browser tab
app.title = "Criminal Cases Dashboard"

def load_data():
    """
    Load criminal cases data from cases.csv
    """
    try:
        # Load the CSV file
        df = pd.read_csv('cases.csv')
        
        # Clean up any potential BOM characters from the CSV
        df.columns = df.columns.str.replace('\ufeff', '')
        
        # Convert dates to datetime
        df['FileDate'] = pd.to_datetime(df['FileDate'])
        df['OffenseDate'] = pd.to_datetime(df['OffenseDate'])
        
        # Clean up text fields by stripping whitespace
        text_columns = ['Gender', 'Race_Tier_1', 'Lead_Agency', 'ChargeOffenseDescription', 'Lead_Officer']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Handle missing values
        df['City_Clean'] = df['City_Clean'].fillna('Unknown')
        df['Lead_Agency'] = df['Lead_Agency'].fillna('Unknown')
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return sample data if CSV fails to load
        sample_data = {
            'CaseNumber': ['Sample1', 'Sample2'],
            'ChargeOffenseDescription': ['Sample Charge', 'Sample Charge 2'],
            'Statute_CaseType': ['Felony', 'Misdemeanor'],
            'Gender': ['M', 'F'],
            'FileDate': [pd.Timestamp('2024-01-01'), pd.Timestamp('2024-01-02')],
            'Age_At_Offense': [25, 30],
            'Lead_Agency': ['Sample Agency', 'Sample Agency 2']
        }
        return pd.DataFrame(sample_data)

# Load the data
df = load_data()

# Define the app layout
app.layout = html.Div([
    # Header section
    html.Div([
        html.H1("Criminal Cases Dashboard", 
                style={
                    'textAlign': 'center',
                    'color': '#2c3e50',
                    'marginBottom': '20px',
                    'fontFamily': 'Arial, sans-serif'
                }),
        
        html.P(f"Analysis of {len(df):,} criminal cases",
               style={
                   'textAlign': 'center',
                   'color': '#7f8c8d',
                   'fontSize': '18px',
                   'marginBottom': '30px'
               })
    ], style={'padding': '20px'}),
    
    # Key metrics row
    html.Div([
        html.Div([
            html.H3(f"{len(df):,}", style={'margin': '0', 'color': '#3498db'}),
            html.P("Total Cases", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '8px', 'width': '18%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{len(df[df['Statute_CaseType'] == 'Felony'])}", style={'margin': '0', 'color': '#e74c3c'}),
            html.P("Felonies", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '8px', 'width': '18%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{len(df[df['Statute_CaseType'] == 'Misdemeanor'])}", style={'margin': '0', 'color': '#f39c12'}),
            html.P("Misdemeanors", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '8px', 'width': '18%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{df['Lead_Agency'].nunique()}", style={'margin': '0', 'color': '#27ae60'}),
            html.P("Agencies", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '8px', 'width': '18%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{df['Age_At_Offense'].mean():.1f}", style={'margin': '0', 'color': '#9b59b6'}),
            html.P("Avg Age", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '8px', 'width': '18%', 'display': 'inline-block', 'margin': '1%'})
    ], style={'padding': '0 20px', 'marginBottom': '30px'}),
    
    # Controls section
    html.Div([
        html.Div([
            html.Label("Case Type:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='case-type-filter',
                options=[{'label': 'All', 'value': 'all'}] + 
                        [{'label': case_type, 'value': case_type} for case_type in ['Felony', 'Misdemeanor', 'Various Violations']],
                value='all',
                style={'marginBottom': '20px'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '15px'}),
        
        html.Div([
            html.Label("Gender:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='gender-filter',
                options=[{'label': 'All', 'value': 'all'}] + 
                        [{'label': 'Male', 'value': 'M'}, {'label': 'Female', 'value': 'F'}],
                value='all',
                style={'marginBottom': '20px'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '5px', 'paddingRight': '10px'}),
        
        html.Div([
            html.Label("Race:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='race-filter',
                options=[{'label': 'All', 'value': 'all'}] + 
                        [{'label': race, 'value': race} for race in df['Race_Tier_1'].dropna().unique()],
                value='all',
                style={'marginBottom': '20px'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '5px', 'paddingRight': '10px'}),
        
        html.Div([
            html.Label("Arrest Type:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='arrest-filter',
                options=[{'label': 'All', 'value': 'all'}] + 
                        [{'label': arrest_type, 'value': arrest_type} for arrest_type in df['Arrest_vs_NonArrest'].dropna().unique()],
                value='all',
                style={'marginBottom': '20px'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '15px'})
    ], style={'padding': '0 40px'}),
    
    # Charts section
    html.Div([
        # First row of charts
        html.Div([
            dcc.Graph(id='charge-type-chart', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px'}),
        
        html.Div([
            dcc.Graph(id='case-type-chart', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px'}),
        
        # Second row of charts
        html.Div([
            dcc.Graph(id='demographics-chart', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px'}),
        
        html.Div([
            dcc.Graph(id='age-distribution-chart', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px'}),
        
        # Third row of charts
        html.Div([
            dcc.Graph(id='timeline-chart', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px'}),
        
        html.Div([
            dcc.Graph(id='weekday-chart', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px'}),
        
        # Agency breakdown
        html.Div([
            dcc.Graph(id='agency-chart', style={'height': '400px'})
        ], style={'width': '100%', 'padding': '20px'}),
        
        # Data table
        html.Div([
            html.H3("Case Details", style={'textAlign': 'center', 'marginBottom': '20px'}),
            dash_table.DataTable(
                id='cases-table',
                columns=[
                    {"name": "Case Number", "id": "CaseNumber"},
                    {"name": "File Date", "id": "FileDate", "type": "datetime"},
                    {"name": "Charge Description", "id": "ChargeOffenseDescription"},
                    {"name": "Case Type", "id": "Statute_CaseType"},
                    {"name": "Gender", "id": "Gender"},
                    {"name": "Race", "id": "Race_Tier_1"},
                    {"name": "Age", "id": "Age_At_Offense"},
                    {"name": "City", "id": "City_Clean"},
                    {"name": "Lead Agency", "id": "Lead_Agency"}
                ],
                data=df.head(100).to_dict('records'),
                style_cell={'textAlign': 'left', 'padding': '8px', 'fontSize': '11px'},
                style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#ecf0f1'},
                page_size=25,
                sort_action="native",
                filter_action="native"
            )
        ], style={'padding': '20px'})
    ])
], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

# Callback for updating charts based on filters
@app.callback(
    [Output('charge-type-chart', 'figure'),
     Output('case-type-chart', 'figure'),
     Output('demographics-chart', 'figure'),
     Output('age-distribution-chart', 'figure'),
     Output('timeline-chart', 'figure'),
     Output('weekday-chart', 'figure'),
     Output('agency-chart', 'figure'),
     Output('cases-table', 'data')],
    [Input('case-type-filter', 'value'),
     Input('gender-filter', 'value'),
     Input('race-filter', 'value'),
     Input('arrest-filter', 'value')]
)
def update_dashboard(selected_case_type, selected_gender, selected_race, selected_arrest):
    """
    Update all dashboard components based on filter selections
    """
    # Filter data based on selections
    filtered_df = df.copy()
    
    if selected_case_type != 'all':
        filtered_df = filtered_df[filtered_df['Statute_CaseType'] == selected_case_type]
    
    if selected_gender != 'all':
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
    if selected_race != 'all':
        filtered_df = filtered_df[filtered_df['Race_Tier_1'] == selected_race]
    
    if selected_arrest != 'all':
        filtered_df = filtered_df[filtered_df['Arrest_vs_NonArrest'] == selected_arrest]
    
    # Top charge types chart
    charge_counts = filtered_df['ChargeOffenseDescription'].value_counts().head(15)
    charge_fig = px.bar(
        x=charge_counts.values,
        y=charge_counts.index,
        orientation='h',
        title="Top 15 Charge Types",
        labels={'x': 'Number of Cases', 'y': 'Charge Description'},
        color=charge_counts.values,
        color_continuous_scale='Blues'
    )
    charge_fig.update_layout(showlegend=False, height=400)
    
    # Case type distribution
    case_type_counts = filtered_df['Statute_CaseType'].value_counts()
    case_type_fig = px.pie(
        values=case_type_counts.values,
        names=case_type_counts.index,
        title="Distribution by Case Type",
        color_discrete_sequence=['#e74c3c', '#f39c12', '#27ae60']
    )
    
    # Demographics chart (Race and Gender)
    demo_df = filtered_df.groupby(['Race_Tier_1', 'Gender']).size().reset_index(name='count')
    demographics_fig = px.bar(
        demo_df,
        x='Race_Tier_1',
        y='count',
        color='Gender',
        title="Demographics: Race and Gender Distribution",
        labels={'Race_Tier_1': 'Race', 'count': 'Number of Cases'},
        color_discrete_map={'M': '#3498db', 'F': '#e91e63'}
    )
    
    # Age distribution
    age_fig = px.histogram(
        filtered_df,
        x='Age_At_Offense',
        nbins=25,
        title="Age Distribution of Defendants",
        labels={'Age_At_Offense': 'Age at Offense', 'count': 'Number of Cases'},
        color_discrete_sequence=['#3498db']
    )
    
    # Timeline chart by month
    timeline_data = filtered_df.groupby('YearMonth').size().reset_index(name='count')
    timeline_data = timeline_data.sort_values('YearMonth')
    
    timeline_fig = px.line(
        timeline_data,
        x='YearMonth',
        y='count',
        title="Cases Filed Over Time (by Month)",
        labels={'YearMonth': 'Year-Month', 'count': 'Number of Cases'},
        markers=True
    )
    timeline_fig.update_traces(line=dict(color='#e74c3c', width=3))
    timeline_fig.update_xaxes(tickangle=45)
    
    # Weekday distribution
    weekday_counts = filtered_df['OffenseWeekday'].value_counts()
    # Reorder to proper weekday order
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_counts = weekday_counts.reindex([day for day in weekday_order if day in weekday_counts.index])
    
    weekday_fig = px.bar(
        x=weekday_counts.index,
        y=weekday_counts.values,
        title="Cases by Day of Week",
        labels={'x': 'Day of Week', 'y': 'Number of Cases'},
        color=weekday_counts.values,
        color_continuous_scale='Viridis'
    )
    weekday_fig.update_layout(showlegend=False)
    
    # Agency breakdown
    agency_counts = filtered_df['Lead_Agency'].value_counts().head(10)
    agency_fig = px.bar(
        x=agency_counts.index,
        y=agency_counts.values,
        title="Top 10 Lead Agencies",
        labels={'x': 'Agency', 'y': 'Number of Cases'},
        color=agency_counts.values,
        color_continuous_scale='Plasma'
    )
    agency_fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=400)
    
    # Table data
    table_columns = ['CaseNumber', 'FileDate', 'ChargeOffenseDescription', 'Statute_CaseType', 
                    'Gender', 'Race_Tier_1', 'Age_At_Offense', 'City_Clean', 'Lead_Agency']
    table_data = filtered_df[table_columns].head(100).to_dict('records')
    
    return charge_fig, case_type_fig, demographics_fig, age_fig, timeline_fig, weekday_fig, agency_fig, table_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
