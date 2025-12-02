from django.db import models


class SyncRun(models.Model):
    run_at = models.DateTimeField(auto_now_add=True)
    created_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Синхронизация мероприятий"
        verbose_name_plural = "Синхронизации мероприятий"

    def __str__(self) -> str:
        return f"Sync at {self.run_at}: +{self.created_count}, ~{self.updated_count}"
