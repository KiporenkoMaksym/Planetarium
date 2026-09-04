from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from app.models import ShowTheme
from app.serializers import ShowThemeSerializer
from user.tests.test_user_api import create_user

THEME_URL = reverse("app:showtheme-list")

def sample_theme(**params):
    defaults = {"name": "Black holes"}
    defaults.update(params)

    return ShowTheme.objects.create(**defaults)


class PublicThemeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(THEME_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class PrivateThemeApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_theme(self):
        sample_theme()

        response = self.client.get(THEME_URL)

        themes = ShowTheme.objects.all()
        serializer = ShowThemeSerializer(themes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_post_themes(self):
        payload = {"name": "Test theme"}

        response = self.client.post(THEME_URL, payload)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )


class AdminThemeApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test1@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_theme(self):
        payload = {"name": "Test theme"}

        response = self.client.post(THEME_URL, payload)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_retrieve_theme(self):
        sample_theme()

        response = self.client.get(f"{THEME_URL}999/")

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_put_theme(self):
        sample_theme()

        response = self.client.put(f"{THEME_URL}999/", {})

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_delete_theme(self):
        sample_theme()

        response = self.client.delete(f"{THEME_URL}999/")

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
