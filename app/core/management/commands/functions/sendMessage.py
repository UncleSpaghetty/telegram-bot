import requests

from decouple import config

# Local
TOKEN = config('BOT_TOKEN')

# Send message
def sendMessage(chat_id, text, disable_notification=True, reply_markup=None, reply_parameters=None):
    print('Sending message')
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'disable_notification': disable_notification,
        'reply_markup': reply_markup,
        'reply_parameters': reply_parameters
    }
    response = requests.post(url, data)
    result = response.json()
    print(result)
    return result

def EditMessage(chat_id, message_id, text, reply_markup=None):
    print('Editing message')
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
    }
    response = requests.post(url, data)
    result = response.json()
    return result