from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    '''ユーザAPIのテスト(public)
    '''

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        '''ユーザ作成テスト
        '''
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpassword',
            'name': 'name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_already_exists(self):
        '''既存ユーザ作成時にステータス400が返るかテスト
        '''
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpassword',
            'name': 'name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''パスワードが5文字より少ない場合にステータスコード400が返るか
        '''
        payload = {
            'email': 'test@gmail.com',
            'password': 'pw',
            'name': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''tokenが作成されるか
        '''
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpassword',
            'name': 'name'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        '''パスワードが異なるときにtokenが発行されないか
        '''
        create_user(email='test@gmail.com', password='testpass')
        payload = {
            'email': 'test@gmail.com',
            'password': 'wrongpass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        '''存在しないユーザに対してtokenが発行されないか
        '''
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpassword'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        '''入力必須項目に入力がないユーザにtokenが発行されないか
        '''
        res = self.client.post(
            TOKEN_URL,
            {'email': 'test@gmail.com', 'password': ''}
        )

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
