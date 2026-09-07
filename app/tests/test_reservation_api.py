from rest_framework.test import APIClient
from django.test import TestCase

from django.urls import reverse
from rest_framework import status

from app.models import Reservation, Ticket
from app.tests.test_showsession_api import (
    sample_show_session
)
from user.tests.test_user_api import create_user

RESERVATION_URL = reverse("app:reservation-list")

def sample_reservation(user):
    return Reservation.objects.create(user=user)

def sample_ticket(reservation, **params):
    show_session = sample_show_session()

    defaults = {
        "row": 2,
        "seat": 1,
        "show_session": show_session,
        "reservation": reservation,
    }
    defaults.update(params)

    return Ticket.objects.create(**defaults)


class PublicReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class PrivateReservationApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test1@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_reservation(self):
        reservation = sample_reservation(user=self.user)

        sample_ticket(reservation)

        res = self.client.get(RESERVATION_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK
        )

    def test_retrieve_reservation(self):
        reservation = sample_reservation(user=self.user)
        sample_ticket(reservation)

        res = self.client.get(f"{RESERVATION_URL}999/")

        self.assertEqual(
            res.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_post_reservation(self):
        res = self.client.post(RESERVATION_URL, {})

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_put_reservation(self):
        reservation = sample_reservation(user=self.user)
        sample_ticket(reservation)

        res = self.client.put(f"{RESERVATION_URL}999/", {})

        self.assertEqual(
            res.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_reservation(self):
        reservation = sample_reservation(user=self.user)
        sample_ticket(reservation)

        res = self.client.delete(f"{RESERVATION_URL}999/")

        self.assertEqual(
            res.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )


class AdminReservationApiTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test1@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_reservation_when_admin_dont_have_reservation(self):
        user = create_user(
            email="test123@test.com",
            password="testpass",
        )
        reservation = sample_reservation(user=user)

        sample_ticket(reservation)

        res = self.client.get(RESERVATION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 0)

        self.client.force_authenticate(user=user)
        res = self.client.get(RESERVATION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
