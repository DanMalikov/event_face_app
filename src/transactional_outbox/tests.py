from unittest.mock import patch

from django.test import TestCase

from .models import OutboxMessage
from .services import enqueue_notification, send_notification


class OutboxSimpleTest(TestCase):
    def setUp(self):
        OutboxMessage.objects.all().delete()

    def test_enqueue_creates_message(self):
        """Проверяем, что enqueue_notification создаёт сообщение"""
        payload = {"email": "test@example.com", "message": "Привет!"}
        msg = enqueue_notification(topic="test", payload=payload)

        self.assertEqual(OutboxMessage.objects.count(), 1)
        self.assertEqual(msg.topic, "test")
        self.assertEqual(msg.payload, payload)
        self.assertFalse(msg.sent)

    @patch("transactional_outbox.services.requests.post")
    def test_send_notification_success(self, mock_post):
        """В случае успеха send_notification возвращает True"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {}

        msg = OutboxMessage.objects.create(
            topic="test",
            payload={"email": "test@example.com", "message": "Успех!"},
        )

        result = send_notification(msg)

        self.assertTrue(result)

        msg.refresh_from_db()
        self.assertFalse(msg.sent)  # False, так как True делает management-команда

    @patch("transactional_outbox.services.requests.post")
    def test_failed_send_keeps_sent_false(self, mock_post):
        """Если сервис упал — сообщение остаётся неотправленным"""
        mock_post.return_value.status_code = 500

        msg = OutboxMessage.objects.create(
            topic="test", payload={"email": "test@example.com", "message": "Ошибка"}
        )

        result = send_notification(msg)

        self.assertFalse(result)
        msg.refresh_from_db()
        self.assertFalse(msg.sent)
