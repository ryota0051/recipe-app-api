from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    '''IngredientAPIのテスト(認証なし)
    '''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''ログインが必要なことをテスト
        '''
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredinentsApiTests(TestCase):
    '''IngredientAPIのテスト(認証あり)
    '''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        '''材料リスト取得テスト
        '''
        Ingredient.objects.create(user=self.user, name='rice')
        Ingredient.objects.create(user=self.user, name='natto')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        '''認証済みユーザの材料リストが返却されるかテスト
        '''
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'test_pass'
        )
        Ingredient.objects.create(user=user2, name='vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Tomato')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        '''材料追加APIテスト(正常なリクエストボディ)
        '''
        payload = {'name': 'cabbage'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        '''材料追加APIテスト(不正なリクエストボディ)
        '''
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
