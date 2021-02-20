from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    '''指定idのレシピ取得用URLを返す
    '''
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='main course'):
    '''test用のtagをモデルに登録して返す。
    '''
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='natto'):
    '''test用のingredientをモデルに登録して返す。
    '''
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    '''test用のrecipeをモデルに登録して返す。
    '''
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):
    '''recipeApiのテスト(未認証)
    '''

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        '''認証が必須であること
        '''
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    '''recipeApiのテスト(未認済みユーザ)
    '''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        '''登録済みレシピ取得テスト
        '''
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        '''レシピ取得のユーザ制限
        '''
        user2 = get_user_model().objects.create_user(
            'other@gamil.com',
            'password'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        '''指定レシピ取得機能テスト
        '''
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)
