from flask import Flask, render_template, Response
from streamer import Streamer
from udp_streamer import get_streamer as get_udp_streamer

app = Flask(__name__)

def gen():
  streamer = Streamer('10.0.0.220', 8080)
  streamer.start()

  while True:
    if streamer.streaming:
      yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + streamer.get_jpeg() + b'\r\n\r\n')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/video_feed')
def video_feed():
  return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def udp_gen(streamer):
  while streamer.streaming:
    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + streamer.get_jpeg() + b'\r\n\r\n')

@app.route('/udp_video_feed')
def udp_video_feed():
  streamer = get_udp_streamer()
  if streamer.streaming:
    return Response(udp_gen(streamer), mimetype='multipart/x-mixed-replace; boundary=frame')
  return Response("No streaming")

@app.route('/udp_streaming')
def udp_streaming():
  return render_template('udp_streaming.html')

if __name__ == '__main__':
  app.run(host='10.0.0.220', threaded=True)
