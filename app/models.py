"""SQLA Database models"""
from app import db


class Host(db.Model):
    """Host model"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    address = db.Column(db.String(256), nullable=False)
    user = db.Column(db.String(256), nullable=False)


class Task(db.Model):
    """Task model"""

    id = db.Column(db.String(35), primary_key=True)
    host = db.Column(db.Integer, db.ForeignKey("host.id"))
    status = db.Column(db.String(2048), default="new", nullable=False)
    command = db.Column(db.String(2048), nullable=False)
    result = db.Column(db.String(2048), default="")


db.create_all()
