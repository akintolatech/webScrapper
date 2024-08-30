from django.urls import path
from . import views

app_name = "botengine"

urlpatterns = [
    # path('', views.authenticator, name="authenticator"),
    path('change-status/<int:bot_id>/', views.change_status, name='change_status'),

]
