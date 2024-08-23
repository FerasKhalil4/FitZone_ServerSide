from django.urls import re_path
from .consumer import *

ASGI_url_patterns =[
    re_path(r'websocket/gym/(?P<branch_id>\d+)/(?P<workout_id>\d+)?/?$',gym_consumer,name='gym_consumer'),
]