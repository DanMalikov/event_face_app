import uuid

from django.db import models


class OutboxMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=255)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Outbox сообщение"
        verbose_name_plural = "Outbox сообщения"

    def __str__(self) -> str:
        return f"{self.topic} ({self.id})"
