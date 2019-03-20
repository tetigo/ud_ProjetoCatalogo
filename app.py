import os

from flask import Flask, g, render_template
from flask import redirect, url_for, session, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager, current_user
from flask_login import login_user, login_required, logout_user

from flask_migrate import Migrate

from sqlalchemy import desc

from requests.exceptions import HTTPError
from requests_oauthlib import OAuth2Session
import json
import datetime
import httplib2

from config import Auth, Config

# para testar local
# permite transporte http, uma vez que https requer ssl
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.sqlite3'
app.config['CSRF_ENABLED'] = True

app.debug = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)

from models import User, Category, Item


# ------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    """
    Metodo para flask_login saber qual o usuario atual
    """
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    """
    Usuario nao autorizado cai nessa funcao para decidir o que fazer com ele
    """
    return render_template('negado.html', not_logged_in=True)


@app.before_request
def set_login_status():
    """
    Altera Status de Login
    """
    if current_user.is_authenticated:
        g.logged_in = True
        g.user_email = current_user.email
    else:
        g.logged_in = False

# ------------------------------------------------------------------------


@app.route('/')
@login_required
def index():
    """
    pagina principal
    """
    items = Item.query.order_by(desc(Item.id)).all()
    lista_nome_categorias = [c.name for c in Category.query.all()]
    return render_template(
         'home.html', categorias=lista_nome_categorias, items=items)


@app.errorhandler(404)
def page_not_found(error):
    """
    erro pagina nao existe
    """
    return '404. Pagina Inexistente', 404


@app.route('/categorias.json')
def get_categorias():
    """
    retorna todas as categorias em formato JSON
    """
    categorias = Category.query.all()
    return jsonify(categorias=[c.serialize for c in categorias])


@app.route('/items.json')
def get_items():
    """
    retorna todas as categorias em formato JSON
    """
    items = Item.query.all()
    return jsonify(items=[c.serialize for c in items])


@app.route('/new', methods=['GET'])
@login_required
def new_item():
    """
    mostra formulario para entrar nova categoria
    """
    categorias = Category.query.all()

    return render_template(
        'item_form.html', item=Item(), categories=categorias,
        target_url=url_for('new_item_save'))


@app.route('/new', methods=['POST'])
@login_required
def new_item_save():
    """
    salva item no banco
    """
    form = request.form
    item = Item()
    item.category_id = int(form['category'])
    item.title = form['title']
    item.description = form['description']
    item.created_at = datetime.datetime.now()
    item.user_id = current_user.id
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/catalog/<category>')
def list_category(category):
    """
    lista items de determinada categoria
    """
    items = Item.query.join(Category).filter(Category.name == category)\
        .order_by(desc(Item.id)).all()
    return render_template(
        'category.html', category=category, items=items,
        categories=[c.name for c in Category.query.all()]
    )


@app.route('/catalog/<category>/<item>')
def item_view(category, item):
    """
    mostra item especifico de determinada categoria
    """    
    item = Item.query.filter(Item.title == item).first()
    
    return render_template('item_show.html', item=item, user=item.user)


@app.route('/catalog/<category>/<item_id>/edit')
@login_required
def edit_item(category, item_id):
    """
    edita item de determinada categoria
    """
    item = Item.query.get(int(item_id))
    if item.user_id != current_user.id:
        return redirect(url_for('list_category', category=category))
    else:
        if is_not_authorized(item_id):
            return render_template('negado.html')
    return render_template(
        'item_form.html', item=item, categories=Category.query.all(),
        target_url=url_for('save_item', item_id=item.id))


@app.route('/catalog/<item_id>/save', methods=['POST'])
@login_required
def save_item(item_id):
    """
    salva item depois que edita
    """
    if is_not_authorized(item_id):
        return render_template('negado.html')
    form = request.form
    item = Item.query.get(int(item_id))
    item.category_id = int(form['category'])
    item.title = form['title']
    item.description = form['description']
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/catalog/<category>/<item_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_item(category, item_id):
    """
    apaga item
    """
    if is_not_authorized(item_id):
        return render_template('negado.html')
    if request.method == 'GET':
        item = Item.query.get(int(item_id))
        return render_template(
            'item_delete.html', item=item, target_url=url_for(
                'delete_item', category=category, item_id=item.id
            ))
    else:
        Item.query.filter(Item.id == int(item_id)).delete()
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/login')
def login():
    """
    login handler route
    redirects to Google oauth uri if user is not logged in
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    # get google oauth url
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    # set oauth state
    session['oauth_state'] = state
    # redirect to google for auth
    return redirect(auth_url)


@app.route('/gCallback')
def callback():
    """
    google callback route
    """
    # redirect to homepage if user is logged in
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    # check for errors
    if 'error' in request.args:
        # user denied access to their account
        if request.args.get('error') == 'access_denied':
            return 'Access denied by user'
        # some unknown error occured
        return 'Some error has occured. Please try again'
    # missing state information in the callback
    # something went wrong, login again
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    # successful authentication confirmed at this point
    google = get_google_auth(state=session['oauth_state'])
    try:
        # fetch token from google servers
        token = google.fetch_token(
            Auth.TOKEN_URI,
            client_secret=Auth.CLIENT_SECRET,
            authorization_response=request.url)
    except HTTPError as e:
        return 'HTTPError occurred: ' + str(e)
    # get handler for server token
    google = get_google_auth(token=token)
    # get user info now that we have token for user
    resp = google.get(Auth.USER_INFO)
    if resp.status_code == 200:
        # user data fetched
        user_data = resp.json()
        email = user_data['email']
        user = User.query.filter_by(email=email).first()
        if user is None:
            # create new user if user with the email didn't exist
            user = User()
            user.email = email
        user.name = user_data['name']
        user.token = json.dumps(token)
        # save user to database
        db.session.add(user)
        db.session.commit()
        # login user now using flask_login
        login_user(user)
        return redirect(url_for('index'))
    return 'Error when fetching user information from Google'


@app.route('/logout')
@login_required
def logout():
    """
    tira usuario do sistema
    """
    logout_user()
    return redirect(url_for("index"))


def is_not_authorized(item_id):
    """
    verifica se usuario tem autorizacao para acessar pagina
    """
    item = Item.query.get(int(item_id))
    return item.user.id != current_user.id


def get_google_auth(state=None, token=None):
    """
    Tutorial para conseguir logar oauth2 pelo google:
    http://bitwiser.in/2015/09/09/add-google-login-in-flask.html
    """
    # if token from server is available, just use it
    # we can now fetch user info from google
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    # if state is set (& token is not), create an OAuth session to fetch token
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    # neither token nor state is set
    # start a new oauth session
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth
