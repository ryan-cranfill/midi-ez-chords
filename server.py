from flask_cors import CORS
from threading import Thread, Event
from flask_socketio import SocketIO, send, emit
from flask import Flask, render_template, Response, jsonify, request

from chord_handler import ChordHandler
from test_server import start_runner

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!!'
CORS(app)
socketio = SocketIO(app)

thread = Thread()

manager = ChordHandler()


@socketio.on('new-label')
def update_label(label_data=None):
    if not label_data:
        return

    global manager
    manager.process_label_data(label_data)


@app.route('/label')
def get_midi():
    global manager

    return jsonify(manager.get_state_dict())


@socketio.on('new-mapping')
def new_mapping(data):
    global thread
    thread.handle_mapping(data)


@socketio.on('connect')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    # Start the chord handler generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = ChordHandler()
        thread.start()
    else:
        print('Thread already alive')


if __name__ == '__main__':
    start_runner()
    socketio.run(app, debug=True, host="0.0.0.0", port=420)
