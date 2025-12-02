from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event


class Command(BaseCommand):
    help = "Удаляет мероприятия, которые закончились более 7 дней назад."

    def handle(self, *args, **options):
        now = timezone.now()
        cutoff = now - timedelta(days=7)

        stale_events = Event.objects.filter(event_time__lt=cutoff)
        count = stale_events.count()
        stale_events.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {count} events with event_time < {cutoff.isoformat()}"
            )
        )
