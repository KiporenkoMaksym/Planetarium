from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    TicketListSerializer,
    AstronomyShowImageSerializer,
)
from user.permissions import IsAdminOrIfAuthenticatedReadOnly


class ShowThemeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AstronomyShowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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

       if self.action == "upload_image":
           return AstronomyShowImageSerializer

       return AstronomyShowSerializer

    @extend_schema(
        summary="Upload image to astronomy show",
        description="Upload an image file for a specific astronomy show.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"image": {"type": "string", "format": "binary"}},
            }
        },
        responses={
            status.HTTP_200_OK: AstronomyShowDetailSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiTypes.OBJECT,
        },
    )

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload_image"
    )
    def upload_image(self, request, pk=None):
        movie = self.get_object()
        serializer = self.get_serializer(
            movie,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get list of astronomy shows",
        description="Get a list of astronomy shows with optional filtering by themes and title.",
        parameters=[
            OpenApiParameter(
                name='themes',
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by themes id (ex. ?themes=1,2,3)"
            ),
            OpenApiParameter(
                name='title',
                type=str,
                description="Filter by title id (ex. ?title=galaxy)"
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PlanetariumDomeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

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

    @extend_schema(
        summary="Get list of show sessions",
        description="Get a list of show sessions with optional filtering by show time and astronomy show.",
        parameters=[
            OpenApiParameter(
                name='show_time',
                type=str,
                description="Filter by show time id (ex. ?show_time=2026-10-15)"
            ),
            OpenApiParameter(
                name='astronomy_show_id',
                type=int,
                description="Filter by astronomy show id (ex. ?astronomy_show=1)"
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            return queryset.prefetch_related("tickets__show_session__astronomy_show")

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Get list of users",
        description="Get a list of user with optional filtering by email.",
        parameters=[
            OpenApiParameter(
                name='email',
                type=str,
                description="Filter users by email (ex. ?email=admin@admin.com)"
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TicketViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(reservation__user=self.request.user)

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
