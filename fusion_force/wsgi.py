# fusion_force/wsgi.py - FIXED
import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fusion_force.settings')

application = get_wsgi_application()

# FIX: Use correct path for WhiteNoise
application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), '..', 'staticfiles'))
application.add_files(os.path.join(os.path.dirname(__file__), '..', 'media'), prefix='/media/')