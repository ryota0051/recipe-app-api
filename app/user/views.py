from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    '''ユーザ新規作成
    '''
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    '''新規token生成view
    '''
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    '''ユーザ管理と認証
    '''
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        '''ユーザの認証と取得
        '''
        return self.request.user
