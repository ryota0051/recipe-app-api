from rest_framework import serializers

from core.models import Tag, Ingredient


class TagSelializer(serializers.ModelSerializer):
    '''tagモデルのserializer
    '''

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id', )


class IngredientSerializer(serializers.ModelSerializer):
    '''Ingredientモデルのserializer
    '''

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        resd_only_fields = ('id', )
