import datetime
import sqlalchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Images(SqlAlchemyBase):
    __tablename__ = 'images'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    img = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    mimetype = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"), nullable=True)
    news_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("news.id"), nullable=True)
    user = orm.relationship('User')
    news = orm.relationship('News')
