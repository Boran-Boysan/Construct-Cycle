"""
ConstructCycle projesi için ASGI yapılandırması.

ASGI callable'ı modül seviyesinde 'application' değişkeni olarak sunar.

"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construct_cycle_project.settings')

application = get_asgi_application()