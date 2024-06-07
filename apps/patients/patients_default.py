# Usual Dash dependencies
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd

# Let us import the app object in case we need to define
# callbacks here
from app import app
#for DB needs
from apps import dbconnect as db

# store the layout objects into a variable named layout

# store the layout objects into a variable named layout
layout = dbc.Container(
    [
        html.H2('Patient Information'), # Page Header
        html.Hr(),
        dbc.Card( # Card Container
            [
                dbc.CardBody( # Define Card Contents
                    [
                        html.Div( # Add Profile Btn
                            [
                                # Add profile button will work like a 
                                # hyperlink that leads to another page
                                dbc.Button(
                                    "Add Patients",
                                    href='/patients/patients_profile?mode=add',
                                    style={'backgroundColor': '#FF9D9D', 'border': 'none','color': 'white'}),  
                            ]
                        ),
                        html.Hr(),
                        html.Div( # Create section to show list of movies
                            [
                                html.H4('View Patients'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Title", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='patient_titlefilter',
                                                        placeholder='Search patient name'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                            className='mb-3' # add 1em bottom margin
                                        )
                                    )
                                ),
                                html.Div(
                                    "Table with patients will go here.",
                                    id='patients_patientslist'
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        
    ]
)

################## load list of patients #########################
@app.callback(
    [
        Output('patients_patientslist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('patient_titlefilter', 'value'), # changing the text box value should update the table 
    ]
)

def patient_loadlist(pathname, searchterm):
    if pathname == '/patients':
        if not searchterm:
            return [dbc.Table()]
        # 1. Obtain records from the DB via SQL
        # 2. Create the html element to return to the Div
        sql = """ SELECT firstname as Firstname, lastname as Lastname,  patient_id as ID
            FROM patients 
            WHERE 
        """
        values = []
        cols = ['Firstname', 'Lastname', 'ID']

        if searchterm:
            # We use the operator ILIKE for pattern-matching
            sql += " (Firstname ILIKE %s OR Lastname ILIKE %s)"
            
            # The % before and after the term means that
            # there can be text before and after
            # the search term
            values += [f"%{searchterm}%", f"%{searchterm}%"]

        df = db.querydatafromdatabase(sql, values, cols)

        if df.shape:
            buttons = []
            for patient_id in df['ID']:
                buttons += [
                    html.Div(
                        dbc.Button("Edit", href=f'/patients/patients_profile?mode=edit&id={patient_id}',
                            size = 'sm', color='warning'),
                            style = {'text-align': 'left'}
                    )
                ]
            df['Action'] = buttons
            df = df[['Firstname', 'Lastname', 'Action']]
            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
                    hover=True, size='sm')
            return [table]
        else:
            return ["No record to display"]
    
    else:
        raise PreventUpdate
    
