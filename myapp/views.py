import random
import base64
from datetime import datetime
import json
import os
from django.conf import settings
import requests
import random
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from myapp.credentials import TELEGRAM_API_URL, URL, APPWRITE_API_KEY, APPWRITE_PROJECT_ID, APPWRITE_BUCKET_ID
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.id import ID

current_time = datetime.now()
client = None
stickers_id_list = []

def setwebhook(request):
    response = requests.post(f"{TELEGRAM_API_URL}setWebhook?url={URL}").json()
    return HttpResponse(f"{response}")

@csrf_exempt
def telegram_bot(request):
    if request.method == 'POST':
        update = json.loads(request.body.decode('utf-8'))
        handle_update(update)
        return HttpResponse('ok')
    else:
        return HttpResponseBadRequest('Bad Request')
    
def initAppwrite():
    global client
    global stickers_id_list
    client = Client()
    client.set_endpoint('https://cloud.appwrite.io/v1')
    client.set_project(APPWRITE_PROJECT_ID)
    client.set_key(APPWRITE_API_KEY)
    storage = Storage(client)
    response =  storage.list_files(bucket_id=APPWRITE_BUCKET_ID)
    stickers_id_list.clear()
    for item in response['files']:
        stickers_id_list.append(item['$id'])
    

def handle_update(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        
        # Check if the message is sent by the bot itself
        if update['message'].get('from', {}).get('is_bot'):
            return  # Ignore messages from other bots

        print(f"Received message: {text} from chat_id: {chat_id}")  # Debugging output
        
        # Get the message ID and the sender's name
        message_id = update['message']['message_id']
        member_name = update['message']['from'].get('first_name', 'User')
        
        send_sticker_raw(chat_id=chat_id, reply_to_message_id=message_id, member_name=member_name)

def send_sticker_raw(chat_id, reply_to_message_id, member_name):
    global current_time
    global stickers_id_list
    global client
    
    time_diffrence = abs(current_time - datetime.now())
    if(time_diffrence.seconds>3):
        current_time = datetime.now()
    else:
        return
    print('stickers count => ',len(stickers_id_list))
    
    if(len(stickers_id_list)==0):
        initAppwrite()
    
    sticker_data = Storage(client).get_file_download(bucket_id=APPWRITE_BUCKET_ID, file_id=random.choice(stickers_id_list))

    files = {
        'sticker': ('sticker.webp', sticker_data, 'image/webp')
    }
    
    payload = {
        'chat_id': chat_id,
        'reply_to_message_id': reply_to_message_id  # This line makes it a reply
    }
    
    response = requests.post(
        f'{TELEGRAM_API_URL}sendSticker',
        params=payload,
        files=files
    )



