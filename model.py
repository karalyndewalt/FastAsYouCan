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
    weekly_mileage = db.Column(db.Integer, nullable=True)

    def greet(self):
        """Greet using email"""
        return "Hello, {}".format(self.email)

    # TODO(kara): change all 'emt' to 'intensity'

    def paces(self, emt):
        """Returns object of Pace class"""
        # finds users most recent race
        most_recent_race = Race.query.filter(Race.user_id == self.user_id).order_by(Race.race_id.desc()).first()
        # __init__ on Pace looks like: Pace(self, VDOT, intensity(as string))
        VDOT = most_recent_race.VDOT()
        pace_obj = Pace(VDOT, emt)
        return pace_obj

    def most_recent_race(self):
        race = Race.query.filter(Race.user_id == self.user_id).order_by(Race.race_id.desc()).first()
        return race

    def training_plan(self):
        return TrainingPlan(self)

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
         # TODO(kara): rewrite using list comp, and time date method .total_seconds

        p_range = self.pace_range()
        time_range = []
        for i in p_range:
            time_str = str(i)
            token_time = time_str.split(".")
            time = token_time[0]
            time = time[-5:]
            time_range.append(time)
        return time_range

    def __repr__(self):
            """Provide a useful representation when printed"""

            string = "<Paces as tuple of VDOT percentage for {} intensity>"
            return string.format(self.intensity)


class TrainingPlan(object):
    """Returns dictionary of Weeks"""

# weeks is a list of Weeks
    def __init__(self, user):
        self.weeks = []

        # week 1 - 3
        self.weeks.append(Week(user, 0.60, plan=self, workouts=()))
        self.weeks.append(Week(user, 0.60, plan=self, workouts=()))
        self.weeks.append(Week(user, 0.60, plan=self, workouts=()))
        # week 4 - 6
        self.weeks.append(Week(user, 0.60, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.162),
            ),
        )))
        self.weeks.append(Week(user, 0.60, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.162),
            ),
        )))
        self.weeks.append(Week(user, 0.60, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.162),
            ),
        )))
        # weeks 7 & 8
        self.weeks.append(Week(user, 0.80, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.216),
                ),
            Workout(
                Segment(emt='tempo', user=user, rep=2, time=10, rest=1),
            ),
        )))
        self.weeks.append(Week(user, 0.80, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.216),
            ),
            Workout(
                Segment(emt='tempo', user=user, rep=2, time=10, rest=1),
            ),
        )))
        # week 9
        self.weeks.append(Week(user, 0.70, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.0945),
                Segment(emt='easy', user=user, distance_as_percent=0.0945),
            ),
            Workout(
                Segment(emt='tempo', user=user, rep=2, time=15, rest=1),
            ),
        )))
        # week 10 and 11
        self.weeks.append(Week(user, 0.90, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.243)
            ),
            Workout(
                Segment(emt='tempo', user=user, rep=3, time=10, rest=1),
            ),
        )))
        self.weeks.append(Week(user, 0.90, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.243),
            ),
            Workout(
                Segment(emt='tempo', user=user, rep=3, time=10, rest=1),
            ),
        )))
        # week 12
        self.weeks.append(Week(user, 0.70, plan=self, workouts=(
            Workout(
                Segment(emt='marathon', user=user, distance_in_miles=12),
            ),
            Workout(
                Segment(emt='tempo', user=user, rep=2, time=15, rest=1),
            ),
        )))
        # week 13
        self.weeks.append(Week(user, 1.0, plan=self, workouts=(
            Workout(
                Segment(emt='tempo', user=user, rep=3, time=5, rest=1),
                Segment(emt='easy', user=user, time=60),
                Segment(emt='tempo', user=user, rep=3, time=5, rest=1),
            ),
            Workout(
                Segment(emt='tempo', user=user, rep=2, time=10, rest=2),
                Segment(emt='easy', user=user, time=75)
                ),
        )))
        # week 14
        self.weeks.append(Week(user, 0.90, plan=self, workouts=(
            Workout(
                Segment(emt='marathon', user=user, distance_in_miles=15),
            ),
            Workout(
                Segment(emt='tempo', user=user, rep=2, time=10, rest=2),
                Segment(emt='easy', user=user, time=75),
            ),
        )))
        # week 15
        self.weeks.append(Week(user, 1.0, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.25),
            ),
            Workout(
                Segment(emt='tempo', user=user, rep=2, time=10, rest=2),
                Segment(emt='easy', user=user, time=75),
            ),
        )))
        # week 16
        self.weeks.append(Week(user, 0.80, plan=self, workouts=(
            Workout(
                Segment(emt='tempo', user=user, rep=3, time=5, rest=1),
                Segment(emt='easy', user=user, time=60),
                Segment(emt='tempo', user=user, rep=3, time=5, rest=1),
            ),
            Workout(
                Segment(emt='tempo', user=user, rep=2, time=10, rest=2),
                Segment(emt='easy', user=user, time=75),
            ),
        )))
        # week 17
        self.weeks.append(Week(user, 0.80, plan=self, workouts=(
            Workout(
                Segment(emt='marathon', user=user, distance_in_miles=12),
            ),
            Workout(
                Segment(emt='easy', user=user, distance_in_miles=2),
                Segment(emt='tempo', user=user, rep=5, time=5, rest=1),
            ),
        )))
        # week 18
        self.weeks.append(Week(user, 0.60, plan=self, workouts=(
            Workout(
                Segment(emt='easy', user=user, distance_as_percent=0.081),
                Segment(emt='easy', user=user, distance_as_percent=0.081),
            ),
            Workout(
                Segment(emt='easy', user=user, distance_in_miles=2),
                Segment(emt='tempo', user=user, rep=5, time=5, rest=1),
            ),
        )))


