import jwt
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

@database_sync_to_async
def get_user(validated_token):
    try:
        return User.objects.get(pk=validated_token['user_id'])
    except:
        return AnonymousUser()

class JWTMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope.get('headers'))
        
        if b'authorization' in headers:
            try:
                auth_header = headers[b'authorization'].decode().split()
                if auth_header[0] == 'Bearer':
                    token = auth_header[1]
                    validated_token = UntypedToken(token)
                    scope['user'] = await get_user(validated_token)
                
            except(InvalidToken,TokenError, jwt.ExpiredSignatureError):
                scope['user'] =  AnonymousUser()
        else:
            scope['user'] =  AnonymousUser()
        
        return await super().__call__(scope, receive, send)
    
    