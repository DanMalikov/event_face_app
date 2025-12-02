from django.apps import AppConfig


class TransactionalOutboxConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "transactional_outbox"
