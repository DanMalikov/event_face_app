from django.db import transaction
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from transactional_outbox.services import enqueue_notification

from .models import Event, Registration
from .serializers import EventRegistrationSerializer, EventSerializer


class EventListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ["name"]
    ordering_fields = ["event_time"]
    ordering = ["event_time"]

    filterset_fields = {
        "status": ["exact"],
        "registration_deadline": ["gte", "lte"],
    }

    def get_queryset(self):
        """по умолчанию отдаем open, но также проверяем другой статус"""
        qs = Event.objects.select_related("venue")

        if "status" not in self.request.query_params:
            qs = qs.filter(status=Event.Status.OPEN)

        return qs


class EventRegisterView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventRegistrationSerializer
    queryset = Event.objects.all()  # для доки

    def post(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            data=request.data,
            context={"event": event},
        )

        if not serializer.is_valid():
            error_msg = None

            if "error" in serializer.errors:
                error_msg = serializer.errors["error"][0]
            else:
                for field, messages in serializer.errors.items():
                    if messages:
                        error_msg = f"{field}: {messages[0]}"
                        break

            if error_msg is None:
                error_msg = "Registration failed"

            failure_message = (
                f"Не удалось зарегистрироваться на мероприятие '{event.name}'. "
                f"Причина: {error_msg}"
            )
            notification_payload = {
                "email": request.data.get("email"),
                "message": failure_message,
            }
            enqueue_notification(
                topic="event_registration",
                payload=notification_payload,
            )

            return Response(
                {"error": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        confirmation_code = get_random_string(length=32)

        with transaction.atomic():
            registration = Registration.objects.create(
                event=event,
                full_name=data["full_name"],
                email=data["email"],
                confirmation_code=confirmation_code,
            )

            success_message = (
                f"Вы успешно зарегистрированы на мероприятие '{event.name}'. "
                f"Код подтверждения: {confirmation_code}"
            )
            notification_payload = {
                "email": registration.email,
                "message": success_message,
            }
            enqueue_notification(
                topic="event_registration",
                payload=notification_payload,
            )

        # 4. Отдаём пользователю ответ
        return Response(
            {
                "message": "Registered successfully",
                "confirmation_code": confirmation_code,
            },
            status=status.HTTP_201_CREATED,
        )
