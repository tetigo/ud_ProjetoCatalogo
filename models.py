#!/usr/bin/python
# -*- coding: utf-8 -*-

from super import db

from datetime import datetime

from flask_login import UserMixin


class User(db.Model, UserMixin):

    """
    Modelo Usuario
    """

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(100))
    token = db.Column(db.Text)
    items = db.relationship('Item', backref='user', uselist=True)

    @property
    def serialize(self):
        """
        retorna objeto em formato serializado
        """

        return {'id': self.id, 'email': self.email, 'name': self.name}


class Category(db.Model):

    """
    Modelo Categoria
    """

    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    items = db.relationship('Item', backref='category', uselist=True)

    @property
    def serialize(self):
        """
        retorna objeto em formato serializado
        """

        return {'id': self.id, 'name': self.name}


class Item(db.Model):

    """
    Modelo Item de Categoria, tambem ligado a Usuario
    """

    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=True,
                           default=datetime.now())

    category_id = db.Column(db.Integer, db.ForeignKey('category.id',
                            ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @property
    def serialize(self):
        """
        retorna objeto em formato serializado
        """

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
            }
