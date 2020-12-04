from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('account:account-create')
TOKEN_URL = reverse('account:account-token')
MANAGE_USER_URL = reverse('account:account-manage')


def create_account(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAccountTests(TestCase):
    """
    Test unaunthenticated API user account
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_account_success(self):
        """
        Test creating new account with valid user information
        """
        payload = {
            'email': 'test@webgurus.co.ke',
            'password': '123pass',
            'name': 'Testing Jina'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_account_exists(self):
        """
        Test that existing user account creation will fail
        """
        payload = {
            'email': 'test@webgurus.co.ke',
            'password': '123pass',
            'name': 'Testing Jina'
        }
        create_account(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_length(self):
        """
        Test if password length meets the minimum password length requirment
        """
        payload = {
            'email': 'test@webgurus.co.ke',
            'password': '123p',
            'name': 'Testing Jina'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        account_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(account_exists)

    def test_create_token_for_user_account(self):
        """
        Test that a token is created for the user account
        """
        payload = {
            'email': 'test@webgurus.co.ke',
            'password': '123p',
            'name': 'Testing Jina'
        }
        create_account(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Test that a token is not created for a user account
        when invalid credentials are provided
        """
        create_account(
            email='test@webgurus.co.ke',
            password='123p7643',
            name='Testing Jina'
        )
        payload = {
            'email': 'test@webgurus.co.ke',
            'password': 'wrongpassword',
            'name': 'Testing Jina'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that token is not created if user account does not exist
        """
        payload = {
            'email': 'test@webgurus.co.ke',
            'password': 'wrongpassword',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
        Test that email and password are provided by user
        """
        res = self.client.post(
            TOKEN_URL, {'email': 'wrongemail', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Test that user is authenticated
        """
        res = self.client.get(MANAGE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAccountApiTests(TestCase):
    """
    Test API requests that requires user authentication
    """

    def setUp(self):

        self.user = create_account(
            email='test@webgurus.co.ke',
            password='wrongpassword',
            name='Testing Jina',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_account_success(self):
        """
        Test retrieving a user account for logged in user
        """
        res = self.client.get(MANAGE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_not_allowed(self):
        """
        Test that post method is not allowed on MANAGE_USER_URL
        """
        res = self.client.post(MANAGE_USER_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_account(self):
        """
        Test updating user account for authenticated users is working
        """
        payload = {
            'name': 'Jina Mpya',
            'password': 'newpassword',
        }
        res = self.client.patch(MANAGE_USER_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
