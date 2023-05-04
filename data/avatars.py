"""import datetime
import sqlalchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Avatar(SqlAlchemyBase):
    __tablename__ = 'avatars'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    img = sqlalchemy.Column(sqlalchemy.Text, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    mimetype = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User') """