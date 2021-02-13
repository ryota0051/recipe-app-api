from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_retrieve_user_unauthorized(self):
        '''認証が必要なAPIテスト(未認証)
        '''
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    '''ユーザ認証が必要なAPIのテストクラス
    '''

    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='testpass',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        '''ログインしたユーザの情報を取得するテスト
        '''
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        '''POSTメソッドが許可されていないことをテスト
        '''
        res = self.client.post(ME_URL, data={})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        '''ユーザの更新テスト
        '''
        payload = {
            'name': 'new_name',
            'password': 'newpass'
        }

        res = self.client.patch(ME_URL, data=payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
