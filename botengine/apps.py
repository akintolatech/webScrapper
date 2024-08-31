from django.apps import AppConfig

from datetime import timedelta
from django.utils import timezone


class BotengineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'botengine'

