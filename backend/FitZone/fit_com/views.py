from rest_framework import generics, status
from rest_framework.response import Response
from community.models import *
from community.serializers import *
from .serializers import ClientPostsSerilizer,SavedPostsSerializer
from .models import Saved_Posts
from drf_spectacular.utils import extend_schema
from .services import PostService

class PostListAV(generics.ListAPIView):
    
    serializer_class = ClientPostsSerilizer
    queryset = Post.objects.filter(is_deleted=False)
    
    @extend_schema(
        summary='get the posts for client'
    )
    def get(self, request, *args, **kwargs):
        posts = PostService.get_client_posts(request.user)
        data = self.get_serializer(posts,many=True).data
        return Response(data,status=status.HTTP_200_OK)

posts_list = PostListAV.as_view()


class CommentsListAV(generics.ListAPIView):
    serializer_class = CommentsSerializer
    
    def get_queryset(self):
        return Comments.objects.filter(is_deleted=False,post = self.kwargs['post_id'])
    
comments_list = CommentsListAV.as_view()

class CommentsListAV(generics.ListAPIView):
    serializer_class = ReactionsSerializer
    
    def get_queryset(self):
        return Reactions.objects.filter(post = self.kwargs['post_id'])
    
reactions_list = CommentsListAV.as_view()

class SavedPostsListAV(generics.ListAPIView):
    serializer_class=SavedPostsSerializer
    
    def get_queryset(self):
        return Saved_Posts.objects.filter(client__user=self.request.user,unsaved=False)

saved_posts = SavedPostsListAV.as_view()
