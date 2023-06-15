from flask import *
from routes import hospital
from routes.extensions import mysql

def create_app():
    app = Flask(__name__)

    app.secret_key  = "we are the champions"

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'wakhu'
    app.config['MYSQL_PASSWORD'] = 'password'
    app.config['MYSQL_DB'] = 'Hospital'

    mysql.init_app(app)

    app.register_blueprint(hospital)

    return app