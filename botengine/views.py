from django.shortcuts import render, redirect, get_object_or_404
from .models import Bot
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Bot, Log
import json

from .tasks import run_bot_automation


@csrf_exempt
@require_POST
def change_status(request, bot_id):
    try:
        bot = Bot.objects.get(id=bot_id)
        data = json.loads(request.body)

        # Extract Status ad save to database
        new_status = data.get('status')
        bot.status = new_status
        bot.save()

        if new_status in dict(Bot.Status.choices):

            print(new_status)
            if new_status == "AE":
                active_log = Log(log_details=f"The Bot is now active ")
                active_log.save()
                run_bot_automation(repeat=5 * 60)
            else:
                idle_log = Log(log_details=f"The Bot is now Idle ")
                idle_log.save()

            return JsonResponse({"message": "Status updated successfully."}, status=200)
        else:
            return JsonResponse({"message": "Invalid status value."}, status=400)

        # return redirect("authenticator:dashboard")

    except Bot.DoesNotExist:
        return JsonResponse({"message": "Bot not found."}, status=404)


def get_logs(request):
    logs = Log.objects.all().order_by('-created')[:10]  # Adjust the queryset as needed
    log_data = [{"counter": idx + 1, "details": log.log_details, "created": log.created.strftime('%Y-%m-%d %H:%M:%S')} for idx, log in enumerate(logs)]
    return JsonResponse(log_data, safe=False)