from flask import Flask, render_template, Response
import cv2
import numpy as np
from pyngrok import ngrok
import pyscreenshot
from werkzeug.serving import make_server
import threading
import time
import requests
import pyaudio
import base64
from flask_socketio import SocketIO,emit
app = Flask(__name__)
socketio = SocketIO(app)

camera = cv2.VideoCapture(0)
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)


cam_on = False

count=0
def gen_header(sampleRate, bitsPerSample, channels, samples):
    # Some veeery big number here instead of: #samples * channels * bitsPerSample // 8
    datasize = 10240000
    # (4byte) Marks file as RIFF
    o = bytes("RIFF", 'ascii')
    # (4byte) File size in bytes excluding this and RIFF marker
    o += (datasize + 36).to_bytes(4, 'little')
    # (4byte) File type
    o += bytes("WAVE", 'ascii')
    # (4byte) Format Chunk Marker
    o += bytes("fmt ", 'ascii')
    # (4byte) Length of above format data
    o += (16).to_bytes(4, 'little')
    # (2byte) Format type (1 - PCM)
    o += (1).to_bytes(2, 'little')
    # (2byte)
    o += (channels).to_bytes(2, 'little')
    # (4byte)
    o += (sampleRate).to_bytes(4, 'little')
    o += (sampleRate * channels * bitsPerSample //
          8).to_bytes(4, 'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,
                                                  'little')               # (2byte)
    # (2byte)
    o += (bitsPerSample).to_bytes(2, 'little')
    # (4byte) Data Chunk Marker
    o += bytes("data", 'ascii')
    # (4byte) Data size in bytes
    o += (datasize).to_bytes(4, 'little')
    return o


FORMAT = pyaudio.paInt16
CHUNK = 1024  # 1024
RATE = 44100
bitsPerSample = 16  # 16
CHANNELS = 1
wav_header = gen_header(RATE, bitsPerSample, CHANNELS, CHUNK)
audio = pyaudio.PyAudio()
stream = ''

@socketio.on("video")
def gen_frames():  # generate frame by frame from camera
    global cam_on, camera
    # Capture frame-by-frame
    success, frame = camera.read()  # read the camera frame

    if (not success) or (not cam_on):
        camera.release()
        camera = cv2.VideoCapture(0)  # use 0 for web camera
    else:
        ret, frame_buffer = cv2.imencode('.jpg', frame)
        frame = frame_buffer.tobytes()
        emit('video', {'image':  base64.b64encode(frame).decode('utf-8')},broadcast=True)  # concat frame one by one and show result



@socketio.on('screen')
def generateScreenFrames():
    
        img=pyscreenshot.grab()
        ret, frame_buffer = cv2.imencode('.png', cv2.cvtColor(np.array(img),cv2.COLOR_BGR2RGB))
        frame = frame_buffer.tobytes()

        emit('screen', {'image':  base64.b64encode(frame).decode('utf-8')},broadcast=True)  # concat frame one by one and show result
        
        
        



# @app.route('/screen_feed')
@socketio.on('connect')

    
    # Video streaming route. Put this in the src attribute of an img tag
    # generateScreenFrames()
    # handle_test_message()
@app.route('/screen')
def screenPage():
    return render_template('screen.html')



@app.route('/')
def index():
    """Video streaming home page."""

    # global cam_on, stream
    # cam_on = True
    # stream = audio.open(format=FORMAT, channels=CHANNELS,
    #                     rate=RATE, input=True, input_device_index=1,
    #                     frames_per_buffer=CHUNK)

    # return render_template('screen.html')
    return render_template('index.html')
@socketio.on('cconnect')
def connect():
    global cam_on, count
    cam_on=True
    count+=1
@socketio.on('disconnect')
def disconnect():
    global count
    count-=1
    if count<0:
        count=0
    if count==0:
        global cam_on, camera
        camera = cv2.VideoCapture(0)
        cam_on = False

@app.route('/audio_unlim')
def audio_unlim():
    # start Recording
    def sound():
        data = wav_header
        data += stream.read(CHUNK)
        yield (data)
        while True:
            data = stream.read(CHUNK)
            yield (data)

    return Response(sound(), mimetype="audio/x-wav")
@app.route('/stop')
def stop():
    socketio.stop()
    return 'stopped'

def start_server():
    global socketio
    socketio.run(app,debug=False, host='0.0.0.0', port=5000,)

def start_server_in_thread():
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True  # Set as daemon so that it's killed when the main thread exits
    server_thread.start()
    print('server started')


def stop_server():
    global socketio
    try:
        data=requests.get('http://localhost:5000/stop')
        print(data.text)
    except:
        print('server not running')    
    


if __name__ == "__main__":
    # start_server()
    pass
