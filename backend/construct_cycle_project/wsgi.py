"""
ConstructCycle projesi için WSGI yapılandırması.

WSGI callable'ı modül seviyesinde 'application' değişkeni olarak sunar.

"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construct_cycle_project.settings')

application = get_wsgi_application()