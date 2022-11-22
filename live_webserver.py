from sre_constants import SUCCESS
from flask import Flask, render_template, Response
import cv2
from pyngrok import ngrok
from werkzeug.serving import make_server
import threading
import pyaudio
app = Flask(__name__)

camera = cv2.VideoCapture(0)
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)
 
class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('starting server')
        self.server.serve_forever()

    def shutdown(self):
        print("server stop")
        camera.release()
        self.server.shutdown()
cam_on=False
def gen_header(sampleRate, bitsPerSample, channels, samples):
    datasize = 10240000 # Some veeery big number here instead of: #samples * channels * bitsPerSample // 8
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

FORMAT = pyaudio.paInt16
CHUNK = 1024 #1024
RATE = 44100
bitsPerSample = 16 #16
CHANNELS = 1
wav_header = gen_header(RATE, bitsPerSample, CHANNELS, CHUNK)
audio = pyaudio.PyAudio()
stream=''

def gen_frames():  # generate frame by frame from camera
    global cam_on,camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame

        if (not success) or (not cam_on):
            print("cam relaesed")
            camera.release()
            camera=cv2.VideoCapture(0) # use 0 for web camera
            break
        else:
            ret, frame_buffer = cv2.imencode('.jpg', frame)
            frame = frame_buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
  
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/end-video")
def end_video():
    global cam_on ,camera
    camera=cv2.VideoCapture(0) 
    cam_on=False
    return Response("camera closed")
@app.route('/')
def index():
    """Video streaming home page."""
    global cam_on, stream
    cam_on=True
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,input_device_index = 1,
                frames_per_buffer=CHUNK)

    return render_template('index.html')
@app.route('/audio_unlim')
def audio_unlim():
    # start Recording
    def sound():
        data = wav_header
        data += stream.read(CHUNK)
        yield(data)
        while True:
            data = stream.read(CHUNK)
            yield(data)

    return Response(sound(), mimetype="audio/x-wav")

def start_server():
    global server
    # App routes defined here
    server = ServerThread(app)
    server.start()
    print('server started')

def stop_server():
    global server
    server.shutdown()
if __name__=="__main__":
    start_server()