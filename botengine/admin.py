from django.contrib import admin
from .models import Bot, Log, Account, Recaptcha

# Register your models here.
admin.site.register(Bot)
admin.site.register(Log)
admin.site.register(Account)
admin.site.register(Recaptcha)
