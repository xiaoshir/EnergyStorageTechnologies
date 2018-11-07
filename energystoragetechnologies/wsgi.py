from flask import Flask
from flask_sqlalchemy import SQLAlchemy

application = Flask(__name__)
application.config['SECRET_KEY'] = 'bbc99195f28d3c411a22906570c55a77'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///energystoragetechnologies.db'

db = SQLAlchemy(application)

from energystoragetechnologies import routes

if __name__ == '__main__':
    application.run(debug=True)