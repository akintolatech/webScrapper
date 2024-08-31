from django.apps import AppConfig

from datetime import timedelta
from django.utils import timezone


class BotengineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'botengine'

    def ready(self):
        # Import the task here to avoid potential import issues
        from .tasks import run_bot_automation
        from .models import Bot

        # Retrieve the single bot instance
        try:
            bot = Bot.objects.get(id=1)
            # Check if the bot's status is 'Active'
            if bot.status == Bot.Status.ACTIVE:
                # Schedule the task to run every 5 minutes
                run_bot_automation(schedule=timezone.now(), repeat=30)
            else:
                print("bot is not active")
        except Bot.DoesNotExist:
            # Handle the case where the bot does not exist
            print("boss does not exist")
        # print("default app config wired ")
