from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy

from . import settings

app = Flask(__name__)
app.config.from_object(settings)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CSRFProtect(app)
db = SQLAlchemy(app)

#pylint: disable=wrong-import-position
from . import views
from . import models
from . import functions
