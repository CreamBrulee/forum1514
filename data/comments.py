import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    news_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("news.id"))
    comment_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("comments.id"))
    vlog = sqlalchemy.Column(sqlalchemy.Integer,
                             default=0)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now())
    user = orm.relationship('User')
