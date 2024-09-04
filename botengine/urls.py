from django.urls import path
from . import views

app_name = "botengine"

urlpatterns = [
    path('change-status/<int:bot_id>/', views.change_status, name='change_status'),
    path('clear_logs/', views.clear_logs, name="clear_logs"),
    path('get-logs/', views.get_logs, name='get_logs'),

    # URL for sending the reCAPTCHA site key from the bot
    path('api/send_recaptcha/', views.send_recaptcha, name='send_recaptcha'),

    # URL for retrieving the reCAPTCHA solution
    path('api/get_recaptcha_solution/', views.get_recaptcha_solution, name='get_recaptcha_solution'),

    # URL for displaying and solving the reCAPTCHA
    path('solve_recaptcha/', views.solve_recaptcha, name='solve_recaptcha'),

    # URL for a thank you page or redirect after solving the reCAPTCHA
    path('thanks/', views.thanks, name='thanks'),
]
