from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

email = 'test@webgurus.co.ke'
password = 'passYangu'


def test_user(email=email, password=password):
    """
    Function for creating sample test user
    """
    return get_user_model().objects.create_user(
        email,
        password,
    )


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

    def test_tag_str(self):
        """
        Test the string representation of a tag model
        """
        tag = models.Tag.objects.create(
            user=test_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """
        Test the string representation of an ingredient model
        """
        ingredient = models.Ingredient.objects.create(
            user=test_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)
