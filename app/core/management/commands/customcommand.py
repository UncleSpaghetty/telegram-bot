import json

from decouple import config

# Local
from .functions.getUpdates import getUpdates, setWebhook
from .functions.sendMessage import sendMessage, EditMessage

def run():
    TOKEN = config('BOT_TOKEN')
    url = "http://localhost:8000/webhooks/updates/"
    # setWebhook(url)
    # updates = []
    updates = getUpdates()

    commands = {}
    if len(updates) > 0:
        last_message = updates[-1]
        if last_message['message']['text'] == '/docker':
            print('Docker command received')
            commands['docker'] = True

    if 'docker' in commands:
        chat_id = updates[0]['message']['chat']['id']
        message_id = updates[0]['message']['message_id']

        reply_markup = {
            'inline_keyboard': [[
                { 'text': 'Rp', 'callback_data': 'rp' },
                { 'text': "Carrisiland", 'callback_data': 'carrisiland' }
            ]]
        }
        reply_parameters = { 'chat_id': chat_id, 'message_id': message_id }
        
        reply_markup = json.dumps(reply_markup)
        reply_parameters = json.dumps(reply_parameters)

        sendMessage(chat_id=chat_id,
                    text='Seleziona il server a cui collegarti:',
                    reply_markup=reply_markup,
                    reply_parameters=reply_parameters)
