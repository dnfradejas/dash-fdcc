import dash
import logging
import os 
# create the application object (stored in app variable), along with CSS styling
app = dash.Dash(__name__, external_stylesheets=["assets/bootstrap.css"])

# make sure that callbacks are not active when input elements enter the layout
app.config.suppress_callback_exceptions = True
# get CSS froma local folder
app.css.config.serve_locally = True
# Enables your app to run offline
app.scripts.config.serve_locally = True
# set app title
app.title = "Fradejas Dental Care Clinic"
app._favicon = os.path.join(os.getcwd(), 'assets/logo.ico')


# these 2 lines reduces the logs on your terminal so you could debug better 
# when errors are encountered

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)