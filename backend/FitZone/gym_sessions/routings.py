from django.urls import path
from .consumer import *

ASGI_url_patterns =[
    path('websocket/gym/<int:branch_id>/',gym_consumer,name='gym_consumer'),
]