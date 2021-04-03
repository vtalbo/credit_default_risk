# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/dashboard/')
def dashboard():
    return "Bienvenue sur le <i>dashboard</i>"
