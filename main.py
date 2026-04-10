import os

import datetime

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    print("Успешное подключение:", datetime.datetime.now())
    return "Небольшая основа для сайта"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
