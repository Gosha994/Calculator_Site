import json
import os
import datetime

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
# from data.news_model import NewsPost
from forms.user import RegisterForm, LoginForm, FeedbackForm, NewsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

REPORTS_FILE = "reports.json"


def load_reports():
    if not os.path.exists(REPORTS_FILE):
        return []
    with open(REPORTS_FILE, "rt", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_report(username, message):
    reports = load_reports()
    new_report = {
        "username": username,
        "message": message,
        "date": str(datetime.datetime.now())
    }
    reports.append(new_report)
    with open(REPORTS_FILE, "wt", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=4)


@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя по id для Flask-Login"""
    db_sess = db_session.create_session()
    return db_sess.get(User, int(user_id))


# ----- Подсветка активной вкладки ----
@app.context_processor
def inject_active_page():
    return {'active_page': request.endpoint}


@app.after_request
def add_cors_headers(response):
    # Правильная загрузка ресурсов
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# ===== Главная страница =====
@app.route("/")
def index():
    print("Успешное подключение:", datetime.datetime.now())
    return render_template("index.html", title="Главная страница")


@app.route("/news")
def news():
    print("Новостная страница", datetime.datetime.now())
    return render_template("news.html", title="Новости")


@app.route("/developers")
def developers():
    return render_template("pass.html", title="Разрабатываем...")


@app.route("/re-help", methods=["GET", "POST"])
def re_help():
    if not current_user.is_authenticated:
        return render_template("re_help.html", title="Обратная связь",
                               form=None, message=None,
                               need_login=True)

    form = FeedbackForm()
    sent = False
    if form.validate_on_submit():
        save_report(current_user.name, form.message.data)
        sent = True
    return render_template("re_help.html", title="Обратная связь",
                           form=form, sent=sent, need_login=False)


@app.route("/help")
def help():
    return render_template("pass.html", title="Разрабатываем...")


@app.route("/profile")
def profile():
    return render_template("profile.html", title="Разрабатываем...")


@app.route("/projects")
def projects():
    return render_template("pass.html", title="Разрабатываем...")


# ===== Регистрация =====
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Проверка совпадения паролей
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")

        db_sess = db_session.create_session()

        # Проверка, существует ли уже пользователь с такой почтой
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")

        # Создание нового пользователя
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


# ===== Вход =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        # Проверка существования пользователя и правильности пароля
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html',
                               title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html', title='Авторизация', form=form)


# ===== Выход =====
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# ----- Авторизация по API -----
@app.route("/api/TMP/login", methods=['GET', 'POST'])
def api_login(login_u, password_u):
    pass


@app.route("/api/TMP/logout", methods=['GET', 'POST'])
@login_required
def api_logout():
    pass


# ===== Запуск =====
def main():
    db_session.global_init("db/server.db")
    app.run(port=7000, host='0.0.0.0')


if __name__ == '__main__':
    main()
