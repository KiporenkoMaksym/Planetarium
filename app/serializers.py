from rest_framework import serializers

from app.models import ShowTheme, AstronomyShow, ShowSession, PlanetariumDome, Reservation, Ticket


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "themes")


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
            "show_time"
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


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowDetailSerializer(
        many=False,
        read_only=True
    )
    planetarium_dome = PlanetariumDomeSerializer(
        many=False,
        read_only=True
    )


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="email"
    )

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "show_session",
            "reservation"
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
        slug_field="user__username"
    )


class TicketDetailSerializer(TicketSerializer):
    show_session = ShowSessionDetailSerializer(
        many=False,
        read_only=True
    )
    reservation = ReservationSerializer(
        many=False,
        read_only=True
    )
