from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    '''tagDB管理View
    '''
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSelializer

    def get_queryset(self):
        '''現在、認証済みのユーザのタグリストを返す
        '''
        return self.queryset.filter(user=self.request.user).order_by('-name')
