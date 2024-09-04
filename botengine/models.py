from django.db import models


# Create your models here.

class Recaptcha(models.Model):
    site_key = models.CharField(max_length=255)
    token = models.CharField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Bot(models.Model):
    bot_name = models.CharField(max_length=255, unique=True)
    successful_logins = models.IntegerField(default=0)
    successful_bookings = models.IntegerField(default=0)

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


class Log(models.Model):

    log_details = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.log_details


class Account(models.Model):

    email = models.CharField(max_length=500)
    password = models.CharField(max_length=33)

    def __str__(self):
        return self.email
