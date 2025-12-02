from typing import Any

import requests
from django.conf import settings


def _get_auth_headers() -> dict[str, str]:
    """Собирает заголовок"""
    if not settings.JWT_TOKEN:
        raise RuntimeError("JWT_TOKEN is not set")
    return {
        "Authorization": f"Bearer {settings.JWT_TOKEN}",
        "Content-Type": "application/json",
    }


def fetch_events_all() -> list[dict[str, Any]]:
    """Полная выгрузка всех мероприятий."""
    url = settings.EVENTS_PROVIDER_BASE_URL
    headers = _get_auth_headers()
    events: list[dict[str, Any]] = []

    while url:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list):
            events.extend(data)
            break

        results = data.get("results", [])
        events.extend(results)
        url = data.get("next")

    return events


def fetch_events_since(changed_at_date: str) -> list[dict[str, Any]]:
    """
    Инкрементальная выгрузка: все мероприятия, изменённые в указанную дату или позже.
    """
    base_url = settings.EVENTS_PROVIDER_BASE_URL
    if "?" in base_url:
        url = f"{base_url}&changed_at={changed_at_date}"
    else:
        url = f"{base_url}?changed_at={changed_at_date}"

    headers = _get_auth_headers()
    events: list[dict[str, Any]] = []

    while url:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list):
            events.extend(data)
            break

        results = data.get("results", [])
        events.extend(results)
        url = data.get("next")

    return events
