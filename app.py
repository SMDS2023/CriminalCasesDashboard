"""
Criminal Cases Dashboard - Bulletproof Version
A Dash application for visualizing criminal case data from cases.csv
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# Initialize the Dash app
app = dash.Dash(__name__, 
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# CRITICAL: Define server for deployment
server = app.server

# App title for browser tab
app.title = "Criminal Cases Dashboard"

def load_data():
    """
    Load criminal cases data with maximum error handling
    """
    try:
        # Check if file exists
        if not os.path.exists('cases.csv'):
            print("ERROR: cases.csv file not found!")
            return create_sample_data()
        
        print("Found cases.csv file, attempting to load...")
        
        # Try to load the CSV file
        df = pd.read_csv('cases.csv')
        
        print(f"Successfully loaded CSV with shape: {df.shape}")
        print(f"Columns found: {list(df.columns)}")
        
        # Check if we have any data
        if len(df) == 0:
            print("ERROR: CSV file is empty!")
            return create_sample_data()
        
        # Clean up any potential BOM characters from the CSV
        df.columns = df.columns.str.replace('\ufeff', '')
        
        # Convert dates to datetime if columns exist
        if 'FileDate' in df.columns:
            try:
                df['FileDate'] = pd.to_datetime(df['FileDate'])
                print("Successfully converted FileDate to datetime")
            except:
                print("Warning: Could not convert FileDate to datetime")
        
        if 'OffenseDate' in df.columns:
            try:
                df['OffenseDate'] = pd.to_datetime(df['OffenseDate'])
                print("Successfully converted OffenseDate to datetime")
            except:
                print("Warning: Could not convert OffenseDate to datetime")
        
        # Clean up text fields by stripping whitespace for existing columns
        text_columns = ['Gender', 'Race_Tier_1', 'Lead_Agency', 'ChargeOffenseDescription', 'Lead_Officer']
        for col in text_columns:
            if col in df.columns:
                try:
                    df[col] = df[col].astype(str).str.strip()
                    print(f"Cleaned column: {col}")
                except:
                    print(f"Warning: Could not clean column: {col}")
        
        # Handle missing values for existing columns
        if 'City_Clean' in df.columns:
            df['City_Clean'] = df['City_Clean'].fillna('Unknown')
        if 'Lead_Agency' in df.columns:
            df['Lead_Agency'] = df['Lead_Agency'].fillna('Unknown')
        
        print(f"Data loaded successfully with {len(df)} rows and {len(df.columns)} columns")
        return df
        
    except Exception as e:
        print(f"ERROR loading data: {e}")
        return create_sample_data()

def create_sample_data():
    """
    Create sample data when real data can't be loaded
    """
    print("Creating sample data...")
    sample_data = {
        'CaseNumber': ['SAMPLE001', 'SAMPLE002', 'SAMPLE003', 'SAMPLE004', 'SAMPLE005'],
        'ChargeOffenseDescription': [
            'POSSESSION OF FIREARM BY CONVICTED FELON', 
            'BATTERY ON LAW ENFORCEMENT OFFICER',
            'DRIVING UNDER THE INFLUENCE',
            'POSSESSION OF CONTROLLED SUBSTANCE',
            'THEFT OF MOTOR VEHICLE'
        ],
        'Statute_CaseType': ['Felony', 'Misdemeanor', 'Misdemeanor', 'Felony', 'Felony'],
        'Gender': ['M', 'F', 'M', 'F', 'M'],
        'Race_Tier_1': ['B', 'W', 'H', 'B', 'W'],
        'FileDate': [
            pd.Timestamp('2024-01-01'), 
            pd.Timestamp('2024-01-02'), 
            pd.Timestamp('2024-01-03'),
            pd.Timestamp('2024-01-04'),
            pd.Timestamp('2024-01-05')
        ],
        'Age_At_Offense': [25, 30, 35, 28, 42],
        'Lead_Agency': [
            'ORLANDO POLICE DEPARTMENT', 
            'ORANGE COUNTY SHERIFF', 
            'ORLANDO POLICE DEPARTMENT',
            'ORANGE COUNTY SHERIFF',
            'OCOEE POLICE DEPARTMENT'
        ],
        'City_Clean': ['Orlando', 'Orlando', 'Tampa', 'Orlando', 'Ocoee'],
        'Arrest_vs_NonArrest': ['Arrest', 'Non-Arrest', 'Arrest', 'Arrest', 'Non-Arrest'],
        'YearMonth': ['2024-01', '2024-01', '2024-01', '2024-01', '2024-01'],
        'OffenseWeekday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }
    return pd.DataFrame(sample_data)

# Load the data
print("Starting data load...")
df = load_data()

# Safely get unique values for dropdowns
def safe_get_unique(column_name):
    """Safely get unique values from a column"""
    if column_name in df.columns:
        try:
            return [val for val in df[column_name].dropna().unique() if val]
        except:
            return []
    return []

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
            html.H3(f"{len(df[df['Statute_CaseType'] == 'Felony']) if 'Statute_CaseType' in df.columns else 0}", style={'margin': '0', 'color': '#e74c3c'}),
            html.P("Felonies", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '8px', 'width': '18%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{len(df[df['Statute_CaseType'] == 'Misdemeanor']) if 'Statute_CaseType' in df.columns else 0}", style={'margin': '0', 'color': '#f39c12'}),
            html.P("Misdemeanors", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '8px', 'width': '18%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{df['Lead_Agency'].nunique() if 'Lead_Agency' in df.columns else 0}", style={'margin': '0', 'color': '#27ae60'}),
            html.P("Agencies", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '8px', 'width': '18%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{df['Age_At_Offense'].mean():.1f}" if 'Age_At_Offense' in df.columns and len(df) > 0 else "N/A", style={'margin': '0', 'color': '#9b59b6'}),
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
                        [{'label': case_type, 'value': case_type} for case_type in safe_get_unique('Statute_CaseType')],
                value='all',
                style={'marginBottom': '20px'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '15px'}),
        
        html.Div([
            html.Label("Gender:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='gender-filter',
                options=[{'label': 'All', 'value': 'all'}] + 
                        [{'label': 'Male' if gender == 'M' else 'Female' if gender == 'F' else gender, 'value': gender} 
                         for gender in safe_get_unique('Gender')],
                value='all',
                style={'marginBottom': '20px'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '5px', 'paddingRight': '10px'}),
        
        html.Div([
            html.Label("Race:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='race-filter',
                options=[{'label': 'All', 'value': 'all'}] + 
                        [{'label': race, 'value': race} for race in safe_get_unique('Race_Tier_1')],
                value='all',
                style={'marginBottom': '20px'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '5px', 'paddingRight': '10px'}),
        
        html.Div([
            html.Label("Arrest Type:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='arrest-filter',
                options=[{'label': 'All', 'value': 'all'}] + 
                        [{'label': arrest_type, 'value': arrest_type} for arrest_type in safe_get_unique('Arrest_vs_NonArrest')],
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
                    {"name": "Statute Description", "id": "Statute_Description"},
                    {"name": "Charge Description", "id": "ChargeOffenseDescription"},
                    {"name": "Case Type", "id": "Statute_CaseType"},
                    {"name": "Gender", "id": "Gender"},
                    {"name": "Race", "id": "Race_Tier_1"},
                    {"name": "Age", "id": "Age_At_Offense"},
                    {"name": "City", "id": "City_Clean"},
                    {"name": "Lead Agency", "id": "Lead_Agency"}
                ],
                data=[],  # Will be populated by callback
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
    
    if selected_case_type != 'all' and 'Statute_CaseType' in df.columns:
        filtered_df = filtered_df[filtered_df['Statute_CaseType'] == selected_case_type]
    
    if selected_gender != 'all' and 'Gender' in df.columns:
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
    if selected_race != 'all' and 'Race_Tier_1' in df.columns:
        filtered_df = filtered_df[filtered_df['Race_Tier_1'] == selected_race]
    
    if selected_arrest != 'all' and 'Arrest_vs_NonArrest' in df.columns:
        filtered_df = filtered_df[filtered_df['Arrest_vs_NonArrest'] == selected_arrest]
    
    # Top statute types chart (using Statute_Description instead of ChargeOffenseDescription)
    if 'Statute_Description' in filtered_df.columns and len(filtered_df) > 0:
        statute_counts = filtered_df['Statute_Description'].value_counts().head(15)
        if len(statute_counts) > 0:
            charge_fig = px.bar(
                x=statute_counts.values,
                y=statute_counts.index,
                orientation='h',
                title="Top 15 Statute Types",
                labels={'x': 'Number of Cases', 'y': 'Statute Description'},
                color=statute_counts.values,
                color_continuous_scale='Blues'
            )
            charge_fig.update_layout(showlegend=False, height=400)
        else:
            charge_fig = px.bar(title="Top Statute Types (No data)")
    else:
        charge_fig = px.bar(title="Top Statute Types (Column not found)")
    
    # Case type distribution
    if 'Statute_CaseType' in filtered_df.columns and len(filtered_df) > 0:
        case_type_counts = filtered_df['Statute_CaseType'].value_counts()
        if len(case_type_counts) > 0:
            case_type_fig = px.pie(
                values=case_type_counts.values,
                names=case_type_counts.index,
                title="Distribution by Case Type",
                color_discrete_sequence=['#e74c3c', '#f39c12', '#27ae60']
            )
        else:
            case_type_fig = px.pie(title="Case Types (No data)")
    else:
        case_type_fig = px.pie(title="Case Types (Column not found)")
    
    # Demographics chart (Race and Gender)
    if 'Race_Tier_1' in filtered_df.columns and 'Gender' in filtered_df.columns and len(filtered_df) > 0:
        try:
            demo_df = filtered_df.groupby(['Race_Tier_1', 'Gender']).size().reset_index(name='count')
            if len(demo_df) > 0:
                demographics_fig = px.bar(
                    demo_df,
                    x='Race_Tier_1',
                    y='count',
                    color='Gender',
                    title="Demographics: Race and Gender Distribution",
                    labels={'Race_Tier_1': 'Race', 'count': 'Number of Cases'},
                    color_discrete_map={'M': '#3498db', 'F': '#e91e63'}
                )
            else:
                demographics_fig = px.bar(title="Demographics (No data)")
        except:
            demographics_fig = px.bar(title="Demographics (Error processing data)")
    else:
        demographics_fig = px.bar(title="Demographics (Columns not found)")
    
    # Age distribution
    if 'Age_At_Offense' in filtered_df.columns and len(filtered_df) > 0:
        try:
            age_fig = px.histogram(
                filtered_df,
                x='Age_At_Offense',
                nbins=25,
                title="Age Distribution of Defendants",
                labels={'Age_At_Offense': 'Age at Offense', 'count': 'Number of Cases'},
                color_discrete_sequence=['#3498db']
            )
        except:
            age_fig = px.histogram(title="Age Distribution (Error processing data)")
    else:
        age_fig = px.histogram(title="Age Distribution (Column not found)")
    
    # Timeline chart by month
    if 'YearMonth' in filtered_df.columns and len(filtered_df) > 0:
        try:
            timeline_data = filtered_df.groupby('YearMonth').size().reset_index(name='count')
            timeline_data = timeline_data.sort_values('YearMonth')
            
            if len(timeline_data) > 0:
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
            else:
                timeline_fig = px.line(title="Timeline (No data)")
        except:
            timeline_fig = px.line(title="Timeline (Error processing data)")
    else:
        timeline_fig = px.line(title="Timeline (Column not found)")
    
    # Weekday distribution
    if 'OffenseWeekday' in filtered_df.columns and len(filtered_df) > 0:
        try:
            weekday_counts = filtered_df['OffenseWeekday'].value_counts()
            # Reorder to proper weekday order
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_counts = weekday_counts.reindex([day for day in weekday_order if day in weekday_counts.index])
            
            if len(weekday_counts) > 0:
                weekday_fig = px.bar(
                    x=weekday_counts.index,
                    y=weekday_counts.values,
                    title="Cases by Day of Week",
                    labels={'x': 'Day of Week', 'y': 'Number of Cases'},
                    color=weekday_counts.values,
                    color_continuous_scale='Viridis'
                )
                weekday_fig.update_layout(showlegend=False)
            else:
                weekday_fig = px.bar(title="Weekday Distribution (No data)")
        except:
            weekday_fig = px.bar(title="Weekday Distribution (Error processing data)")
    else:
        weekday_fig = px.bar(title="Weekday Distribution (Column not found)")
    
    # Agency breakdown
    if 'Lead_Agency' in filtered_df.columns and len(filtered_df) > 0:
        try:
            agency_counts = filtered_df['Lead_Agency'].value_counts().head(10)
            if len(agency_counts) > 0:
                agency_fig = px.bar(
                    x=agency_counts.index,
                    y=agency_counts.values,
                    title="Top 10 Lead Agencies",
                    labels={'x': 'Agency', 'y': 'Number of Cases'},
                    color=agency_counts.values,
                    color_continuous_scale='Plasma'
                )
                agency_fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=400)
            else:
                agency_fig = px.bar(title="Agencies (No data)")
        except:
            agency_fig = px.bar(title="Agencies (Error processing data)")
    else:
        agency_fig = px.bar(title="Agencies (Column not found)")
    
    # Table data - only include columns that exist
    available_columns = [col for col in ['CaseNumber', 'FileDate', 'Statute_Description', 'ChargeOffenseDescription', 'Statute_CaseType', 
                        'Gender', 'Race_Tier_1', 'Age_At_Offense', 'City_Clean', 'Lead_Agency'] if col in filtered_df.columns]
    
    if available_columns and len(filtered_df) > 0:
        try:
            table_data = filtered_df[available_columns].head(100).to_dict('records')
        except:
            table_data = [{'Message': 'Error loading table data'}]
    else:
        table_data = [{'Message': 'No data available for table'}]
    
    return charge_fig, case_type_fig, demographics_fig, age_fig, timeline_fig, weekday_fig, agency_fig, table_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
