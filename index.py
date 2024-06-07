# Dash related dependencies
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# To open browser upon running your app
import webbrowser

# Importing your app definition from app.py so we can use it
from app import app

from apps import commonmodules as cm
# from apps.movies import movies_home, movies_profile
from apps.appointments import appointments_default, appointments_profile
from apps.patients import patients_default, patients_profile
from apps import home
from apps import login
from apps import signup


CONTENT_STYLE = {
    "margin-top": "1em",
    "margin-left": "1em",
    "margin-right": "1em",
    "padding": "1em 1em",
}

app.layout = html.Div(
    [
        # Location Variable -- contains details about the url
        dcc.Location(id='url', refresh=True),


        # LOGIN DATA
        dcc.Store(id='sessionlogout', data=True, storage_type='session'),

        # USER ID
        dcc.Store(id='currentuserid', data=-1, storage_type='session'),

        
        dcc.Store(id='currentrole', data=-1, storage_type='session'),

        # Adding the navbar
        html.Div(cm.navbar, id='navbar_div', className=''),

        # Page Content -- Div that contains page layout
        html.Div(id='page-content', style=CONTENT_STYLE),

        # Adding the footer
        # fm.footer

    ],
)


@app.callback(
    [
        Output('page-content', 'children'),
        Output('sessionlogout', 'data'),
        Output('navbar_div', 'className'),
    ],
    [
        # If the path (i.e. part after the website name; 
        # in url = youtube.com/watch, path = '/watch') changes, 
        # the callback is triggered
        Input('url', 'pathname')
    ],
    [
        State('sessionlogout', 'data'),
        State('currentuserid', 'data')
    ]
)
def displaypage(pathname, sessionlogout, userid):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        raise PreventUpdate
       
    if eventid == 'url':
        if userid < 0: # if not logged in
            if pathname == '/':
                returnlayout = login.layout
            elif pathname == '/signup':
                returnlayout = signup.layout
            else:
                returnlayout = 'error 404: page not found'
        else:
            if pathname == '/logout':
                returnlayout = login.layout
                sessionlogout = True

            elif pathname == '/' or pathname == '/home':
                returnlayout = home.layout

            elif pathname == '/appointments':
                returnlayout = appointments_default.layout
            elif pathname == '/appointments/appointments_profile':
                returnlayout = appointments_profile.layout
            elif pathname == '/patients':
                returnlayout = patients_default.layout
            elif pathname == '/patients/patients_profile':
                returnlayout = patients_profile.layout
            else:
                returnlayout = 'error 404: page not found'

        # decide session logout value
        logout_condition = [
            pathname in ['/', '/logout'],
            userid == -1,
            not userid
        ]
        sessionlogout = any(logout_condition)

        # hide navbar if not logged in; else, set class/style to default
        navbar_classname = 'd-none' if sessionlogout else ''

        return [returnlayout, sessionlogout, navbar_classname]   
    else:
        raise PreventUpdate


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run_server(debug=False)