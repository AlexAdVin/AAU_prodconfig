import requests
import simplejson as json
import serial
import time

from flask import Flask, session, render_template, jsonify, request, redirect, url_for, flash
from flask_session import Session
from flask_sqlalchemy import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_socketio import SocketIO, emit

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
socketio = SocketIO(app)

@app.route("/dashboard", methods=["GET", "POST"])
def dashBoard():
    
    return render_template("socket_dashboard.html")

@app.route("/", methods=["GET", "POST"])
def socketIO():
    
    return render_template("socketIO.html")


@socketio.on("submit vote")
def vote(data):
    selection = data["selection"]
    emit("announce vote", {"selection": selection}, broadcast=True)


@socketio.on("submit event")
def reading(data):

    uno = serial.Serial('COM5', 115200)
    
    if data["selection"]:

        while True:

            arduino_data1 = uno.readline().decode('ascii')
            uno_data = float(arduino_data1)
            print(uno_data)

            #for item in arduino_data1:
                #arduino_data1 = float(item)

            #return render_template("main.html", arduino_data=arduino_data)
            #return jsonify({"success": True, "rate": uno_data})
            emit("announce event", {"value": uno_data}, broadcast=True)
            #time.sleep(1) # Sleep for 2 seconds
        
        
    
if __name__ == '__main__':
    app.debug = True
    app.run()
