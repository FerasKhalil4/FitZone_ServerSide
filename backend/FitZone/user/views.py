from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, ClientSerializer
from .models import Client
from .permissions import ClientCheck

class RegistrationAV(APIView):
    def post(self, request, *args, **kwargs):
        data = {}
        serializer = ClientSerializer(data=request.data)
        
        if serializer.is_valid():
            account = serializer.save()
            
            user_profile = serializer.validated_data['user_profile']
            user_profile.pop('password', None)
            data['user'] = user_profile

            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        else:
            raise ValidationError({
                'error': 'Please check your data',
                'error_message': serializer.errors
            })
        return Response(data, status=status.HTTP_201_CREATED)

Registration = RegistrationAV.as_view()

class LoginAV(APIView):
    
    def post(self , request, *args, **kwargs):
        
        account = User.objects.filter(username = request.data.get('username') , is_deleted = False) .first()
        if account :
            if account.check_password(request.data.get('password')):
                    refresh = RefreshToken.for_user(account)
                    return Response({'token':{'refresh_token':str(refresh) ,
                                              'access':str(refresh.access_token)} , 
                                     'username' :account.username                                      
                                         }, status = 200)
        
        return Response({'error':'check on the entered data'}, status = 403)
            
Login = LoginAV.as_view()

class ClientProfile(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientSerializer
    permission_classes = [ClientCheck]

    def get_object(self):
            return self.request.user.client
    
    def update(self, request, *args, **kwargs):
        client = self.get_object()
        user_data = request.data.pop('user_profile', None)
        client_serializer = ClientSerializer(client, data=request.data, partial=True)
        
        if user_data:
            user = client.user
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
        client_serializer.is_valid(raise_exception=True)
        client_serializer.save()
        
        return Response( client_serializer.data
        )
client_profile = ClientProfile.as_view()

# class UserProfile(generics.RetrieveAPIView):
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     def get_object(self):
#         return self.request.user
# user_profile = UserProfile.as_view()