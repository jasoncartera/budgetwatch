from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from pytz import timezone
from flask_mail import Mail
from budgetwatch.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

mail = Mail(app)


from budgetwatch.users.routes import users
from budgetwatch.entry.routes import entry
from budgetwatch.main.routes import main

app.register_blueprint(users)
app.register_blueprint(entry)
app.register_blueprint(main)


from .util import filters



