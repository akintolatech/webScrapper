from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from botengine.models import Bot, Log, Account


# Create your views here.

def authenticator(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('authenticator:dashboard')
        else:
            context = {'error': 'Invalid username or password'}
            return render(request, 'authenticator/auth.html', context)
    else:
        return render(request, 'authenticator/auth.html')


@login_required(login_url='/authenticate/')
def dashboard(request):
    if request.user.is_authenticated:

        bot = Bot.objects.get(id=1)
        logs = Log.objects.all()
        recent_logs = logs[: 5]
        accounts = Account.objects.all()


        context = {
            "bot": bot,
            "recent_logs" :recent_logs,
            "logs": logs,
            "log_count": logs.count(),
            "accounts": accounts
        }

        return render(request, 'authenticator/pages/dashboard.html', context)
    else:
        return redirect('login')


@login_required(login_url='/authenticate/')
def clear_logs(request):
    logs = Log.objects.all()
    logs.delete()

    return redirect('authenticator:dashboard')


# @login_required(login_url='/authenticate/')
# def edit_accounts(request):
#     if request.method == "POST":
#         form_type = request.POST.get("form_type")
#         print(form_type)
#
#         if form_type == "status_form":
#             # Handle the status form submission
#             # Update the bot status logic here if needed
#             pass
#
#         elif form_type == "accounts_form":
#             # Handle the accounts form submission
#             accounts = Account.objects.all()
#
#             for account in accounts:
#                 email_text = request.POST.get(f"email_{account.id}")
#                 password_text = request.POST.get(f"password_{account.id}")
#
#                 print(email_text)
#
#                 account.email = email_text
#                 account.password = password_text
#
#                 # if email_text:
#                 #     account.email = email_text
#                 # if password_text:
#                 #     account.password = password_text
#
#                 account.save()
#
#             return redirect("authenticator:dashboard")
#
#     return redirect("authenticator:dashboard")


def logout_view(request):
    logout(request)
    return redirect('authenticator:authenticator')
