from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bbc99195f28d3c411a22906570c55a77'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../energystoragetechnologies.db'

db = SQLAlchemy(app)

from energystoragetechnologies import routes
