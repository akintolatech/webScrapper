from django.urls import path
from . import views

app_name = "authenticator"

urlpatterns = [
    path('', views.authenticator, name="authenticator"),
    path('logout/', views.logout_view, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('clear_logs/', views.clear_logs, name="clear_logs"),
    # path('edit_accounts/', views.edit_accounts, name="edit_accounts")

]
