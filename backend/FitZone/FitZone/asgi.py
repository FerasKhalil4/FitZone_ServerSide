"""
ASGI config for FitZone project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.routings import ASGI_urlpatterns as chat_routings
from gym_sessions.routings import ASGI_url_patterns as gym_routings
from chat.middleware import JWTMiddleware



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitZone.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTMiddleware(URLRouter(chat_routings + gym_routings))
        
    }
)