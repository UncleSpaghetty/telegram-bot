from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from telegram import Update
# from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from django.views import View
import json
# from django.views.decorators.http import require_POST
from decouple import config

TOKEN = config('BOT_TOKEN')

# @require_POST
# def updates(request):
# 	return HttpResponse('Hello, world. This is the webhook response.')

@method_decorator(csrf_exempt, name='dispatch')
class TelegramBotView(View):

	bot = TOKEN

	def post(self, request, *args, **kwargs):
		update_id = None
		update = Update.de_json(json.loads(request.body), self.bot)
		self.dispatcher.process_update(update)
		return HttpResponse()
