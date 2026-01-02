"""
WSGI config for SmartPharmacy CRM project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartpharmacy.settings')
application = get_wsgi_application()
