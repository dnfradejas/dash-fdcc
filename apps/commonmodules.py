# Usual Dash dependencies
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate

# Let us import the app object in case we need to define
# callbacks here
from app import app


# CSS Styling for the NavLink components
navlink_style = {
    'color': '#ffff',
    'max-width': '1200px',
}


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/home")),
        dbc.NavItem(dbc.NavLink("Appointments", href="/appointments")),
        dbc.NavItem(dbc.NavLink("Patients", href="/patients")),
        dbc.NavItem(dbc.NavLink("Logout", href="/logout")),
    ],
    brand=dbc.Row(
        [
            dbc.Col(html.Img(src="/assets/logo.jpg", height="30px")),
            dbc.Col(dbc.NavbarBrand("Fradejas Dental Care Clinic", className="ml-2")),
        ],
        align="center",
    ),
    brand_href="/home",
    color="#FF9D9D",
    dark=True,
)

