from __future__ import annotations

import time
from typing import Any

import requests
from django.conf import settings

from .models import OutboxMessage


def enqueue_notification(topic: str, payload: dict[str, Any]) -> OutboxMessage:
    """Кладём сообщение в outbox"""
    return OutboxMessage.objects.create(
        topic=topic,
        payload=payload,
    )


def send_notification(msg: OutboxMessage) -> bool:
    """Отправляем одно сообщение во внешний notification-service"""
    if not settings.JWT_TOKEN:
        return False
    if not settings.NOTIFICATIONS_OWNER_ID:
        return False

    url = settings.NOTIFICATIONS_BASE_URL
    headers = {
        "Authorization": f"Bearer {settings.JWT_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload: dict[str, Any] = msg.payload or {}
    email = payload.get("email")
    message = payload.get("message")

    if not email or not message:
        return False

    body = {
        "id": str(msg.id),  # ключ идемпотентности
        "owner_id": settings.NOTIFICATIONS_OWNER_ID,
        "email": email,
        "message": message,
    }

    max_attempts = 3
    backoff_seconds = 2

    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=5)
        except requests.RequestException:
            if attempt < max_attempts:
                time.sleep(backoff_seconds * attempt)
                continue
            return False

        if resp.status_code in (200, 201):
            return True

        if resp.status_code in (429, 500, 504):
            if attempt < max_attempts:
                time.sleep(backoff_seconds * attempt)
                continue
            return False

        return False

    return False
