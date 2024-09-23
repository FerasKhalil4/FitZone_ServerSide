from rest_framework import generics
from .serializers import BlockSerializer
from .models import BlockList
from drf_spectacular.utils import extend_schema

class BlockListAV(generics.ListCreateAPIView):
    serializer_class = BlockSerializer
    queryset = BlockList.objects.all()
    
    def get_queryset(self):
        return BlockList.objects.filter(blocker = self.request.user,blocking_status = True)

    @extend_schema(
        summary='get all the blockings related to the requested blocker'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    @extend_schema(
        summary='blocking process'
    )
    def post(self, request, *args, **kwargs):
        request.data['blocker'] = self.request.user.pk
        return super().post(request, *args, **kwargs)
        
Blocklist = BlockListAV.as_view()

class BlockDetailsAV(generics.RetrieveDestroyAPIView):
    queryset = BlockList.objects.all()
    serializer_class = BlockSerializer
    
    @extend_schema(
        summary='get blocking related to the requested blocker'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='unblock user'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
        
BlockDetails = BlockDetailsAV.as_view()