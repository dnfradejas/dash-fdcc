# Usual Dash dependencies
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from dash.exceptions import PreventUpdate
import datetime
from apps import constants as c
# Let us import the app object in case we need to define
# callbacks here
from app import app
from apps.src import dash1 as generate_visualization

################################################## CUSTOM STYLES ##############################################################
style = {
         'paddingBlock':'8px',
         'backgroundColor':'#EFEFEF',
         'border':'none',
         'borderRadius':'10px'
        }

################################################## DASH BOARD LOCATION #########################################################
def generate_filters(title, id_name):
    return html.Div([
                html.H3(title, className="card-title", 
                        style={'margin': '0px','fontSize': '16px', 'fontWeight': 'lighter'}),
                # create a combo box for months
                dcc.Dropdown(
                    id=id_name,
                    multi=True
                )
        ])

def generate_stats_card(title, id_name):
    return html.Div(
        dbc.Card([
            dbc.CardBody([
                html.H3(title, className="card-title", style={'margin': '0px','fontSize': '20px','fontWeight': 'lighter'}),
                html.P(id=id_name, className="card-value", style={'margin': '0px','fontSize': '25px','fontWeight': 'bold', 'textAlign': 'center'}),
            ])
        ], 
        style=style)
    )

def generate_graphs(title, id_name = ""):
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H3(title, className="card-title", style={'margin': '0px','fontSize': '20px','fontWeight': 'lighter'}),
                dcc.Loading([
                    html.Div(id=id_name)
                ], type="default")
            ])
        ], style=style)
    ])

################################################# DASH BOARD LOCATION END ########################################################

layout = html.Div([
    dbc.Container([
        html.H2("Clinic Dashboard"),
        # add line break
        html.Hr(),

        dbc.Row([
            dbc.Col(generate_filters("Select Month", "dropdown_month"), width=4),
        ]),
        html.Div(style={'height': '20px'}),
        dbc.Row([
            dbc.Col(generate_stats_card("Total Revenue", "total_revenue"), width=3),
            dbc.Col(generate_stats_card("Revenue Last Month",  "revenue_previous_month"), width=3),
            dbc.Col(generate_stats_card("Average Daily Income", "ave_daily_income"), width=3),
            dbc.Col(generate_stats_card("Total Appointments",  "total_appointments"), width=3),
        ]),
        html.Div(style={'height': '20px'}),
        dbc.Row([
            dbc.Col(generate_graphs("Top Procedures", "top_procedures"), width=6),
            dbc.Col(generate_graphs("Revenue per Procedure", "revenue_per_procedure"), width=6),
        ]),
        html.Div(style={'height': '20px'}),
        dbc.Row([
            dbc.Col(generate_graphs("Revenue per Month", "revenue_per_month"), width=12),
        ])
    ])
])


@app.callback(
    [
        Output('dropdown_month', 'options'),
    ],
    [
        Input('url', 'pathname')
    ]

)
def update_dropdowns(pathname):
    if pathname != '/home' or pathname != '/':
        try:
            months = c.get_months()
            months = months.to_dict('records')
            
            
        except:
            pass
    else:
        raise PreventUpdate
    return [months]

@app.callback(
    [
        Output('total_revenue', 'children'),
        Output('revenue_previous_month', 'children'),
        Output('ave_daily_income', 'children'),
        Output('total_appointments', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('dropdown_month', 'value')
    ]
)
def update_stats(pathname, month_ids):
    if pathname != '/home' or pathname != '/':
        if month_ids == None or len(month_ids) == 0:
            month_ids = [1,2,3,4,5,6,7,8,9,10,11,12]
        
        try:
            total_revenue = c.extract_revenue_multiple_months(month_ids)

            # format total cost in peso
            total_revenue = f"₱{total_revenue:,.2f}"

            revenue_previous_month = c.extract_revenue_per_month(c.extract_previous_month())
            if revenue_previous_month == None:
                revenue_previous_month = 0
            # format total cost in peso
            revenue_previous_month = f"₱{revenue_previous_month:,.2f}"

            ave_daily_income = c.average_daily_income(month_ids)
            # format average daily income in peso
            ave_daily_income = f"₱{ave_daily_income:,.2f}"

            total_apt = c.total_appointments_per_month(month_ids)
            # format average number of patients
            total_apt = f"{total_apt:,.0f}"
        except:
            pass

    else:
        raise PreventUpdate
    
    return [total_revenue,revenue_previous_month, ave_daily_income,total_apt]


@app.callback(
    [
        Output('top_procedures', 'children'),
        Output('revenue_per_procedure', 'children'),
        Output('revenue_per_month', 'children'),
    ],

    [
        Input('url', 'pathname'),
        Input('dropdown_month', 'value'),
    ],
)
def update_graphs(pathname, month_ids):

    if pathname != '/home' or pathname != '/':
        if month_ids == None or len(month_ids) == 0:
            month_ids = [1,2,3,4,5,6,7,8,9,10,11,12]
        try:
            # generate pie chart for top procedures
            top_procedure = c.get_top_procedures(month_ids)
            revenue_per_procedure = c.generate_revenue_per_procedure_per_month(month_ids)
            revenue_per_month = c.generate_revenue_in_months()

            fig1, fig2, fig3 = generate_visualization.generate_visualization(top_procedure, revenue_per_procedure, revenue_per_month)

        except:
            pass
    else:
        raise PreventUpdate
    
    return [html.Div([
        html.Div([
            dcc.Graph(figure=fig1),] ,style={'display': 'justify-content-center'})
    ])], [html.Div([
        html.Div([
            dcc.Graph(figure=fig2),] ,style={'display': 'justify-content-center'})
    ])], [html.Div([
        html.Div([
            dcc.Graph(figure=fig3),] ,style={'display': 'justify-content-center'})
    ])]


