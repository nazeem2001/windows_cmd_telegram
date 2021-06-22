# windows_cmd_telegram


please install requirements by



**pip install -r requirements.txt**

**_To make it automatically start_**


**DO THE FOLLOWING STEPS**
1. create a .bat file in the same folder  
   with the following content 
   **@echo off
   
   cls
   
   python telegram_bot.py>>./tele_bot_log/logs.txt
   
   exit**
   
 2. create a .vbs file in the same folder 

    Set WshShell = CreateObject("WScript.Shell") 
    
WshShell.Run chr(34) & "name_of_the_.bat_file" & Chr(34), 0

Set WshShell = Nothing

3. copy the .vbs file 
4. past a shortcut in C:\Users\user_name\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
   
