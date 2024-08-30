from django.db import models


# Create your models here.
class Bot(models.Model):

    bot_name = models.CharField(max_length=255, unique=True)

    class Status(models.TextChoices):
        ACTIVE = "AE", "Active"
        IDLE = "IE", "Idle"

    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.IDLE
    )

    def __str__(self):
        return self.bot_name

