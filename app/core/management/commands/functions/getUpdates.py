import requests
from decouple import config

TOKEN = config('BOT_TOKEN')

# Get updates
def getUpdates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    results = response.json()['result']
    return results

def setWebhook(url, certificate=None, ip_address=None, max_connections=None, allowed_updates=None, drop_pending_updates=None, secret_token=None):
    data = {
        'url': url,
        'certificate': certificate,
        'ip_address': ip_address,
        'max_connections': max_connections,
        'allowed_updates': allowed_updates,
        'drop_pending_updates': drop_pending_updates,
        'secret_token': secret_token
    }
    response = requests.post(url, data)
    print(response)
    return response
