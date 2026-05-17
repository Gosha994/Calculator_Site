import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase


class NewsPost(SqlAlchemyBase):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    image_filename = sqlalchemy.Column(sqlalchemy.String(300), nullable=True)
    file_filename = sqlalchemy.Column(sqlalchemy.String(300), nullable=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    author = sqlalchemy.orm.relationship('User', lazy='joined')
