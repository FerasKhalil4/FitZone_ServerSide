from rest_framework import generics, status 
from rest_framework.response import Response
from .models import *
from .serializers import *
from .paginations import Pagination
from django.db.models import Q
class PostListAV(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_deleted=False)
    pagination_class = Pagination
    def get(self, request,gym_id, *args, **kwargs):
        try:            
            posts = Post.objects.filter(gym =gym_id,is_deleted=False).distinct()
            if not posts.exists():
                return Response({'message':'no posts available'},status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(posts,many=True)
            return Response(serializer.data)
        except Exception as e:
            raise serializers.ValidationError(str(e))
     
    def post(self, request,gym_id, *args, **kwargs):
        
        user = request.user

        data = request.data
        if type(data) is not dict :
            data = request.data.dict()
        data['gym_id'] = gym_id
        images = request.FILES.getlist('images', [])
        videos = request.FILES.getlist('videos', [])
        try:
            employee = Employee.objects.get(user_id=user)
            data['is_approved'] = True if employee.is_trainer == False else False
            data['poster_id'] = employee.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                post=serializer.save()
            if images is not None:
                images_responsed=[]
                for image in images:           
                        instance=Image.objects.create(post=post, image=image)
                        images_responsed.append(instance) 
            if videos is not None:
                videos_responsed=[]                
                for video in videos:
                    instance=Video.objects.create(post=post, video=video)
                    videos_responsed.append(instance) 
            return Response(serializer.data)  
                                
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
postListAV = PostListAV.as_view()

class PostDetailAV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_deleted=False)
    
    def get(self ,request ,*args, **kwargs):
        try:
            pk = kwargs.pop('pk',None)
            post =self.get_object()
            serializer = self.get_serializer(post)
            return Response(serializer.data)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    def put (self, request ,*args, **kwargs):
        data = request.data.copy()
        try:
            instance =self.get_object()
            
            employee =Employee.objects.get(user= request.user)
            if request.user.role == 3 and 'is_approved' in data :
                instance.is_approved = True
                instance.approved_by = employee
                return Response({'message':'post has been approved'},status= status.HTTP_200_OK)
            else:
                data.pop('is_approved',None)

            if employee.id != instance.poster.id :
                return Response({'error':'you are not allowed to update the post'},status= status.HTTP_400_BAD_REQUEST) 
            
            serializer = self.get_serializer(instance, data = data, partial= True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(serializer.data,status= status.HTTP_200_OK)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    def delete(self, request, *args, **kwargs):
        try:
            if request.user.role == 4 :
                post = self.get_object()
                employee = Employee.objects.get(user_id = request.user.id)
                if post.poster.id == employee.id:
                    return super().delete(request, *args, **kwargs)
                else :
                    return Response({'message':'You are not authorized to delete this post'},status=status.HTTP_403_FORBIDDEN)
            elif request.user.role == 3 :
                    return super().delete(request, *args, **kwargs)
        except Exception as e :
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
                
    
postDetailAV = PostDetailAV.as_view()
    