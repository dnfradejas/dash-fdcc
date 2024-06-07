# Usual Dash dependencies
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.parse import urlparse, parse_qs

# Let us import the app object in case we need to define
# callbacks here
from app import app
#for DB needs
from apps import dbconnect as db

# store the layout objects into a variable named layout
layout = dbc.Container(
    [
        html.Div( # This div shall contain all dcc.Store objects
            [
                dcc.Store(id='appointment_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Appointment Details'), # Page Header
        html.Hr(),
        dbc.Alert(id='appointment_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Appointment Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='appointment_date',
                                placeholder='Date',
                                month_format='MMM Do, YY',
                            ),
                            width=5
                        )
                    ],
                    className='mb-3' # add 1em bottom margin
                ),

                dbc.Row(
                    [
                        dbc.Label("Doctor Name", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='appointment_doctor',                              
                            ),
                            width=5
                        )
                    ],
                    className='mb-3' # add 1em bottom margin
                ),

                dbc.Row(
                    [
                        dbc.Label("Patient Name", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='appointment_patient',
                               
                            ),
                            width=5
                        )
                    ],
                    className='mb-3' # add 1em bottom margin
                ),

                dbc.Row(
                    [
                        dbc.Label("Procedure(s)", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='appointment_procedure',
                                multi=True  # Allow multiple selections
                            ),
                            width=5
                        )
                    ],
                        className='mb-3'  # add 1em bottom margin
                ),

                dbc.Row(
                    [
                        dbc.Label("Total Cost", width=1),
                        dbc.Col(
                            dbc.Input(
                                id='appointment_cost',
                            ),
                            width=5
                        )
                    ],
                        className='mb-3'  # add 1em bottom margin
                ),
            ]
        ),
        # enclosing the checklist in a Div so we can
        # hide it in Add Mode
        # html.Div(
        #     dbc.Row(
        #         [
        #             dbc.Label("Wish to delete?", width=2),
        #             dbc.Col(
        #                 dbc.Checklist(
        #                     id='appointment_profile_removerecord',
        #                     options=[
        #                         {
        #                             'label': "Mark for Deletion",
        #                             'value': 1
        #                         }
        #                     ],
        #                     # I want the label to be bold
        #                     style={'fontWeight':'bold'}, 
        #                 ),
        #                 width=6,
        #             ),
        #         ],
        #         className="mb-3",
        #     ),
        #     id='appointment_removerecord_div',
        # ),

        dbc.Button(
            'Submit',
            id='appointment_submit',
            n_clicks=0, # Initialize number of clicks
            style={'backgroundColor': '#FF9D9D', 'border': 'none','color': 'white'}
        ),
        dbc.Modal( # Modal = dialog box; feedback for successful saving.
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    'Appointment successfully saved!'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/appointments' # Clicking this would lead to a change of pages
                    )
                )
            ],
            centered=True,
            id='appointment_successmodal',
            backdrop='static' # Dialog box does not go away if you click at the background
        )
    ]
)


@app.callback(
    [
        Output('appointment_doctor', 'options'),
        Output('appointment_patient', 'options'),
        Output('appointment_procedure', 'options'),

    ],
    [
        Input('url', 'pathname')
    ]

)
def appointment_loaddropdown(pathname):
    if pathname == '/appointments/appointments_profile':
        sql = """
            SELECT firstname || ' ' || lastname as label, patient_id as value
            FROM patients
            ORDER by label ASC
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        patient_opts = df.to_dict('records')

        sql = """
            SELECT procedure_name as label, procedure_id as value
            FROM procedures
            ORDER BY procedure_name ASC
        """
        values = []
        df = db.querydatafromdatabase(sql, values, cols)
        procedure_opts = df.to_dict('records')

        sql = """
            SELECT firstname || ' ' || lastname as label, doctor_id as value
            FROM doctors
            ORDER BY label ASC
        """
        values = []
        df = db.querydatafromdatabase(sql, values, cols)
        doctor_opts = df.to_dict('records')


    else:
        raise PreventUpdate
    
    return [doctor_opts, patient_opts, procedure_opts]
   



@app.callback(
    Output('appointment_cost', 'value'),
    Input('appointment_procedure', 'value'),
)
def calculate_cost(selected_procedures):
    if selected_procedures is None:
        return None
    
    total_cost = 0

    for procedure_id in selected_procedures:
        sql = """
            SELECT procedure_cost
            FROM procedures
            WHERE procedure_id = %s
        """
        values = [procedure_id]
        cols = ['cost']
        df = db.querydatafromdatabase(sql, values, cols)
        total_cost += df['cost'][0]
    
    return '₱ {:,.2f}'.format(total_cost)

@app.callback(
    [
        # dbc.Alert Properties
        Output('appointment_alert', 'color'),
        Output('appointment_alert', 'children'),
        Output('appointment_alert', 'is_open'),

        # dbc.Modal Properties
        Output('appointment_successmodal', 'is_open')

    ],
    [
        # For buttons, the property n_clicks 
        Input('appointment_submit', 'n_clicks')
    ],
    [
        # The values of the fields are States 
        # They are required in this process but they 
        # do not trigger this callback
        State('appointment_date', 'date'),
        State('appointment_doctor', 'value'),
        State('appointment_patient', 'value'),
        State('appointment_procedure', 'value'),
        State('appointment_cost', 'value'),
        # State('appointment_profile_removerecord', 'value'),

    ]
)
def save_appointment(submitbtn, date, doctor_id, patient_id, procedure_id, cost):
    ctx = dash.callback_context
    # The ctx filter -- ensures that only a change in url will activate this callback
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'appointment_submit' and submitbtn:
            # the submitbtn condition checks if the callback was indeed activated by a click
            # and not by having the submit button appear in the layout
            # Set default outputs
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            # We need to check inputs
            if not date: # If title is blank, not title = True
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Please supply the appointment date.'
            elif not doctor_id:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Please supply the doctor.'
            elif not patient_id: # If title is blank, not title = True
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Please supply the patient name.'
            elif not procedure_id:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Please supply the procedure.'
            elif not cost:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Please supply the total cost.'
            else:
                cost = float(cost.replace('₱', '').replace(',', '').strip())
                
                try:
                    sql = '''
                        INSERT INTO appointments (patient_id, doctor_id, date, total_cost)
                        VALUES (%s, %s, %s, %s)
                        RETURNING appointment_id
                        '''
                    values = [patient_id, doctor_id, date, cost]
                    
                    appointment_id = db.modifydatabasewithreturning(sql, values)[0]
                    for procedure in procedure_id:
                        sql = '''
                            INSERT INTO appointment_procedure (appointment_id, procedure_id)
                            VALUES (%s, %s)
                        '''
                        values = [appointment_id, procedure]
                        db.modifydatabase(sql, values)

                except Exception as e:
                    alert_open = True
                    alert_color = 'danger'
                    alert_text = 'An error occurred. Please try again.'
                # If this is successful, we want the successmodal to show
                modal_open = True
            return [alert_color, alert_text, alert_open, modal_open]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate


