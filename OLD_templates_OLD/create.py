import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://khxxfluukbyqoh:1084ea7b53f5ce4fdbdef299f6c0fc5f334adc6d9d3400e3761b43bf93878c8e@ec2-54-75-246-118.eu-west-1.compute.amazonaws.com:5432/d62ujht21ufg6u"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()

