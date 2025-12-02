from django.utils import timezone
from rest_framework import serializers

from .models import Event, Registration


class EventSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source="venue.name", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "event_time",
            "status",
            "registration_deadline",
            "venue",
            "venue_name",
        ]


class EventRegistrationSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=128)
    email = serializers.EmailField()

    def validate(self, attrs):
        event: Event = self.context["event"]
        email = attrs["email"]

        if event.status != Event.Status.OPEN:
            raise serializers.ValidationError(
                {"error": "Event is not open for registration"}
            )

        if event.registration_deadline is not None:
            now = timezone.now()
            if now > event.registration_deadline:
                raise serializers.ValidationError(
                    {"error": "Registration deadline has passed"}
                )

        if Registration.objects.filter(event=event, email=email).exists():
            raise serializers.ValidationError(
                {"error": "You are already registered for this event"}
            )

        return attrs
