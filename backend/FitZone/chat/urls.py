from django.urls import path,include
from .views import MessageList,chatroomsList

urlpatterns = [
    path('messages/<int:chatroom_id>/', MessageList, name='chat'),
    path('rooms/',chatroomsList,name='rooms')
]