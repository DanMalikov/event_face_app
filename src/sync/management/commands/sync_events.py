from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from events.models import Event
from sync.client import fetch_events_all, fetch_events_since
from sync.models import SyncRun
from sync.services import upsert_event_from_payload


class Command(BaseCommand):
    help = "Синхронизация мероприятий с events-provider"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Выполнить полную синхронизацию всех мероприятий",
        )

    def handle(self, *args, **options):
        full_sync: bool = options["all"]

        if full_sync:
            self.stdout.write(self.style.WARNING("Running FULL sync..."))
            events_data = fetch_events_all()
        else:
            self.stdout.write(self.style.WARNING("Running incremental sync..."))
            last_changed_at = (
                Event.objects.exclude(changed_at__isnull=True)
                .order_by("-changed_at")
                .values_list("changed_at", flat=True)
                .first()
            )

            if last_changed_at is None:
                self.stdout.write(
                    self.style.WARNING(
                        "No events with changed_at found, falling back to FULL sync"
                    )
                )
                events_data = fetch_events_all()
            else:
                changed_at_date = last_changed_at.date().isoformat()
                self.stdout.write(f"Fetching events changed since {changed_at_date}...")
                events_data = fetch_events_since(changed_at_date)

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for payload in events_data:
                event, created = upsert_event_from_payload(payload)
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            SyncRun.objects.create(
                created_count=created_count,
                updated_count=updated_count,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync completed: created={created_count}, updated={updated_count}"
            )
        )
