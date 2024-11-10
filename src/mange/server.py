import os
import hashlib

from flask import Flask, render_template, request

from mange.api import *
from mange.conf import settings

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

def runserver():
    app.run(port=5050)