class Week(object):
    """Returns x days of training as a list

    Uses user race.VDOT to determine distance of workouts, and remainder of
    peak mileage to assign distances to non-quality days.
    """
# TODO(kara): CLEAN - peakmileage should come from the User class. User.weekly_mileage
# workouts - comes as a list, should only accept a list (even an empty one)
# peakmileage = User.weekly_mileage, do not need this in the __init__ because
# the Week will be called as a method from the User class
    def __init__(self, user, percent_peak_mileage, plan, workouts, days=6):
        self.user = user
        #  percent_peak_mileage is specified for each TP, must pass in.
        self.percent_peak_mileage = percent_peak_mileage
        # user_id from User class/instance, as class method
        self.peakmileage = calculator.miles_to_meters(user.weekly_mileage)
        self.week_in_meters = (self.percent_peak_mileage * self.peakmileage)
        # self.week_in_miles = (self.percent_peak_mileage * self.peakmileage)
        self.plan = plan
        self.days = days
        self.quality_distance = sum(workout.distance for workout in workouts)
        self.workouts = self.create_remaining_days(workouts)
        for workout in self.workouts:
            workout.week = self
        self.distance = sum(workout.distance for workout in self.workouts)
        # print "WEEK DIST: ", self.distance

    def create_remaining_days(self, workouts):
        """Generate remaining training days"""

        days = self.days - len(workouts)
        # print "NUM days: ", days
        # print "week_in_meters: ", self.week_in_meters
        # print "quality_distance ", self.quality_distance
        rem_dist = self.week_in_meters - self.quality_distance
        distance = rem_dist/days
        for i in range(days):
            seg = Segment(emt="easy", user=self.user)
            seg.distance = distance
            workout = Workout(seg)
            workouts = workouts + (workout,)
        remainder_of_seven = 7 - len(workouts)
        for i in range(remainder_of_seven):
            workouts = workouts + (0,)
        return workouts

    def show_week(self):

        return "Week Distance: {}".format(self.distance)


class Workout(object):
    """Returns list of segments

    a single workout is a list of segments
    'quality days', specific instructions for workouts with distance, time, pace attributes
    """
    # workout is a list of segments(plural), segments = [segment, segment, segment....]
    # segments should only accept a list
    # use segment.distance() to get distance of workout.

    def __init__(self, *segments):
        # TODO(kara):
        # if not isinstance(segments, list):
        #     raise TypeError("whatever you want to say")

        self.segments = segments
        for segment in self.segments:
            segment.workout = self
        self.distance = sum(seg.calc_distance() for seg in segments)
        # print"workout distance: ", self.distance
        self.week = None

    def show_workout(self):
        # for seg in self.segments:
        #     seg.show_segment()
        return "Workout Distance: {}".format(self.distance)


class Segment(object):
    """Pace() and distance or time components of a workout"""

# TODO(kara):
# think about default of time as 1
# make abstraction or class methods?? LATER

    def __init__(self, emt, user, workout=None, rep=1, time=None, distance_in_miles=None,
                 distance_as_percent=None, rest=None):

        # emt is the STRING: "easy", "marathon", or "tempo"
        self.emt = emt
        # when segment is called from the User class user_id will not need to be passed in
        self.user = user
        # uses instance method from User class
        self.pace = user.paces(self.emt)
        self.rep = rep
        self.time = time
        if time:
            self.total_time = time * rep
        self.rest = rest
        # adds bi-directional accountability, linked to parent instance
        self.workout = None
        # peakmileage in meters
        peakmileage = calculator.miles_to_meters(self.user.weekly_mileage)
        self.distance = None
        if distance_as_percent:
            self.distance = (distance_as_percent * peakmileage)
        # in meters
        if distance_in_miles:
            self.distance = calculator.miles_to_meters(distance_in_miles)
        # there is another way to define self.distance --> ? when generated from
        # the Week the segment distance is seg.distance...
        # sooo set self.distance = None so it can be set outside of the __init__?
        # and probably more... sit.

    def calc_distance(self):
        """
        """
        # needs to determine distance uses pace.velocity OR self.distance * time
        if self.time:
            velocity_range = self.pace.velocity()
            distance = velocity_range[1] * self.total_time
        else:
            distance = self.distance
        return distance

    # def length_workout(self):
    #     for seg in self.workout.segments:
    #         self.workout.distance = sum(seg.calc_distance())
    #         print "length_workout:", self.workout.distance
    #     # the sum of all the segments that make up the week

    def show_segment(self):
        """Returns string representation of the segment"""

        seg_tuple = ()
        if self.pace:
            pace_as_time = self.pace.convert_timedelta()
            pace = "Pace: {} ".format(pace_as_time[1])
            seg_tuple += (pace,)
        if self.rep > 1:
            reps = "Reps: {} x {} min. ".format(self.rep, self.time)
            seg_tuple += (reps,)
        if self.time:
            time = "Time: {} ".format(self.total_time)
            seg_tuple += (time,)
        if self.distance:
            distance = "Distance: {} ".format(self.distance)
            seg_tuple += (distance,)

        return seg_tuple

    def __repr__(self):
        """Return string representation of segment"""

        string = "<Intensity: {}, reps: {}, time: {}, rest: {}>"
        return string.format(self.emt, self.rep, self.time, self.rest)



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
