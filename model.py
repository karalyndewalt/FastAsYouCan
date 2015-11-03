from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import calculator
from datetime import timedelta

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
    # distance is in meters -TODO!! will be removed when Race is routes are in place
    # distance = db.Column(db.Integer, nullable=False)
    # time is in minutes - TODO!! will be removed when Race is routes are in place
    # time = db.Column(db.Integer, nullable=False)
    # VDOT = db.Column(db.Integer, nullable=False)
    weekly_mileage = db.Column(db.Integer, nullable=True)

    def greet(self):
        """Greet using email"""

        return "Hello, {}".format(self.email)

    def __repr__(self):
        """Provide helpful representation when printed"""

        string = "<User id = {} VDOT = {} Max Weekly Mileage = {}>"
        return string.format(self.user_id, self.VDOT, self.weekly_mileage)


class Race(db.Model):
    """Store users races to compute VDOT from"""

    __tablename__ = "races"

    race_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    # distance in meters
    distance = db.Column(db.Integer, nullable=False)
    # time in minutes
    time = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", backref=db.backref("races", order_by=race_id))

    # turn into a property, later
    def VDOT(self):
        """Return user VDOT"""

        percent_VO2 = calculator.get_percent_VO2max(self.time)
        vel = calculator.velocity(self.distance, self.time)
        race_VO2 = calculator.get_VO2_from_velocity(vel)
        VDOT = race_VO2 / percent_VO2

        return VDOT

    def __repr__(self):
        """Provide helpful representation when printed"""

        string = "<Race id: {}, User id: {}, distance: {}, time: {}>"
        return string.format(self.race_id, self.user_id, self.distance, self.time)


class Pace(object):
#     """Store paces E, M, T as percentages"""

    PACE_DICT = {
        "easy": (0.55, 0.65, 0.74),
        "marathon": (0.75, 0.79, 0.84),
        "tempo": (0.83, 0.86, 0.89)
    }

    def __init__(self, VDOT, intensity):
        self.VDOT = VDOT
        self.intensity = intensity

    def pace_range(self):
        intensity_tuple = self.PACE_DICT[self.intensity]
        p_range = []
        for t in intensity_tuple:
            percent_VDOT = self.VDOT * t
            velocity = calculator.get_velocity_from_VO2(percent_VDOT)
            miles_per_min = velocity / 1609.34
            minutes_per_mile = timedelta(minutes=(1/miles_per_min))
            p_range.append(minutes_per_mile)
        return p_range


class Workouts(object):
    """ stores workouts for Marthon training"""
    pass



################################################################################
# Helper Functions


def connect_to_db(app):
    """Connect to the database."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///model.db'
    app.config['SQLALCHEMY-ECHO'] = True
    db.app = app
    db.init_app(app)
    db.create_all()

connect_to_db(app)

print "Connected to Model.db"
