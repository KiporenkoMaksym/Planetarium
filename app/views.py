from datetime import datetime

from django.db.models import F, Count
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from app.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket
)
from app.serializers import (
    ShowThemeSerializer,
    AstronomyShowSerializer,
    PlanetariumDomeSerializer,
    ShowSessionSerializer,
    ReservationSerializer,
    TicketSerializer,
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
    TicketDetailSerializer,
    TicketListSerializer
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]


    def get_queryset(self):
       title = self.request.query_params.get("title")
       themes = self.request.query_params.get("themes")

       queryset = self.queryset

       if title:
           queryset = queryset.filter(title__icontains=title)

       if themes:
            themes_ids =self._params_to_ints(themes)
            queryset = queryset.filter(themes__id__in=themes_ids)

       if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("themes")

       return queryset.distinct()

    def get_serializer_class(self):
       if self.action == "list":
           return AstronomyShowListSerializer

       if self.action == "retrieve":
           return AstronomyShowDetailSerializer

       return AstronomyShowSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = (
        ShowSession.objects.all()
        .select_related("astronomy_show", "planetarium_dome")
        .annotate(
            tickets_available=F("planetarium_dome__rows")
            * F("planetarium_dome__seats_in_rows")
            - Count("tickets")
        )
    )
    serializer_class = ShowSessionSerializer

    def get_queryset(self):
            show_time = self.request.query_params.get("show_time")
            astronomy_show_id = self.request.query_params.get("astronomy_show")

            queryset = super().get_queryset()

            if show_time:
                show_time = datetime.strptime(show_time, "%Y-%m-%d").date()
                queryset = queryset.filter(show_time__date=show_time)

            if astronomy_show_id:
                queryset = queryset.filter(astronomy_show_id=int(astronomy_show_id))

            return queryset.distinct()

    def get_serializer_class(self):

        if self.action == "list":
            return ShowSessionListSerializer

        if self.action == "retrieve":
            return ShowSessionDetailSerializer

        return ShowSessionSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = Reservation.objects.filter(
            user=self.request.user
        )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            return queryset.select_related(
                "show_session",
                "reservation__user"
            )

        if self.action == "retrieve":
            return queryset.select_related(
                "show_session__astronomy_show",
                "show_session__planetarium_dome",
                "reservation__user",
            )

        return queryset

    def get_serializer_class(self):

        if self.action == "list":
            return TicketListSerializer

        if self.action == "retrieve":
            return TicketDetailSerializer

        return TicketSerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100
