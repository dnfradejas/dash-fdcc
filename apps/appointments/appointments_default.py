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
        html.H2('Appointment Information'), # Page Header
        html.Hr(),
        dbc.Card( # Card Container
            [
                dbc.CardBody( # Define Card Contents
                    [
                        html.Div( # Add Movie Btn
                            [
                                # Add movie button will work like a 
                                # hyperlink that leads to another page
                                dbc.Button(
                                    "Add Appointment",
                                    href='/appointments/appointments_profile?mode=add',
                                    style={'backgroundColor': '#FF9D9D', 'border': 'none','color': 'white'}
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div( # Create section to show list of movies
                            [
                                html.H4('Browse Appointments'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Title", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='appointments_titlefilter',
                                                        placeholder='Search Name / Appointment Date'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                            className='mb-3' # add 1em bottom margin
                                        )
                                    )
                                ),
                                html.Div(
                                    "Table with movies will go here.",
                                    id='appointments_applist'
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
        Output('appointments_applist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('appointments_titlefilter', 'value'), # changing the text box value should update the table
    ]
)
def patient_loadlist(pathname, searchterm):
    if pathname == '/appointments':
        if not searchterm:
            return [dbc.Table()]
        # 1. Obtain records from the DB via SQL
        # 2. Create the html element to return to the Div

        sql = """SELECT 
                    p.firstname || ' ' || p.lastname as Name, 
                    d.firstname || ' ' || d.lastname as Doctor, 
                    STRING_AGG(pr.procedure_name, ', ') as Procedures,
                    a.total_cost, 
                    a.date as appointment_date

                FROM 
                    appointments as a
                LEFT JOIN 
                    doctors as d on d.doctor_id = a.doctor_id
                LEFT JOIN 
                    patients as p on p.patient_id = a.patient_id
                LEFT JOIN 
                    appointment_procedure as ap on ap.appointment_id = a.appointment_id
                LEFT JOIN 
                    procedures as pr on pr.procedure_id = ap.procedure_id
                
                WHERE (p.firstname ILIKE %s OR p.lastname ILIKE %s) 
                GROUP BY 
                    Name, Doctor, a.total_cost, appointment_date
                

        """
        values = []
        cols = ['Name', 'Doctor', 'Procedures', 'Cost', 'Appointment Date']

        if searchterm:
            
            # The % before and after the term means that
            # there can be text before and after
            # the search term
            values += [f"%{searchterm}%", f"%{searchterm}%"]

        df = db.querydatafromdatabase(sql, values, cols)
        df = df[['Name', 'Doctor', 'Procedures', 'Cost', 'Appointment Date']]
        df['Cost'] = df['Cost'].apply(lambda x: f'₱ {x:,.2f}')
        df = df.sort_values('Appointment Date', ascending=False)
        
        table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
                hover=True, size='sm')
        return [table]
    else:
        raise PreventUpdate
    
# @app.callback(
#     [
#         Output('moviehome_movielist', 'children')
#     ],
#     [
#         Input('url', 'pathname'),
#         Input('moviehome_titlefilter', 'value'), # changing the text box value should update the table 
#     ]
# )

# def moviehome_loadmovielist(pathname, searchterm):
#     if pathname == '/movies':
#         # 1. Obtain records from the DB via SQL
#         # 2. Create the html element to return to the Div
#         sql = """ SELECT movie_name, genre_name, movie_id
#             FROM movies m
#                 INNER JOIN genres g ON m.genre_id = g.genre_id
#             WHERE 
#                 NOT movie_delete_ind

#         """
#         values = [] # blank since I do not have placeholders in my SQL
#         cols = ['Movie Title', 'Genre', 'ID']
        
        
#         ### ADD THIS IF BLOCK
#         if searchterm:
#             # We use the operator ILIKE for pattern-matching
#             sql += " AND movie_name ILIKE %s"
            
#             # The % before and after the term means that
#             # there can be text before and after
#             # the search term
#             values += [f"%{searchterm}%"]

#         df = db.querydatafromdatabase(sql, values, cols)
        
#         if df.shape: # check if query returned anything
#             buttons = []
#             for movie_id in df['ID']:
#                 buttons += [
#                     html.Div(
#                         dbc.Button('Edit', href=f'movies/movies_profile?mode=edit&id={movie_id}',
#                                    size='sm', color='warning'),
#                         style={'text-align': 'center'}
#                     )
#                 ]
            
#             df['Action'] = buttons
            
#             # remove the column ID before turning into a table 
#             df = df[['Movie Title', 'Genre', 'Action']]

#             table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
#                     hover=True, size='sm')
#             return [table]
#         else:
#             return ["No records to display"]
        
#     else:
#         raise PreventUpdate