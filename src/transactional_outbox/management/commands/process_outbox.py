from __future__ import annotations

import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from transactional_outbox.models import OutboxMessage
from transactional_outbox.services import send_notification


class Command(BaseCommand):
    help = "Обрабатывает outbox и отправляет уведомления в notification-service."

    def add_arguments(self, parser):
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Крутиться в бесконечном цикле",
        )
        parser.add_argument(
            "--sleep",
            type=int,
            default=5,
            help="Пауза между циклами",
        )

    def handle(self, *args, **options):
        loop = options["loop"]
        sleep = options["sleep"]

        self.stdout.write(self.style.SUCCESS("Starting outbox processor..."))

        while True:
            messages = OutboxMessage.objects.filter(sent=False).order_by("created_at")

            if not messages.exists():
                if not loop:
                    self.stdout.write("No messages to process, exiting.")
                    return
                time.sleep(sleep)
                continue

            processed = 0

            for msg in messages:
                try:
                    if send_notification(msg):
                        msg.sent = True
                        msg.sent_at = timezone.now()
                        msg.save(update_fields=["sent", "sent_at"])
                        processed += 1
                except Exception:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to mark message {msg.id} as sent")
                    )

            self.stdout.write(f"Processed {processed} messages")

            if not loop:
                return

            time.sleep(sleep)
