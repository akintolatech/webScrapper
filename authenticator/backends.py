# myapp/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import BotUser


class MyAuthBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, ):
        try:
            user = BotUser.objects.get(username=username)
            if user.password == password:
                return user
        except BotUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return BotUser.objects.get(pk=user_id)
        except BotUser.DoesNotExist:
            return None
