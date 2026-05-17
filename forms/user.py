from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class FeedbackForm(FlaskForm):
    message = TextAreaField('Ваше сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    image = FileField('Изображение', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Только картинки')])
    file = FileField('Прикреплённый файл',
                     validators=[FileAllowed(['pdf', 'zip', 'doc', 'docx'], 'Недопустимый формат')])
    submit = SubmitField('Опубликовать')
