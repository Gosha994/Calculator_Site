import json
import os
import datetime

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
# from data.news_model import NewsPost
from werkzeug.utils import secure_filename
from forms.user import RegisterForm, LoginForm, FeedbackForm, NewsForm
from data.news import NewsPost
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

REPORTS_FILE = "reports.json"

# Конфигурация загрузки новостей
UPLOAD_FOLDER = 'static/uploads/news'
ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_FILE_EXT = {'pdf', 'zip', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Загрузка администраторов
def load_admins():
    # Временно: считаем администратором любого, кто зашёл (для теста)
    return {'1111': 1}


# Сохранение загруженных файлов
def save_uploaded_file(file, folder, allowed_ext):
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_ext:
            return None
        filename = secure_filename(f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        return os.path.join('static', 'uploads', 'news', filename).replace('\\', '/')
    return None


# Жалобы пользователей
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


@app.route("/news", methods=['GET', 'POST'])
def news():
    ALLOWED_ADMINISTRATORS = load_admins()

    # --- Чтение новостей (отдельная сессия) ---
    db_sess_read = db_session.create_session()
    posts = db_sess_read.query(NewsPost).options(joinedload(NewsPost.author)).order_by(NewsPost.created_at.desc()).all()
    db_sess_read.close()  # Закрываем сразу после чтения

    form = None
    if current_user.is_authenticated and current_user.name in ALLOWED_ADMINISTRATORS:
        form = NewsForm()
        if form.validate_on_submit():
            # Сохраняем файлы
            image_path = save_uploaded_file(form.image.data, app.config['UPLOAD_FOLDER'], ALLOWED_IMAGE_EXT)
            file_path = save_uploaded_file(form.file.data, app.config['UPLOAD_FOLDER'], ALLOWED_FILE_EXT)

            # --- Запись новости (новая сессия) ---
            db_sess_write = db_session.create_session()
            post = NewsPost(
                title=form.title.data,
                content=form.content.data,
                image_filename=image_path,
                file_filename=file_path,
                author_id=current_user.id
            )
            db_sess_write.add(post)
            db_sess_write.commit()
            db_sess_write.close()
            return redirect('/news')

    return render_template("news.html", title="Новости", news=posts, form=form, can_post=(form is not None))


@app.route("/developers")
def developers():
    # Список разработчиков
    developers_list = [
        {
            "name": "Лугов Святослав",
            "role": "Программист, Основоположник идеи империи калькуляторов",
            "nickname": "GoSha994",
            "projects": ["Calculator Game", "LSA Site"],
            "github": "github.com/Gosha994",
            "ava": "gosha.png"
        },
        {
            "name": "Семчик Максим",
            "role": "Программист, Мемный арбуз",
            "nickname": "FunnyMaxmm",
            "projects": ["Calculator Game", "LSA Site"],
            "github": "https://github.com/FunnyMaxmm",
            "ava": "funnymax.png"
        },
        {
            "name": "Аникин Роман",
            "role": "Программист, Самая продуктивная креветка на диком кресле",
            "nickname": "BaraCur4ik",
            "projects": ["Calculator Game", "Навык Алисы (вне команды)"],
            "github": "https://github.com/BaraCur4ik",
            "ava": "barakurchik.png"
        }
    ]
    return render_template("developers.html", title="Разработчики", developers=developers_list)


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
    # Список проетов
    projects_list = [
        {
            "project_name": "Calculator Game",
            "info": "Мета игра для вовлечения в точные науки",
            "url": "/pass",
            "github": "https://github.com/Gosha994/Calculator",
            "ava": "calculator.png"
        },
        {
            "project_name": "LSA Site",
            "info": "Новостной сайт о проектах команды",
            "url": "/",
            "github": "https://github.com/Gosha994/Calculator_Site",
            "ava": "lsa_site.png"
        }
    ]
    return render_template("projects.html", title="Наши проекты", projects=projects_list)


@app.route("/pass")
def pass_link():
    return render_template("pass.html")


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
