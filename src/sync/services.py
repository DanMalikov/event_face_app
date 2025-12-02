from __future__ import annotations

from datetime import datetime
from typing import Any

from django.utils.dateparse import parse_datetime

from events.models import Event, Venue


def _parse_dt(value: str | None) -> datetime | None:
    """Меняем дату из строки в datetime"""
    if not value:
        return None
    dt = parse_datetime(value)
    return dt


def _map_status(provider_status: str | None) -> str:
    """Маппим статусы из events-provider в наши статусы."""
    if not provider_status:
        return Event.Status.OPEN

    provider_status = provider_status.lower()

    if provider_status in ("new", "open"):
        return Event.Status.OPEN
    if provider_status == "closed":
        return Event.Status.CLOSED

    return Event.Status.OPEN


def upsert_event_from_payload(payload: dict[str, Any]) -> tuple[Event, bool]:
    """
    Создаём или обновляем Event и, если нужно, Venue на основе данных от events-provider
    """
    event_id = payload.get("id")
    name = payload.get("name")

    event_time = _parse_dt(payload.get("event_time"))
    changed_at = _parse_dt(payload.get("changed_at"))
    registration_deadline = _parse_dt(payload.get("registration_deadline"))

    status = _map_status(payload.get("status"))

    place_data = payload.get("place")
    venue = None
    if place_data and isinstance(place_data, dict):
        venue_id = place_data.get("id")
        venue_name = place_data.get("name") or ""
        if venue_id:
            venue, _ = Venue.objects.update_or_create(
                id=venue_id,
                defaults={
                    "name": venue_name,
                },
            )

    event, created = Event.objects.update_or_create(
        id=event_id,
        defaults={
            "name": name or "",
            "event_time": event_time,
            "status": status,
            "venue": venue,
            "registration_deadline": registration_deadline,
            "changed_at": changed_at,
        },
    )

    return event, created
