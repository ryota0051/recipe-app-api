from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
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


class RecipeSerializer(serializers.ModelSerializer):
    '''Recipeモデルのserializer
    '''
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'tags', 'time_minutes',
                  'price', 'link')
        read_only_fields = ('id', )


class RecipeDetailSerializer(RecipeSerializer):
    '''指定Recipeモデルのserializer
    '''
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
