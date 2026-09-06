import datetime
from django.test import TestCase

from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from app.models import (
    ShowSession,
    AstronomyShow,
    PlanetariumDome
)
from app.serializers import ShowSessionDetailSerializer
from app.tests.test_astronomy_show_api import (
    sample_astronomy_show
)
from app.tests.test_planetarium_dome_api import (
    sample_planetarium_dome
)
from user.tests.test_user_api import create_user

SHOW_SESSION_URL = reverse("app:showsession-list")

def sample_show_session(**params):
    astronomy_show = sample_astronomy_show()
    planetarium_dome = sample_planetarium_dome()

    defaults = {
        "astronomy_show": astronomy_show,
        "planetarium_dome": planetarium_dome,
        "show_time": datetime.datetime(
            year=2026,
            month=9,
            day=25,
        ),
    }
    defaults.update(params)
    return ShowSession.objects.create(**defaults)

def detail_url(show_session_id):
    return reverse(
        "app:showsession-detail",
        args=[show_session_id]
    )


class PublicShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class PrivateShowSessionApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test1@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_show_session(self):
        sample_show_session()

        response = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_retrieve_show_session(self):
        show_session = sample_show_session()

        url = detail_url(show_session.id)
        res = self.client.get(url)

        serializer = ShowSessionDetailSerializer(
            show_session,
            many=False
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_show_session(self):
        res = self.client.post(SHOW_SESSION_URL, {})
        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_put_show_session(self):
        show_session = sample_show_session()

        url = detail_url(show_session.id)

        res = self.client.put(url, {})

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_delete_show_session(self):
        show_session = sample_show_session()

        url = detail_url(show_session.id)

        res = self.client.delete(url, {})

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN
        )


class AdminShowSessionApiTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test1@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_show_session(self):
        astronomy_show = sample_astronomy_show()
        planetarium_dome = sample_planetarium_dome()

        payload = {
            "astronomy_show": astronomy_show.id,
            "planetarium_dome": planetarium_dome.id,
            "show_time": datetime.datetime(
                year=2026,
                month=9,
                day=25
            )
        }

        res = self.client.post(SHOW_SESSION_URL, payload)
        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED
        )

    def test_put_show_session(self):
        show_session = sample_show_session()

        astronomy_show = AstronomyShow.objects.get(pk=1)
        planetarium_dome = PlanetariumDome.objects.get(pk=1)

        payload = {
            "astronomy_show": astronomy_show.id,
            "planetarium_dome": planetarium_dome.id,
            "show_time": datetime.datetime(
                year=2026,
                month=9,
                day=25
            )
        }

        url = detail_url(show_session.id)
        res = self.client.put(url, payload)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK
        )

    def test_delete_show_session(self):
        show_session = sample_show_session()

        url = detail_url(show_session.id)

        res = self.client.delete(url)

        self.assertEqual(
            res.status_code,
            status.HTTP_204_NO_CONTENT
        )
