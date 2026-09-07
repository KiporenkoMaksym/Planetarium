import pathlib
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class ShowTheme(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


def show_image_path(instance: "AstronomyShow", filename):
    filename = (f"{slugify(instance.title)}-{uuid.uuid4()}"
                + pathlib.Path(filename).suffix)
    return pathlib.Path("upload-image/") / pathlib.Path(filename)


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    themes = models.ManyToManyField(
        ShowTheme,
        blank=True,
        related_name="astronomy_shows"
    )
    image = models.ImageField(upload_to=show_image_path, null=True, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_rows = models.IntegerField()

    @property
    def get_available_seats(self):
        return self.seats_in_rows * self.rows

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow,
        on_delete=models.CASCADE,
        related_name="show_session"
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.CASCADE,
        related_name="show_sessions"
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self):
        return (f"{self.astronomy_show.title} -"
                f"{self.planetarium_dome.name}")


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, planetarium_dome, errors_to_raise):
        for ticket_attr_value, ticket_attr_name, planetarium_dome_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_rows")
        ]:
            count_attrs = getattr(planetarium_dome, planetarium_dome_attr_name)
            if not(1 <= ticket_attr_value <= count_attrs):
                raise errors_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name}"
                                          f"number must be in available range:"
                                          f" 1, {count_attrs}"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.show_session.planetarium_dome,
            ValidationError
        )

    def save(
            self,
            *args,
            **kwargs
    ):
        self.full_clean()
        return super(Ticket, self).save(*args, **kwargs)

    class Meta:
        ordering = ["row", "seat"]
        unique_together = (("row", "seat", "show_session"),)

    def __str__(self):
        return (f"Ticket: row {self.row}, seat {self.seat}"
                f"- {self.show_session}")
