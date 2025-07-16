"""
Enhanced Criminal Cases Dashboard 
Complete analytics with officer performance, statute violations, and secondary charges
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
app.title = "Enhanced Criminal Cases Dashboard"

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
        text_columns = ['Gender', 'Race_Tier_1', 'Lead_Agency', 'ChargeOffenseDescription', 'Lead_Officer', 'Statute_Description', 'Statute']
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
        if 'Lead_Officer' in df.columns:
            df['Lead_Officer'] = df['Lead_Officer'].fillna('Unknown')
        
        # Create officer case counts for analysis
        if 'Lead_Officer' in df.columns:
            df['Officer_Case_Count'] = df.groupby('Lead_Officer')['CaseNumber'].transform('count')
        
        # Flag 790.07 cases
        if 'Statute' in df.columns:
            df['Is_790_07'] = df['Statute'].str.contains('790.07', na=False)
        
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
        'Statute_Description': [
            'Firearm Violations',
            'Battery',
            'DUI',
            'Drug Possession',
            'Theft'
        ],
        'Statute': ['790.23', '784.07', '316.193', '893.13', '812.014'],
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
        'Lead_Officer': [
            'SMITH JOHN',
            'JONES MARY',
            'BROWN DAVID',
            'DAVIS SUSAN',
            'WILSON MIKE'
        ],
        'City_Clean': ['Orlando', 'Orlando', 'Tampa', 'Orlando', 'Ocoee'],
        'Arrest_vs_NonArrest': ['Arrest', 'Non-Arrest', 'Arrest', 'Arrest', 'Non-Arrest'],
        'YearMonth': ['2024-01', '2024-01', '2024-01', '2024-01', '2024-01'],
        'OffenseWeekday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }
    df = pd.DataFrame(sample_data)
    df['Officer_Case_Count'] = df.groupby('Lead_Officer')['CaseNumber'].transform('count')
    df['Is_790_07'] = df['Statute'].str.contains('790.07', na=False)
    return df

# Load the data
print("Starting data load...")
df = load_data()

# Safely get unique values for dropdowns
def safe_get_unique(column_name):
    """Safely get unique values from a column"""
    if column_name in df.columns:
        try:
            return [val for val in df[column_name].dropna().unique() if val and str(val) != 'nan']
        except:
            return []
    return []

# Define the app layout
app.layout = html.Div([
    # Header section
    html.Div([
        html.H1("Enhanced Criminal Cases Dashboard", 
                style={
                    'textAlign': 'center',
                    'color': '#2c3e50',
                    'marginBottom': '10px',
                    'fontFamily': 'Arial, sans-serif'
                }),
        
        html.P(f"Comprehensive analysis of {len(df):,} criminal cases with officer analytics",
               style={
                   'textAlign': 'center',
                   'color': '#7f8c8d',
                   'fontSize': '16px',
                   'marginBottom': '20px'
               })
    ], style={'padding': '15px'}),
    
    # Key metrics row
    html.Div([
        html.Div([
            html.H3(f"{len(df):,}", style={'margin': '0', 'color': '#3498db', 'fontSize': '24px'}),
            html.P("Total Cases", style={'margin': '0', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '15px', 'borderRadius': '8px', 'width': '15%', 'display': 'inline-block', 'margin': '0.5%'}),
        
        html.Div([
            html.H3(f"{len(df[df['Statute_CaseType'] == 'Felony']) if 'Statute_CaseType' in df.columns else 0}", style={'margin': '0', 'color': '#e74c3c', 'fontSize': '24px'}),
            html.P("Felonies", style={'margin': '0', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '15px', 'borderRadius': '8px', 'width': '15%', 'display': 'inline-block', 'margin': '0.5%'}),
        
        html.Div([
            html.H3(f"{df['Lead_Agency'].nunique() if 'Lead_Agency' in df.columns else 0}", style={'margin': '0', 'color': '#27ae60', 'fontSize': '24px'}),
            html.P("Agencies", style={'margin': '0', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '15px', 'borderRadius': '8px', 'width': '15%', 'display': 'inline-block', 'margin': '0.5%'}),
        
        html.Div([
            html.H3(f"{df['Lead_Officer'].nunique() if 'Lead_Officer' in df.columns else 0}", style={'margin': '0', 'color': '#9b59b6', 'fontSize': '24px'}),
            html.P("Officers", style={'margin': '0', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '15px', 'borderRadius': '8px', 'width': '15%', 'display': 'inline-block', 'margin': '0.5%'}),
        
        html.Div([
            html.H3(f"{len(df[df.get('Is_790_07', False)]) if 'Is_790_07' in df.columns else 0}", style={'margin': '0', 'color': '#e67e22', 'fontSize': '24px'}),
            html.P("790.07 Cases", style={'margin': '0', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '15px', 'borderRadius': '8px', 'width': '15%', 'display': 'inline-block', 'margin': '0.5%'}),
        
        html.Div([
            html.H3(f"{df['Age_At_Offense'].mean():.1f}" if 'Age_At_Offense' in df.columns and len(df) > 0 else "N/A", style={'margin': '0', 'color': '#34495e', 'fontSize': '24px'}),
            html.P("Avg Age", style={'margin': '0', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '15px', 'borderRadius': '8px', 'width': '15%', 'display': 'inline-block', 'margin': '0.5%'})
    ], style={'padding': '0 15px', 'marginBottom': '20px'}),
    
    # Enhanced Controls section
    html.Div([
        # First row of filters
        html.Div([
            html.Div([
                html.Label("Agency:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='agency-filter',
                    options=[{'label': 'All Agencies', 'value': 'all'}] + 
                            [{'label': agency, 'value': agency} for agency in safe_get_unique('Lead_Agency')],
                    value='all',
                    style={'marginBottom': '10px', 'fontSize': '12px'}
                )
            ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '10px'}),
            
            html.Div([
                html.Label("Officer:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='officer-filter',
                    options=[{'label': 'All Officers', 'value': 'all'}],
                    value='all',
                    style={'marginBottom': '10px', 'fontSize': '12px'}
                )
            ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '5px', 'paddingRight': '5px'}),
            
            html.Div([
                html.Label("Statute Description:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='statute-filter',
                    options=[{'label': 'All Statutes', 'value': 'all'}] + 
                            [{'label': statute, 'value': statute} for statute in safe_get_unique('Statute_Description')],
                    value='all',
                    style={'marginBottom': '10px', 'fontSize': '12px'}
                )
            ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '5px', 'paddingRight': '5px'}),
            
            html.Div([
                html.Label("Case Type:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='case-type-filter',
                    options=[{'label': 'All Types', 'value': 'all'}] + 
                            [{'label': case_type, 'value': case_type} for case_type in safe_get_unique('Statute_CaseType')],
                    value='all',
                    style={'marginBottom': '10px', 'fontSize': '12px'}
                )
            ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '10px'})
        ]),
        
        # Second row of filters
        html.Div([
            html.Div([
                html.Label("Gender:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='gender-filter',
                    options=[{'label': 'All Genders', 'value': 'all'}] + 
                            [{'label': 'Male' if gender == 'M' else 'Female' if gender == 'F' else gender, 'value': gender} 
                             for gender in safe_get_unique('Gender')],
                    value='all',
                    style={'marginBottom': '10px', 'fontSize': '12px'}
                )
            ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '10px'}),
            
            html.Div([
                html.Label("Race:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='race-filter',
                    options=[{'label': 'All Races', 'value': 'all'}] + 
                            [{'label': race, 'value': race} for race in safe_get_unique('Race_Tier_1')],
                    value='all',
                    style={'marginBottom': '10px', 'fontSize': '12px'}
                )
            ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '5px', 'paddingRight': '5px'}),
            
            html.Div([
                html.Label("Arrest Type:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='arrest-filter',
                    options=[{'label': 'All Types', 'value': 'all'}] + 
                            [{'label': arrest_type, 'value': arrest_type} for arrest_type in safe_get_unique('Arrest_vs_NonArrest')],
                    value='all',
                    style={'marginBottom': '10px', 'fontSize': '12px'}
                )
            ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '5px', 'paddingRight': '5px'}),
            
            html.Div([
                html.Label("790.07 Focus:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='790-filter',
                    options=[
                        {'label': 'All Cases', 'value': 'all'},
                        {'label': '790.07 Cases Only', 'value': 'yes'},
                        {'label': 'Non-790.07 Cases', 'value': 'no'}
                    ],
                    value='all',
                    style={'marginBottom': '10px', 'fontSize': '12px'}
                )
            ], style={'width': '24%', 'display': 'inline-block', 'paddingLeft': '10px'})
        ])
    ], style={'padding': '0 20px', 'marginBottom': '20px'}),
    
    # Charts section
    html.Div([
        # First row - Officer Analytics
        html.Div([
            dcc.Graph(id='officer-performance-chart', style={'height': '350px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='statute-breakdown-chart', style={'height': '350px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        
        # Second row - Demographics and 790.07 Analysis
        html.Div([
            dcc.Graph(id='demographics-chart', style={'height': '350px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='790-analysis-chart', style={'height': '350px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        
        # Third row - Case Type and Timeline
        html.Div([
            dcc.Graph(id='case-type-chart', style={'height': '350px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='timeline-chart', style={'height': '350px'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        
        # Fourth row - Agency Analysis
        html.Div([
            dcc.Graph(id='agency-chart', style={'height': '350px'})
        ], style={'width': '100%', 'padding': '10px'}),
        
        # Data tables section
        html.Div([
            html.H3("Secondary Charges Analysis (790.07 Related)", 
                   style={'textAlign': 'center', 'marginBottom': '15px', 'color': '#2c3e50'}),
            dash_table.DataTable(
                id='secondary-charges-table',
                columns=[],
                data=[],
                style_cell={'textAlign': 'left', 'padding': '8px', 'fontSize': '11px'},
                style_header={'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#fadbd8'},
                page_size=15,
                sort_action="native",
                filter_action="native"
            )
        ], style={'padding': '15px'}),
        
        html.Div([
            html.H3("Detailed Case Records", 
                   style={'textAlign': 'center', 'marginBottom': '15px', 'color': '#2c3e50'}),
            dash_table.DataTable(
                id='cases-table',
                columns=[
                    {"name": "Case Number", "id": "CaseNumber"},
                    {"name": "Officer", "id": "Lead_Officer"},
                    {"name": "Agency", "id": "Lead_Agency"},
                    {"name": "Statute", "id": "Statute"},
                    {"name": "Statute Description", "id": "Statute_Description"},
                    {"name": "Case Type", "id": "Statute_CaseType"},
                    {"name": "Gender", "id": "Gender"},
                    {"name": "Race", "id": "Race_Tier_1"},
                    {"name": "Age", "id": "Age_At_Offense"},
                    {"name": "File Date", "id": "FileDate"},
                    {"name": "City", "id": "City_Clean"}
                ],
                data=[],
                style_cell={'textAlign': 'left', 'padding': '8px', 'fontSize': '11px'},
                style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#ecf0f1'},
                page_size=25,
                sort_action="native",
                filter_action="native"
            )
        ], style={'padding': '15px'})
    ])
], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

# Callback to update officer dropdown based on agency selection
@app.callback(
    Output('officer-filter', 'options'),
    Input('agency-filter', 'value')
)
def update_officer_dropdown(selected_agency):
    if selected_agency == 'all' or not selected_agency:
        officers = safe_get_unique('Lead_Officer')
    else:
        if 'Lead_Agency' in df.columns and 'Lead_Officer' in df.columns:
            agency_df = df[df['Lead_Agency'] == selected_agency]
            officers = [val for val in agency_df['Lead_Officer'].dropna().unique() if val and str(val) != 'nan']
        else:
            officers = []
    
    return [{'label': 'All Officers', 'value': 'all'}] + [{'label': officer, 'value': officer} for officer in officers]

# Main callback for updating all charts and tables
@app.callback(
    [Output('officer-performance-chart', 'figure'),
     Output('statute-breakdown-chart', 'figure'),
     Output('demographics-chart', 'figure'),
     Output('790-analysis-chart', 'figure'),
     Output('case-type-chart', 'figure'),
     Output('timeline-chart', 'figure'),
     Output('agency-chart', 'figure'),
     Output('secondary-charges-table', 'data'),
     Output('secondary-charges-table', 'columns'),
     Output('cases-table', 'data')],
    [Input('agency-filter', 'value'),
     Input('officer-filter', 'value'),
     Input('statute-filter', 'value'),
     Input('case-type-filter', 'value'),
     Input('gender-filter', 'value'),
     Input('race-filter', 'value'),
     Input('arrest-filter', 'value'),
     Input('790-filter', 'value')]
)
def update_dashboard(selected_agency, selected_officer, selected_statute, selected_case_type, 
                    selected_gender, selected_race, selected_arrest, selected_790):
    """
    Update all dashboard components based on filter selections
    """
    # Filter data based on selections
    filtered_df = df.copy()
    
    if selected_agency != 'all' and 'Lead_Agency' in df.columns:
        filtered_df = filtered_df[filtered_df['Lead_Agency'] == selected_agency]
    
    if selected_officer != 'all' and 'Lead_Officer' in df.columns:
        filtered_df = filtered_df[filtered_df['Lead_Officer'] == selected_officer]
    
    if selected_statute != 'all' and 'Statute_Description' in df.columns:
        filtered_df = filtered_df[filtered_df['Statute_Description'] == selected_statute]
    
    if selected_case_type != 'all' and 'Statute_CaseType' in df.columns:
        filtered_df = filtered_df[filtered_df['Statute_CaseType'] == selected_case_type]
    
    if selected_gender != 'all' and 'Gender' in df.columns:
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
    if selected_race != 'all' and 'Race_Tier_1' in df.columns:
        filtered_df = filtered_df[filtered_df['Race_Tier_1'] == selected_race]
    
    if selected_arrest != 'all' and 'Arrest_vs_NonArrest' in df.columns:
        filtered_df = filtered_df[filtered_df['Arrest_vs_NonArrest'] == selected_arrest]
    
    if selected_790 == 'yes' and 'Is_790_07' in df.columns:
        filtered_df = filtered_df[filtered_df['Is_790_07'] == True]
    elif selected_790 == 'no' and 'Is_790_07' in df.columns:
        filtered_df = filtered_df[filtered_df['Is_790_07'] == False]
    
    # Officer Performance Chart
    if 'Lead_Officer' in filtered_df.columns and len(filtered_df) > 0:
        try:
            officer_counts = filtered_df['Lead_Officer'].value_counts().head(15)
            if len(officer_counts) > 0:
                officer_fig = px.bar(
                    x=officer_counts.values,
                    y=officer_counts.index,
                    orientation='h',
                    title="Top 15 Officers by Case Volume",
                    labels={'x': 'Number of Cases', 'y': 'Officer'},
                    color=officer_counts.values,
                    color_continuous_scale='Blues'
                )
                officer_fig.update_layout(showlegend=False, height=350)
            else:
                officer_fig = px.bar(title="Officer Performance (No data)")
        except:
            officer_fig = px.bar(title="Officer Performance (Error)")
    else:
        officer_fig = px.bar(title="Officer Performance (No data available)")
    
    # Statute Breakdown Chart
    if 'Statute_Description' in filtered_df.columns and len(filtered_df) > 0:
        try:
            statute_counts = filtered_df['Statute_Description'].value_counts().head(10)
            if len(statute_counts) > 0:
                statute_fig = px.pie(
                    values=statute_counts.values,
                    names=statute_counts.index,
                    title="Statute Distribution"
                )
            else:
                statute_fig = px.pie(title="Statute Distribution (No data)")
        except:
            statute_fig = px.pie(title="Statute Distribution (Error)")
    else:
        statute_fig = px.pie(title="Statute Distribution (No data available)")
    
    # Demographics Chart
    if 'Race_Tier_1' in filtered_df.columns and 'Gender' in filtered_df.columns and len(filtered_df) > 0:
        try:
            demo_df = filtered_df.groupby(['Race_Tier_1', 'Gender']).size().reset_index(name='count')
            if len(demo_df) > 0:
                demographics_fig = px.bar(
                    demo_df,
                    x='Race_Tier_1',
                    y='count',
                    color='Gender',
                    title="Demographics: Race and Gender",
                    labels={'Race_Tier_1': 'Race', 'count': 'Number of Cases'},
                    color_discrete_map={'M': '#3498db', 'F': '#e91e63'}
                )
            else:
                demographics_fig = px.bar(title="Demographics (No data)")
        except:
            demographics_fig = px.bar(title="Demographics (Error)")
    else:
        demographics_fig = px.bar(title="Demographics (No data available)")
    
    # 790.07 Analysis Chart
    if 'Is_790_07' in filtered_df.columns and 'Age_At_Offense' in filtered_df.columns and len(filtered_df) > 0:
        try:
            df_790 = filtered_df[filtered_df['Is_790_07'] == True]
            if len(df_790) > 0:
                analysis_fig = px.histogram(
                    df_790,
                    x='Age_At_Offense',
                    nbins=15,
                    title="Age Distribution for 790.07 Cases",
                    labels={'Age_At_Offense': 'Age at Offense', 'count': 'Number of Cases'},
                    color_discrete_sequence=['#e74c3c']
                )
            else:
                analysis_fig = px.histogram(title="790.07 Analysis (No 790.07 cases found)")
        except:
            analysis_fig = px.histogram(title="790.07 Analysis (Error)")
    else:
        analysis_fig = px.histogram(title="790.07 Analysis (No data available)")
    
    # Case Type Chart
    if 'Statute_CaseType' in filtered_df.columns and len(filtered_df) > 0:
        try:
            case_type_counts = filtered_df['Statute_CaseType'].value_counts()
            if len(case_type_counts) > 0:
                case_type_fig = px.pie(
                    values=case_type_counts.values,
                    names=case_type_counts.index,
                    title="Case Type Distribution",
                    color_discrete_sequence=['#e74c3c', '#f39c12', '#27ae60']
                )
            else:
                case_type_fig = px.pie(title="Case Types (No data)")
        except:
            case_type_fig = px.pie(title="Case Types (Error)")
    else:
        case_type_fig = px.pie(title="Case Types (No data available)")
    
    # Timeline Chart
    if 'YearMonth' in filtered_df.columns and len(filtered_df) > 0:
        try:
            timeline_data = filtered_df.groupby('YearMonth').size().reset_index(name='count')
            timeline_data = timeline_data.sort_values('YearMonth')
            
            if len(timeline_data) > 0:
                timeline_fig = px.line(
                    timeline_data,
                    x='YearMonth',
                    y='count',
                    title="Cases Over Time",
                    labels={'YearMonth': 'Year-Month', 'count': 'Number of Cases'},
                    markers=True
                )
                timeline_fig.update_traces(line=dict(color='#e74c3c', width=3))
                timeline_fig.update_xaxes(tickangle=45)
            else:
                timeline_fig = px.line(title="Timeline (No data)")
        except:
            timeline_fig = px.line(title="Timeline (Error)")
    else:
        timeline_fig = px.line(title="Timeline (No data available)")
    
    # Agency Chart
    if 'Lead_Agency' in filtered_df.columns and len(filtered_df) > 0:
        try:
            agency_counts = filtered_df['Lead_Agency'].value_counts().head(10)
            if len(agency_counts) > 0:
                agency_fig = px.bar(
                    x=agency_counts.index,
                    y=agency_counts.values,
                    title="Top 10 Agencies by Case Volume",
                    labels={'x': 'Agency', 'y': 'Number of Cases'},
                    color=agency_counts.values,
                    color_continuous_scale='Viridis'
                )
                agency_fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=350)
            else:
                agency_fig = px.bar(title="Agencies (No data)")
        except:
            agency_fig = px.bar(title="Agencies (Error)")
    else:
        agency_fig = px.bar(title="Agencies (No data available)")
    
    # Secondary Charges Table (790.07 focus)
    secondary_data = []
    secondary_columns = []
    
    if 'Is_790_07' in filtered_df.columns and len(filtered_df) > 0:
        try:
            df_790 = filtered_df[filtered_df['Is_790_07'] == True]
            if len(df_790) > 0:
                # Group by case number to see what other charges appear with 790.07
                case_groups = df_790.groupby('CaseNumber').agg({
                    'ChargeOffenseDescription': lambda x: ', '.join(x.unique()),
                    'Statute_Description': lambda x: ', '.join(x.unique()),
                    'Lead_Officer': 'first',
                    'Age_At_Offense': 'first',
                    'Gender': 'first',
                    'Race_Tier_1': 'first'
                }).reset_index()
                
                secondary_data = case_groups.head(50).to_dict('records')
                secondary_columns = [
                    {"name": "Case Number", "id": "CaseNumber"},
                    {"name": "Officer", "id": "Lead_Officer"},
                    {"name": "All Charges", "id": "ChargeOffenseDescription"},
                    {"name": "All Statutes", "id": "Statute_Description"},
                    {"name": "Age", "id": "Age_At_Offense"},
                    {"name": "Gender", "id": "Gender"},
                    {"name": "Race", "id": "Race_Tier_1"}
                ]
        except Exception as e:
            print(f"Error creating secondary charges table: {e}")
    
    # Main Cases Table
    available_columns = [col for col in ['CaseNumber', 'Lead_Officer', 'Lead_Agency', 'Statute', 'Statute_Description', 'Statute_CaseType', 
                        'Gender', 'Race_Tier_1', 'Age_At_Offense', 'FileDate', 'City_Clean'] if col in filtered_df.columns]
    
    if available_columns and len(filtered_df) > 0:
        try:
            table_data = filtered_df[available_columns].head(100).to_dict('records')
        except:
            table_data = [{'Message': 'Error loading table data'}]
    else:
        table_data = [{'Message': 'No data available for table'}]
    
    return (officer_fig, statute_fig, demographics_fig, analysis_fig, case_type_fig, 
            timeline_fig, agency_fig, secondary_data, secondary_columns, table_data)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
