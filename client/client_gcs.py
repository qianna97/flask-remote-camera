import socket
from flask import Flask, render_template, Response, jsonify, request, url_for, redirect
import cv2, json

ip = ""
port = ""

socketTCP = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

app = Flask(__name__)

video_camera = None
global_frame = None

class VideoStream(object):
    def __init__(self):
        self.cap = cv2.VideoCapture("http://0.0.0.0:5002/video_viewer")
        self.out = None

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        ret, frame = self.cap.read()

        if ret:
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        else:
            return None

def getVideo():
    global video_camera
    global global_frame

    if video_camera == None:
        video_camera = VideoStream()

    while True:
        frame = video_camera.get_frame()
        if frame != None:
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        ip = request.form['ip']
        port = request.form['port']
        if (connect_server(ip,port) == 1):
            return redirect(url_for('home'))
        else:
            return "Can't Connect to Server"
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/command')
def command():
    comm_ = request.args.get('a',0,type=str)
    socketTCP.send(comm_)
    return jsonify(history=comm_)

@app.route('/video_viewer')
def video_viewer():
    return Response(getVideo(),mimetype='multipart/x-mixed-replace; boundary=frame')

def connect_server(ip,port):
    try:
        socketTCP.connect((ip, int(port)))
        return 1
    except:
        return 0

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,threaded=True,debug=True)
