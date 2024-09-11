from django.urls import path
from .consumer import community

ASGI_url_patterns = [
    path('community/websocket/',community,name='community')
]