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

    def easy_pace(self):
        """Returns object of Pace class"""

        # VDOT comes from Race, find most recent race by user_id query
        race = Race.query.filter(Race.user_id == self.user_id).order_by(Race.race_id.desc()).first()
        # call Race instance method .VDOT
        VDOT = race.VDOT()
        # (__init__ on Pace (self, VDOT, intensity(as a string)))
        easy_pace_obj = Pace(VDOT, "easy")
        return easy_pace_obj

    def marathon_pace(self):
        """Returns object of Pace class"""

        # VDOT comes from Race, find most recent race by user_id query
        race = Race.query.filter(Race.user_id == self.user_id).order_by(Race.race_id.desc()).first()
        # call Race instance method .VDOT
        VDOT = race.VDOT()
        # (__init__ on Pace (self, VDOT, intensity(as a string)))
        marathon_pace_obj = Pace(VDOT, "marathon")

        return marathon_pace_obj

    def tempo_pace(self):
        """Returns object of Pace class"""

        # VDOT comes from Race, find most recent race by user_id query
        race = Race.query.filter(Race.user_id == self.user_id).order_by(Race.race_id.desc()).first()
        # call Race instance method .VDOT
        VDOT = race.VDOT()
        # (__init__ on Pace (self, VDOT, intensity(as a string)))
        tempo_pace_obj = Pace(VDOT, "tempo")
        return tempo_pace_obj

    def __repr__(self):
        """Provide helpful representation when printed"""

        string = "<User id = {} Max Weekly Mileage = {}>"
        return string.format(self.user_id, self.weekly_mileage)


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
        """Returns the range of times in minutes/mile for a given intensity"""

        intensity_tuple = self.PACE_DICT[self.intensity]
        p_range = []
        for t in intensity_tuple:
            percent_VDOT = self.VDOT * t
            velocity = calculator.get_velocity_from_VO2(percent_VDOT)
            miles_per_min = velocity / 1609.34
            minutes_per_mile = 1 / miles_per_min
            # minutes_per_mile = timedelta(minutes=(1/miles_per_min))
            p_range.append(timedelta(minutes=minutes_per_mile))
        return p_range

    def velocity(self):
        """Returns list of velocity (low, avg, high) in meters/minute for a given intensity"""

        intensity_tuple = self.PACE_DICT[self.intensity]
        velocity_range = []
        for t in intensity_tuple:
            percent_VDOT = self.VDOT * t
            velocity = calculator.get_velocity_from_VO2(percent_VDOT)
            velocity_range.append(velocity)
        return velocity_range

    def convert_timedelta(self):
        """Return list of pace times (low, avg, high) converted from timedelta object"""

         #        >>> test = [1, 2, 3, 4, 5, 6, 7]
         #        >>> test1 = test[-5:]
         #        >>> print test1
         #        >>> [3, 4, 5, 6, 7]
         # rewrite using list comp, and time date method .total_seconds

        p_range = self.pace_range()
        time_range = []
        for i in p_range:
            time_str = str(i)
            token_time = time_str.split(".")
            time = token_time[0]
            time = time[-5:]
            time_range.append(time)
        return time_range

    # I don't know if there is a meaningful repr, the object is a tuple of
    # percents of user VDOT.
    def __repr__(self):
            """Provide a useful representation when printed"""

            string = "<Paces as VDOT percentage for {} range>"
            return string.format(self.intensity)


# 6 days to start, could allow user specified num training days
class Training_Plan(object):
    """Returns dictionary of Weeks"""

# weeks is a list of Weeks
    def __init__(weeks):
        # for Week in weeks:
            # key[#of week]: [week]
        pass


class Week(object):
    """Returns x days of training as a list

    Uses user race.VDOT to determine distance of workouts, and remainder of
    peak mileage to assign distances to non-quality days.
    """
# get user defined # of days to run/week
# attributes: %ofpeakmileage, workouts, peakmileage
# peakmileage should come from the User class. User.weekly_mileage
# workouts - comes as a list, should only accept a list (even an empty one)
# if/else for empty list
    # if empty list (percent_peak_mileage/peakmileage)/days) = daily_dist
        # for each day create a segment @ Easy for distance= daily_dist
    def __init__(self, percent_peak_mileage, peakmileage, workouts, days=6):
        self.percent_peak_mileage = percent_peak_mileage
        self.peakmileage = peakmileage


class Workouts(object):
    """Returns

    a single workout is a list of segments
    'quality days', specific instructions for workouts with distance, time, pace attributes
    """
    # pass in %peak_mileage and user.weekly_mileage
    # workout is a list of segments(plural), segments = [segment, segment, segment....]
    # segments should only accept a []
    # use segment.seg_distance() to get distance of workout.
    # FOR FUTURE: set of lists, for distance vs time --> 2.5hrs OR (|) 27% of mileage, which-ever is less
    def __init__(self, segments):
        self.segments = segments


class Segments(object):
    """Pace() and distance or time components of a workout"""

    def __init__(self, pace, rep=None, time=None, distance=None, rest=None):
        # pace >>> can/should this be an object of Pace()?
        # NTS ^ should probably just pass in the string and use that to call instance from User.
        # distance is always a percentage
        # want to pass the whole object through and just call the string_seg method to display
        self.pace = pace
        self.rep = rep
        self.time = time
        self.distance = distance
        self.rest = rest

    def make_Pace(self):
        """Makes instance of Pace()"""
        pass


    # wait
    def string_seg(self):
        # probably need abstract Segments Class.... whoomp whoomp
        """Return string representation of a segment"""
        segment = "{EMT} run, {pace},  ".format(EMT=self.pace, pace=())
        # pace_type = user.easy_pace_obj or user.marathon_pace_obj or user.tempo_pace_obj

    def seg_distnace(self):
        # needs to determine distance uses pace.velocity OR self.distance * time
        pass

training_plan = Training_Plan()
week1 = Week()
workout1 = Workout()
segment1 = Segment("easy", distance=10)
segment2 = Segment("easy", distance=10)
workout1.segments.append(segment1)
workout1.segments.append(segment2)
week1.workouts.apend(workout1)
training_plan.weeks[1] = week1

segment1 = Segment(pace="easy", distance=10)

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
