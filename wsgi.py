# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#
# The below has been auto-generated for your Flask project

import sys
import os

# Add project directory to PythonAnywhere path
sys.path.insert(0, "/home/Wamietech/wamie_tech_portfolio")

# Import and create the app
from app import create_app
application = create_app()
