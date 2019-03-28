#! /usr/bin/python

import os

from dotenv import load_dotenv

# carrega variaveis de ambiente desse arquivo
load_dotenv('.flaskenv')


class Auth:
    """
    Info para autenticacao Oauth2 no Google
    """
    # OAuth credentials
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    # URI that google server will redirect to
    REDIRECT_URI = 'http://localhost:5000/gCallback'
    # Endpoint to start OAuth request from
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    # Endpoint to fetch user token
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    # Endpoint to get user information at the end of oauth
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    # Data we plan to access from Google profile
    SCOPE = ['profile', 'email']


class Config:
    '''
    Info para chave secreta de config da app
    '''
    SECRET_KEY = os.getenv('SECRET_KEY')
