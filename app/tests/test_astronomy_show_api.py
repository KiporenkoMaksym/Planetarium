from django.test import TestCase

from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from app.models import AstronomyShow, ShowTheme
from app.serializers import AstronomyShowDetailSerializer
from user.tests.test_user_api import create_user

ASTRONOMY_SHOW_API_URL = reverse("app:astronomyshow-list")

def sample_astronomy_show(**params):
    defaults = {
        "title": "Black holes",
        "description":
            "Black holes are the most massive objects in the universe",
    }
    defaults.update(params)

    astronomy_show = AstronomyShow.objects.create(**defaults)

    themes = [
        ShowTheme.objects.create(name="Black holes"),
        ShowTheme.objects.create(name="Dark matter"),
        ShowTheme.objects.create(name="Cosmology"),
    ]

    astronomy_show.themes.set(themes)

    return astronomy_show

def detail_url(astronomy_show_id):
    return reverse(
        "app:astronomyshow-detail",
        args=[astronomy_show_id]
    )

class PublicAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(ASTRONOMY_SHOW_API_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class PrivateAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test1@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_astronomy_show(self):
        sample_astronomy_show()

        res = self.client.get(ASTRONOMY_SHOW_API_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_astronomy_show(self):
        astronomy_show = sample_astronomy_show()
        astronomy_show.themes.add(
            ShowTheme.objects.create(name="Black holes")
        )

        url = detail_url(astronomy_show.id)
        res = self.client.get(url)

        serialiser = AstronomyShowDetailSerializer(
            astronomy_show,
            many=False
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialiser.data)

    def test_post_astronomy_show(self):
        payload = {
            "title": "Black holes",
            "description":
                "Black holes are the most massive objects in the universe",
        }
        res = self.client.post(ASTRONOMY_SHOW_API_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAstronomyShowApiTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test1@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_astronomy_show(self):
        theme = ShowTheme.objects.create(name="Black holes")
        payload = {
            "title": "Black holes",
            "description":
                "Black holes are the most massive objects in the universe",
            "themes": [theme.id],
        }

        res = self.client.post(ASTRONOMY_SHOW_API_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_put_astronomy_show(self):
        astronomy_show = sample_astronomy_show()

        url = detail_url(astronomy_show.id)
        payload = {
            "title": "Black holes",
            "description":
                "Black holes are the most massive objects in the universe",
        }
        res = self.client.put(url, payload)

        astronomy_show.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(astronomy_show.title, payload["title"])
        self.assertEqual(astronomy_show.description, payload["description"])

    def test_delete_astronomy_show(self):
        astronomy_show = sample_astronomy_show()

        url = detail_url(astronomy_show.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            AstronomyShow.objects.filter(id=astronomy_show.id).exists()
        )
