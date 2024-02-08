from django.urls import path
# from django.views.decorators.csrf import csrf_exempt

# from . import views
from .views import TelegramBotView

urlpatterns = [
    # path('updates/', csrf_exempt(views.TelegramBotView), name='updates'),
    path('updates/', TelegramBotView.as_view(), name='telegram_webhook'), 
]