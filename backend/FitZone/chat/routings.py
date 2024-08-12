from django.urls import path
from .consumer import NewChat, OldChat
ASGI_urlpatterns = [
    path('websocket/new/<int:user_id>/',NewChat),
    path('websocket/old/<int:chatroom_id>/',OldChat),

]