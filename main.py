import os

import datetime


app = Flask(__name__)


@app.route("/")
def index():
    print("Успешное подключение:", datetime.datetime.now())
    return render_template("index.html", title="Главная страница")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
