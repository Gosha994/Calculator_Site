import os
from flask import Flask, render_template

import datetime

app = Flask(__name__)


@app.route("/")
def index():
    print("Успешное подключение:", datetime.datetime.now())
    return render_template("index.html", title="Главная страница")


port = 5000

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
