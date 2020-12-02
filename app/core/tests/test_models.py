from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """
        Test creating a new user with an email
        (Instead of Django's default username) is successfull
        """
        email = 'test@webgurus.co.ke'
        password = 'test@123#'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test if the email of new user is normalized
        """
        email = 'test@WEBgurus.co.ke'
        password = 'test@123#'
        user = get_user_model().objects.create_user(
            email,
            password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """
        Test to ensure the email of new user is valid
        """
        password = 'test@123#'
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                password
            )

    def test_create_new_super_user(self):
        """
        Test creation on new super user
        """
        password = 'test@123#'
        email = 'test@WEBgurus.co.ke'
        user = get_user_model().objects.create_superuser(
            email,
            password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
