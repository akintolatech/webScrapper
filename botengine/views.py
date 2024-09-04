from django.shortcuts import render, redirect, get_object_or_404,HttpResponseRedirect
from .models import Bot
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Bot, Log
import json
from django.contrib.auth.decorators import login_required
from .tasks import run_bot_automation
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Recaptcha


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


@login_required(login_url='/authenticate/')
def clear_logs(request):
    logs = Log.objects.all()
    logs.delete()

    return redirect('authenticator:dashboard')


# Get logs every 5 seconds woth Js fetch request
def get_logs(request):
    logs = Log.objects.all()
    recent_logs = logs[:5]

    # Data for recent logs
    recent_log_data = [
        {"counter": idx + 1, "details": log.log_details, "created": log.created.strftime('%Y-%m-%d %H:%M:%S')}
        for idx, log in enumerate(recent_logs)
    ]

    # Data for all logs
    all_log_data = [
        {"counter": idx + 1, "details": log.log_details, "created": log.created.strftime('%Y-%m-%d %H:%M:%S')}
        for idx, log in enumerate(logs)
    ]

    return JsonResponse({"recent_logs": recent_log_data, "all_logs": all_log_data}, safe=False)


# views.py

@csrf_exempt
def send_recaptcha(request):
    if request.method == 'POST':
        site_key = request.POST.get('site_key')
        recaptcha = Recaptcha(site_key=site_key)
        recaptcha.save()
        return JsonResponse({'status': 'received'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_recaptcha_solution(request):
    try:
        recaptcha = Recaptcha.objects.last()  # Retrieve the most recent reCAPTCHA
        if recaptcha and recaptcha.token:
            return JsonResponse({'recaptcha_token': recaptcha.token})
        return JsonResponse({'recaptcha_token': None})
    except Recaptcha.DoesNotExist:
        return JsonResponse({'error': 'No reCAPTCHA found'}, status=404)


def solve_recaptcha(request):
    recaptcha = Recaptcha.objects.last()  # Retrieve the most recent reCAPTCHA
    if request.method == 'POST' and recaptcha:
        recaptcha.token = request.POST.get('g-recaptcha-response')
        recaptcha.save()
        return redirect('/thanks/')
    return render(request, 'solve_recaptcha.html', {'recaptcha': recaptcha})

def thanks(request):
    return render(request, 'thanks.html')