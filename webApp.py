from flask import Flask, render_template, request
import webbrowser
import os
from flask_cors import CORS
import json

import lambdaSpeechToScore
import lambdaGetSample

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = '*'

rootPath = ''


@app.route(rootPath+'/')
def main():
    return render_template('main.html')

@app.route(rootPath+'/status')
def status():
    return "OK"

@app.route(rootPath+'/GetAccuracyFromRecordedAudioFile', methods=['POST'])
def GetAccuracyFromRecordedAudioFile():

    event = {'body': json.dumps(request.get_json(force=True))}
    lambda_correct_output = lambdaSpeechToScore.lambda_handler_file(event, [])
    return lambda_correct_output

@app.route(rootPath+'/GetAccuracyFromRecordedAudio', methods=['POST'])
def GetAccuracyFromRecordedAudio():
    event = {'body': json.dumps(request.get_json(force=True))}
    lambda_correct_output = lambdaSpeechToScore.lambda_handler(event, [])
    return lambda_correct_output


if __name__ == "__main__":
    language = 'en'
    print(os.system('pwd'))
    webbrowser.open_new('http://127.0.0.1:3000/')
    app.run(host="0.0.0.0", port=3000)
