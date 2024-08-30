from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from botengine.models import Bot


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

        context = {
            "bot": bot
        }

        return render(request, 'authenticator/pages/dashboard.html', context)
    else:
        return redirect('login')


def logout_view(request):
    logout(request)
    return redirect('authenticator:authenticator')
