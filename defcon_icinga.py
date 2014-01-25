import requests
from flask import Flask, render_template


app = Flask(__name__)


red = '#911821'
yellow = '#c3a41e'
green = '#3aad2f'


def defcon():
    URL = 'http://127.0.0.1/icinga-web/web/api/service/filter/columns[SERVICE_NAME|HOST_NAME|SERVICE_CURRENT_STATE]/authkey=xyzxyzxyz/json'
    r = requests.get(URL)
    problems = []
    for i in r.json()['result']:
        if i['SERVICE_CURRENT_STATE'] != '0':
            problems.append(i)

    if len(problems) == 0:
        color = green
    elif 1 <= len(problems) <= 3:
        color = yellow
    else:
        color = red

    return color, len(problems), problems


@app.route('/')
def index():
    problems = defcon()
    background_color = problems[0]
    return render_template('index.html', background_color = background_color,
                           problems_len = problems[1], problems = problems[2])
