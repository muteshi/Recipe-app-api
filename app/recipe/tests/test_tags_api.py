from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """
    Test tags that can be accessed without authentication
    """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that a login is required before retrieving user tags
        """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Test that only authorized user can access protected TAGs
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@webgurus.co.ke',
            'passwordHere'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Test retrieving of tags successfully
        """
        # sample tags
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')  # return tags in order
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """
        Test that tags returned are for the authenticated user
        """
        user2 = get_user_model().objects.create_user(
            'other@webgurus.co.ke',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """
        Test adding of  new tag
        """
        payload = {'name': 'Simple tag'}
        self.client.post(TAGS_URL, payload)

        tag_exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(tag_exists)

    def test_create_tag_invalid(self):
        """
        Test creating a new tag with invalid information
        """
        payload = {'name': ''}  # tag with empty name
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """
        Test filtering tags by those assigned to recipes
        """
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Coriander eggs on toast',
            duration=10,
            price=5.00,
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """
        Test filtering tags by assigned returns unique items
        """
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            duration=5,
            price=3.00,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Porridge',
            duration=3,
            price=2.00,
            user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
