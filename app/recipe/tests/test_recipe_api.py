import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
# from rest_framework import serializers
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """
    Return recipe's photo url
    """
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_recipe_url(recipe_id):
    """
    Return recipe details url
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def test_tag(user, name='Main course'):
    """
    Create and return a sample test tag
    """
    return Tag.objects.create(user=user, name=name)


def test_ingredient(user, name='Testing ing'):
    """
    Create and return a sample test ingredient
    """
    return Ingredient.objects.create(user=user, name=name)


def test_recipe(user, **params):
    """
    Create and return a sample test recipe
    """
    defaults = {
        'title': 'testing recipe',
        'duration': 10,
        'price': 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """
    Test public access of recipe API
    """

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """
        Test that authentication is required
        """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """
    Test that access to protected API is authenticated
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@webgurus.co.ke',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """
        Test retrieving list of recipes
        """
        # sample recipes list
        test_recipe(user=self.user)
        test_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """
        Test retrieving recipes for specific user
        """
        user2 = get_user_model().objects.create_user(
            'other@webgurus.co.ke',
            'pass24638'
        )
        test_recipe(user=user2)
        test_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_details_recipe_view(self):
        """
        Test viewing a recipe detail
        """
        recipe = test_recipe(user=self.user)
        recipe.tags.add(test_tag(user=self.user))
        recipe.ingredients.add(test_ingredient(user=self.user))

        url = detail_recipe_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """
        Test creating a new recipe
        """
        payload = {
            'title': 'Test recipe',
            'duration': 30,
            'price': 10.00,
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """
        Test creating a recipe with tags
        """
        # sample tags
        tag1 = test_tag(user=self.user, name='Tag 1')
        tag2 = test_tag(user=self.user, name='Tag 2')
        payload = {
            'title': 'Test recipe with two tags',
            'tags': [tag1.id, tag2.id],
            'duration': 30,
            'price': 10.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """
        Test creating recipe with ingredients
        """
        ingredient1 = test_ingredient(user=self.user, name='Ingredient 1')
        ingredient2 = test_ingredient(user=self.user, name='Ingredient 2')
        payload = {
            'title': 'Test recipe with ingredients',
            'ingredients': [ingredient1.id, ingredient2.id],
            'duration': 45,
            'price': 15.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """
        Test updating a recipe with http patch method
        """
        recipe = test_recipe(user=self.user)
        recipe.tags.add(test_tag(user=self.user))
        new_tag = test_tag(user=self.user, name='Curry')

        payload = {
            'title': 'Chicken tikka',
            'tags': [new_tag.id]
        }
        url = detail_recipe_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """
        Test updating a recipe with http put method
        """
        recipe = test_recipe(user=self.user)
        recipe.tags.add(test_tag(user=self.user))

        payload = {
            'title': 'Spaghetti carbonara',
            'duration': 25,
            'price': 5.00
        }
        url = detail_recipe_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.duration, payload['duration'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):
    """
    Test class for recipe model image upload
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user', 'testpass')
        self.client.force_authenticate(self.user)
        self.recipe = test_recipe(user=self.user)

    def tearDown(self):
        """
        Clean up function (for removing temp files)
        """
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """
        Test successful uploading of an image to recipe model
        """
        url = image_upload_url(self.recipe.id)
        # named temp file
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """
        Test uploading an invalid or empty image
        """
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
