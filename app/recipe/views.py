from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    '''レシピの属性BaseView
    '''
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        '''登録済みのデータリストを返す
        '''
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        '''データ登録
        '''
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    '''tagDB管理View
    '''
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    '''IngredientDB管理View
    '''
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
