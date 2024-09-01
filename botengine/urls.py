from django.urls import path
from . import views

app_name = "botengine"

urlpatterns = [
    # path('', views.authenticator, name="authenticator"),
    path('get-logs/', views.get_logs, name='get_logs'),
    path('change-status/<int:bot_id>/', views.change_status, name='change_status'),

]
