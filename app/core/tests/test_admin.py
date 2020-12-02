from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@webgurus.co.ke',
            password='HuyoNiMIMI123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@webgurus.co.ke',
            password='HuyoNiMIMI123user',
            name='Mimi Huyu'
        )

    def test_users_listed(self):
        """
        Test if users are listed on the user page in admin interface
        """
        url = reverse('admin:core_customuser_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """
        Test if user edit page works properly
        """
        # admin/core/customuser/<id:id>
        url = reverse('admin:core_customuser_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """
        Test if create user page works
        """
        # admin/core/customuser/<id:id>
        url = reverse('admin:core_customuser_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
