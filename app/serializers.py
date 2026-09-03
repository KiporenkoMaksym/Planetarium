from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

from app.models import ShowTheme, AstronomyShow, ShowSession, PlanetariumDome, Reservation, Ticket


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "themes", "image")
        read_only_fields = ("id", "image")


class AstronomyShowImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "image")


class AstronomyShowListSerializer(AstronomyShowSerializer):
    themes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )


class AstronomyShowDetailSerializer(AstronomyShowSerializer):
    themes = ShowThemeSerializer(many=True, read_only=True)


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_rows")


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time",
        )


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="title"
    )
    planetarium_dome = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    tickets_available = serializers.IntegerField(read_only=True)
    show_image = serializers.ImageField(
        source="astronomy_show.image",
        read_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time",
            "tickets_available",
            "show_image",
        )


class PlanetariumDomeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = (
            "id",
            "name",
        )


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowDetailSerializer(
        many=False,
        read_only=True
    )
    planetarium_dome = PlanetariumDomeShortSerializer(
        many=False,
        read_only=True
    )


class TicketSerializer(serializers.ModelSerializer):
    reservation = serializers.SlugRelatedField(
        slug_field="user__email",
        read_only=True,

    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "show_session",
            "reservation"
        )


class TicketCreateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["show_session"].planetarium_dome,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = (
            "row",
            "seat",
            "show_session",
        )


class TicketListSerializer(TicketSerializer):
    show_session = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="show_time"
    )
    reservation = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="user__email"
    )


class ReservationSerializer(serializers.ModelSerializer):
    email = serializers.SlugRelatedField(
        source="user",
        read_only=True,
        slug_field="email"
    )
    tickets = TicketCreateSerializer(many=True)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "email", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class TicketDetailSerializer(TicketSerializer):
    show_session = ShowSessionDetailSerializer(
        many=False,
        read_only=True
    )
    reservation = SlugRelatedField(
        slug_field="user__email",
        read_only=True
    )
