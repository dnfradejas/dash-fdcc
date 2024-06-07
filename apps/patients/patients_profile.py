# Usual Dash dependencies
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from urllib.parse import urlparse, parse_qs
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
        html.Div( # This div shall contain all dcc.Store objects
            [
                dcc.Store(id='patients_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Patient Details'), # Page Header
        html.Hr(),
        dbc.Alert(id='patient_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
                # Form fields here
                dbc.Row(
                    [
                        dbc.Label("First Name", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text', 
                                id='patientprofile_firstname',
                                
                            ),
                            width=3
                        )
                    ],
                    className='mb-3' # add 1em bottom margin
                ),
                dbc.Row(
                    [
                        dbc.Label("Middle Name", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text', 
                                id='patientprofile_middlename',
                                
                            ),
                            width=3
                        )
                    ],
                    className='mb-3' # add 1em bottom margin
                ),
                dbc.Row(
                    [
                        dbc.Label("Last Name", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text', 
                                id='patientprofile_lastname',
                                
                            ),
                            width=3
                        )
                    ],
                    className='mb-3' # add 1em bottom margin
                ),
                dbc.Row(
                    [
                        dbc.Label("Sex", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='patientprofile_sex',                              
                            ),
                            width=2
                        )
                    ],
                    className='mb-3' # add 1em bottom margin
                ),
                dbc.Row(
                    [
                        dbc.Label("Birthday", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='patientprofile_birthday',
                                placeholder='Birthday',
                                month_format='MMM Do, YY',
                            ),
                            width=5
                        )
                    ],
                    className='mb-3' # add 1em bottom margin
                ),

            ]
        ),
        # enclosing the checklist in a Div so we can
        # hide it in Add Mode
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Wish to delete?", width=2),
                    dbc.Col(
                        dbc.Checklist(
                            id='patientprofile_removerecord',
                            options=[
                                {
                                    'label': "Mark for Deletion",
                                    'value': 1
                                }
                            ],
                            # I want the label to be bold
                            style={'fontWeight':'bold'}, 
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            id='patientpofile_removerecord_div'
        ),

        dbc.Button(
            'Submit',
            id='patientprofile_submit',
            n_clicks=0, # Initialize number of clicks,
            style={'backgroundColor': '#FF9D9D', 
                   'border': 'none',
                   'color': 'white'}
        ),
        dbc.Modal( # Modal = dialog box; feedback for successful saving.
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    'Successfully added/modified the patient!'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/patients' # Clicking this would lead to a change of pages
                    )
                )
            ],
            centered=True,
            id='patientprofile_successmodal',
            backdrop='static' # Dialog box does not go away if you click at the background
        )
    ]
)

@app.callback(
    [
        # load sexes in the database to dropdown
        Output('patientprofile_sex', 'options'),
        Output('patients_toload', 'data'),
        Output('patientpofile_removerecord_div', 'style')
    ],
    [
        Input('url', 'pathname') # load when the page loads
    ],
    [
        State('url', 'search') 
    ]

)
def load_sex_dropdown(pathname, search):
    """
    This function will load the sex options from the database

    Args:
        pathname (str): The current URL pathname

    """
    if pathname == '/patients/patients_profile':
        sql = """SELECT sex_name as label, sex_id as value 
                 FROM sex
        """
        
        values = [] #blank to be a place holder
        cols = ['label','value']
        df = db.querydatafromdatabase(sql, values, cols)
        sex_opts = df.to_dict('records')

        # are we on add or edit mode?
        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0

        # to show the remove option?
        removediv_style = {'display': 'none'} if not to_load else False
        # Convert the list of strings into a list of dictionaries

    
    else:
        raise PreventUpdate
    return [sex_opts,to_load, removediv_style]

@app.callback(
    [
        # dbc.Alert Properties
        Output('patient_alert', 'color'),
        Output('patient_alert', 'children'),
        Output('patient_alert', 'is_open'),

        # dbc.Modal Properties
        Output('patientprofile_successmodal', 'is_open'),
    ],
    [
        Input('patientprofile_submit', 'n_clicks')
    ],
    [
        State('patientprofile_firstname', 'value'),
        State('patientprofile_middlename', 'value'),
        State('patientprofile_lastname', 'value'),
        State('patientprofile_sex', 'value'),
        State('patientprofile_birthday', 'date'),
        State('url', 'search'),
        State('patientprofile_removerecord', 'value'),
    ]
)

def save_patient(submitbtn, firstname, middlename, 
                 lastname, sex, birthday, search, removerecord):
    ctx = dash.callback_context
    # The ctx filter ensure that only a a change in url will trigger the callback
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'patientprofile_submit' and submitbtn:
            # 1. Check if the fields are empty
            
            # set default outputs
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not firstname: # if firstname is blank, not firstname = True
                alert_open = True
                alert_color = 'danger'
                alert_text = 'First Name is required'
            elif not middlename:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Middle Name is required'
            elif not lastname:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Last Name is required'
            elif not sex:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'sex is required'
            elif not birthday:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Birthday is required'
            else:
                # 2. Save the record to the database
                
                # # parse or decode the 'mode' portion of the search queries 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]

                if create_mode == 'add':
                    sql = """INSERT INTO patients (firstname, middlename, lastname, 
                                                   sex_id, birthday) 
                                VALUES (%s, %s, %s, %s, %s)"""
                    values = [firstname, middlename, lastname, sex, birthday]               
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    patient_id = parse_qs(parsed.query)['id'][0]

                    # save the update to db
                    sql = """UPDATE patients 
                             SET 
                                firstname = %s, 
                                middlename = %s, 
                                lastname = %s,
                                sex_id = %s,
                                birthday = %s
                            WHERE
                                patient_id = %s

                    """
                    values = [firstname, middlename, lastname, sex, birthday, patient_id]
                # save to database
                try:
                    # save to dabase
                    db.modifydatabase(sql, values)

                    # if successful, show the modal
                    modal_open = True

                except Exception as e:
                    if 'unique constraint' in str(e).lower():
                        alert_open = True
                        alert_color = 'danger'
                        alert_text = 'Patient already exists'
                    else:
                        alert_open = True
                        alert_color = 'danger'
                        alert_text = 'An error occurred. Please try again.'
                     
            return [alert_color, alert_text, alert_open, modal_open]
        
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate


@app.callback(
    [
        Output('patientprofile_firstname', 'value'),
        Output('patientprofile_middlename', 'value'),
        Output('patientprofile_lastname', 'value'),
        Output('patientprofile_sex', 'value'),
        Output('patientprofile_birthday', 'date'),
    ],
    [
        Input('patients_toload', 'modified_timestamp')
    ],
    [
        State('patients_toload', 'data'),
        State('url', 'search'),
    ]
)
def patientprofile_loadprofile(timestamp, toload, search):
    """
    This function will load the profile of the patient
    """
    if toload:
        parsed = urlparse(search)
        patient_id = parse_qs(parsed.query)['id'][0]
        sql = """SELECT firstname, middlename, lastname, sex_id, birthday
                FROM patients
                WHERE patient_id = %s"""
        values = [patient_id]
        cols = ['firstname', 'middlename', 'lastname','sex_id', 'birthday']

        df = db.querydatafromdatabase(sql, values, cols)

        firstname = df.loc[0, 'firstname']
        middlename = df.loc[0, 'middlename']
        lastname = df.loc[0, 'lastname']
        sex_id = int(df.loc[0, 'sex_id'])
        birthday = df.loc[0, 'birthday']

        return [firstname, middlename, lastname, sex_id, birthday]
    else:
        raise PreventUpdate