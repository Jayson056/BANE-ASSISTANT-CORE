"""
BANE Official Site - Render Deployment Script (WSGI Entry)
Ensure this file is pointed to by your WSGI config (e.g. gunicorn bane_site:application)
"""
import os
import sys

# Add the 'deployment/site' directory to Python path
# This assumes the script is run from the root of BANE-Deployment
sys.path.append(os.path.join(os.path.dirname(__file__), 'deployment', 'site'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bane_web.settings')

application = get_wsgi_application()
