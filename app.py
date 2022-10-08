from sre_constants import SUCCESS
from flask import Flask, render_template, Response
import cv2
from pyngrok import ngrok
from werkzeug.serving import make_server
import threading
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
def gen_frames():  # generate frame by frame from camera
    global cam_on,camera
    while True:
        # Capture frame-by-frame
        print(cam_on)
        success, frame = camera.read()  # read the camera frame
        print((not success) and (not cam_on))
        if (not success) or (not cam_on):
            print("kksjjkal")
            camera.release()
            camera=cv2.VideoCapture(0) # use 0 for web camera
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
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
    global cam_on
    cam_on=True
    return render_template('index.html')
def start_server():
    global server
    # App routes defined here
    server = ServerThread(app)
    server.start()
    print('server started')

def stop_server():
    global server
    server.shutdown()