from django.test import TestCase

from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from app.models import PlanetariumDome
from app.serializers import PlanetariumDomeSerializer
from user.tests.test_user_api import create_user

PLANETARIUM_DOME_URL = reverse("app:planetariumdome-list")

def sample_planetarium_dome(**params):
    defaults = {
        "name": "Galaxy Hole",
        "rows": 10,
        "seats_in_rows": 10,
    }
    defaults.update(params)

    return PlanetariumDome.objects.create(**defaults)


class PublicPlanetariumDomeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLANETARIUM_DOME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePlanetariumDomeApiTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_planetarium_dome(self):
        sample_planetarium_dome()

        res = self.client.get(PLANETARIUM_DOME_URL)

        planetarium_dome = PlanetariumDome.objects.all()
        serializer = PlanetariumDomeSerializer(planetarium_dome, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_planetarium_dome(self):
        payload = {
            "name": "Galaxy",
            "rows": 10,
            "seats_in_rows": 10,
        }
        res = self.client.post(PLANETARIUM_DOME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlanetariumDomeApiTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test1@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_planetarium_dome(self):
        payload = {
            "name": "Galaxy",
            "rows": 10,
            "seats_in_rows": 10,
        }
        res = self.client.post(PLANETARIUM_DOME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_planetarium_dome(self):
        sample_planetarium_dome()

        res = self.client.get(f"{PLANETARIUM_DOME_URL}20/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_planetarium_dome(self):
        sample_planetarium_dome()

        res = self.client.put(f"{PLANETARIUM_DOME_URL}20/", {})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_planetarium_dome(self):
        sample_planetarium_dome()

        res = self.client.delete(f"{PLANETARIUM_DOME_URL}20/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
