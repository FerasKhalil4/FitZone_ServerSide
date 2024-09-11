from django.urls import path
from .views import posts_list,comments_list,reactions_list,saved_posts
urlpatterns = [
    path('posts/',posts_list,name='posts_list'),
    path('comments/<int:post_id>/',comments_list,name='comments_list'),
    path('reactions/<int:post_id>/',reactions_list,name='reactions_list'),
    path('posts/saved/',saved_posts,name='saved_posts'),
]
