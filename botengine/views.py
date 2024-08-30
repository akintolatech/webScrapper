from django.shortcuts import render, redirect, get_object_or_404
from .models import Bot
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Bot
import json

# Create your views here.

# def activate_bot(request):
#
#     bot = Bot.objects.get(id=1)
#
#     if bot.status == Bot.Status.ACTIVE:
#         bot.status = Bot.Status.IDLE
#     else:
#         bot.status = Bot.Status.ACTIVE
#
#     bot.save()
#     return redirect("authenticator:dashboard")


@csrf_exempt
@require_POST
def change_status(request, bot_id):
    try:
        bot = Bot.objects.get(id=bot_id)
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status in dict(Bot.Status.choices):
            bot.status = new_status
            bot.save()
            return JsonResponse({"message": "Status updated successfully."}, status=200)
        else:
            return JsonResponse({"message": "Invalid status value."}, status=400)
    except Bot.DoesNotExist:
        return JsonResponse({"message": "Bot not found."}, status=404)