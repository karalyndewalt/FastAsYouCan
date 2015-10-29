from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DB_URI = "sqlite:///model.db"

db = SQLAlchemy()

################################################################################
# Model Definitions


class User(db.Model):
    """Run calculator user"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), unique=True)
    # distance is in meters
    distance = db.Column(db.Integer, nullable=False)
    # time is in minutes
    time = db.Column(db.Integer, nullable=False)
    VDOT = db.Column(db.Integer, nullable=False)
    weekly_mileage = db.Column(db.Integer)

    def greet(self):
        """Greet using email"""

        return "Hello, {}".format(self.email)

    def __repr__(self):
        """Provide helpful representation when printed"""

        string = "<User id = {} VDOT = {} Max Weekly Milage = {}>"
        return string.format(self.user_id, self.VDOT, self.weekly_mileage)

################################################################################
# Helper Functions


def connect_to_db(app):
    """Connect to the database."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///model.db'
    app.config['SQLALCHEMY-ECHO'] = True
    db.app = app
    db.init_app(app)

connect_to_db(app)

print "Connected to Model.db"
