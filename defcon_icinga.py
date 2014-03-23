import os
import time
import requests
import json
from threading import Thread
from flask import Flask, render_template, session, request
from flask_bootstrap import Bootstrap
from flask.ext.socketio import SocketIO, emit, join_room, leave_room


HOST = '127.0.0.1'
AUTHKEY = 'xyz'
URL = 'http://%s/icinga-web/web/api/service/filter/columns[SERVICE_NAME|HOST_NAME|SERVICE_CURRENT_STATE]/authkey=%s/json' % (HOST, AUTHKEY)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.urandom(24)
Bootstrap(app)
socketio = SocketIO(app)


def defcon():
    colors = {'red': '#d9534f',
              'yellow': '#f0ad4e',
              'green': '#5cb85c'}

    r = requests.get(URL)
    problems = []
    for i in r.json()['result']:
        if i['SERVICE_CURRENT_STATE'] != '0':
            problems.append(i)

    if len(problems) == 0:
        color = colors['green']
    elif 1 <= len(problems) <= 3:
        color = colors['yellow']
    else:
        color = colors['red']

    return json.dumps({'check_time': time.strftime('%H:%M:%S'), 'color': color, 'count': len(problems), 'problems':
                      problems})


def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        time.sleep(10)
        defcon_json = defcon()
        socketio.emit('my response', defcon_json, namespace='/defcon')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/defcon')
def defcon_connect():
    print('Client connected')
    defcon_json = defcon()
    emit('my response', defcon_json, namespace='/defcon')


@socketio.on('disconnect', namespace='/defcon')
def defcon_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    Thread(target=background_thread).start()
    socketio.run(app)
