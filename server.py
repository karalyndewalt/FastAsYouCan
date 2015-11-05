"""Training generator"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from datetime import timedelta
import calculator
from model import connect_to_db, db, User, Race, Pace

app = Flask(__name__)

#required for Flask session and the debug toolbar
app.secret_key = "ABC"

# so undefined variable in Jinga2 doesn't fail silently
# app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""

    return render_template("home.html")


 # return render_template("home.html", blah=blah)

@app.route("/calculate-VDOT", methods=["POST"])
def create_table():
    hr = request.form.get("hours")
    mm = request.form.get("minutes")
    ss = request.form.get("seconds")
    peak_mileage = float(request.form.get("mileage"))
    units = request.form.get("units")
    distance = float(request.form.get("distance"))
    email = request.form.get("email")

    # have function in calculator.py (with doctest) would it be clear to call .calculator.function()?
    time = float(mm) + (float(hr) * 60) + (float(ss) / 60)

    distance_in_meters = calculator.convert_distance_to_meters(distance, units)

    # should exist on Race class, remove VDOT variable
    # VDOT = calculator.user_VDOT(distance, units, time)
    # print VDOT
    # session["VDOT"] = VDOT
    # -------TODO--------
        # send distance and time to races tabel under user email/id
    new_user = User(email=email, weekly_mileage=peak_mileage)
    db.session.add(new_user)
    db.session.commit()

    user_obj = User.query.filter(User.email == email).first()
    user_id = user_obj.user_id
    session["user_id"] = user_id

    new_race = Race(user_id=session["user_id"], distance=distance_in_meters, time=time)
    db.session.add(new_race)
    db.session.commit()

    session["VDOT"] = new_race.VDOT()

    return render_template("generate-calendar.html", VDOT=session["VDOT"])


def gen_training_plan(easy, marathon, tempo, peak_mileage):
    """Returns full training plan as [(fraction peak_mileage, [q1, q2])]"""

    training_plan = [
        # (fraction peak_mileage, [Q1,
        #                          Q2])
        (0.60, "Easy runs @ {easy}, to meet mileage goals".format(easy=easy)),
        (0.60, "Easy runs @ {easy}, to meet mileage goals".format(easy=easy)),
        (0.60, "Easy runs @ {easy}, to meet mileage goals".format(easy=easy)),
        (0.60, "Easy runs @ {easy}, to meet mileage goals".format(easy=easy),
            "Long run @ {easy}, distance: {distance}".format(easy=easy, distance=0.162 * peak_mileage)),
        (0.60, "Easy runs @ {easy}, to meet mileage goals".format(easy=easy),
            "Long run @ {easy}, distance: {distance}".format(easy=easy, distance=0.162 * peak_mileage)),
        (0.60, "Easy runs @ {easy}, to meet mileage goals".format(easy=easy),
            "Long run @ {easy}, distance: {distance}".format(easy=easy, distance=0.162 * peak_mileage)),
        (0.80, "Long run @ {easy}, distance: {distance}".format(easy=easy, distance=0.216 * peak_mileage),
            "Tempo - 20 minutes @ {tempo}, broken into 2 x 10 minutes with 1 minutes rest".format(tempo=tempo)),
        (0.80, "Long run @ {easy}, distance: {distance}".format(easy=easy, distance=0.216 * peak_mileage),
            "Tempo - 20 minutes @ {tempo}, broken into 2 x 10 minutes with 1 minutes rest".format(tempo=tempo)),
        (0.70, "Two Easy runs @ {easy}, total distance:{distance}".format(easy=easy, distance=0.189 * peak_mileage),
            "Tempo - 30 minutes @ {tempo}, broken into 3 x 10 minutes with 1 minutes rest".format(tempo=tempo)),
        (0.90, "Long run @ {easy}, distance: {distance}".format(easy=easy, distance=0.243 * peak_mileage),
            "Tempo - 30 minutes @ {tempo}, broken into 3 x 10 minutes with 1 minutes rest".format(tempo=tempo)),
        (0.90, "Long run @ {easy}, distance: {distance}".format(easy=easy, distance=0.243 * peak_mileage),
            "Tempo - 30 minutes @ {tempo}, broken into 2 x 15 minutes with 1 minutes rest".format(tempo=tempo)),
        (0.70, "Marathon run for 12 miles @ {marathon}. Finish with 5 to 6 20-30 second strides with 1 minutes rest.".format(marathon=marathon),
            "Tempo - 30 minutes @ {tempo}, broken into 2 x 15 minutes with 1 minutes rest".format(tempo=tempo)),
        (1.0, "Tempo 3 x 5 minutes @ {tempo}, with 1 minute rest. Easy run @ {easy}, for 60 minutes. Tempo 3 x 5 minutes @  {tempo}, with 1 minute rest.".format(easy=easy, tempo=tempo),
            "Tempo 2 x 10 minutes @ {tempo}, with 2 minute rest. Easy run @ {easy}, for 75 minutes.".format(easy=easy, tempo=tempo)),
        (0.90, "Marthon - 15 miles @ ".format(marathon=marathon),
            "Tempo 2 x 10 minutes @ {tempo}, with 2 minute rest. Easy run @ {easy}, for 75 minutes.".format(easy=easy, tempo=tempo)),
        (1.0, "Long run @ {easy}, distance: {distance}".format(easy=easy, distance=(0.25 * peak_mileage)),
            "Tempo 2 x 10 minutes @ {tempo}, with 2 minute rest. Easy run @ {easy}, for 75 minutes.".format(easy=easy, tempo=tempo)),
        (0.80, "Tempo 3 x 5 minutes @ {tempo}, with 1 minute rest. Easy run @ {easy}, for 60 minutes. Tempo 3 x 5 minutes @ {tempo}, with 1 minute rest.".format(tempo=tempo, easy=easy),
            "Tempo 2 x 10 minutes @ {tempo}, with 2 minute rest. Easy run @ {easy}, for 75 minutes.".format(tempo=tempo, easy=easy)),
        (0.80, "Marathon run for 12 miles @ {marathon} ".format(marathon=marathon),
            "Easy run @ {easy}, for 2 miles. Tempo - 25 minutes @ {tempo}, broken into 5 x 5 minutes with 1 minute rest.".format(easy=easy, tempo=tempo)),
        (0.60, "Two Easy runs @ {easy}, total distance: {distance}".format(easy=easy, distance=0.162 * peak_mileage),
            "Easy run @ {easy}, for 2 miles. Tempo - 25 minutes @ {tempo}, broken into 5 x 5 minutes with 1 minute rest".format(easy=easy, tempo=tempo))
    ]
    return training_plan


# def gen_pace_objects(VDOT):
#     e = "easy"
#     m = "marathon"
#     t = "tempo"
#     easy = Pace(VDOT, e)
#     marathon = Pace(VDOT, m)
#     tempo = Pace(VDOT, t)

#     return easy, marathon, tempo
    # returns a tuple - weirdness, this is not what you want.^^^
    # for loop and list comp are better ideas, you will keep access to the instances
    # and have nice access to them as individuals to pass into the training_plan

@app.route("/generate-calendar")
def creat_calendar():
    # change this to call off the user_id when you have login conf.
    VDOT = session["VDOT"]
    user_id = session["user_id"]
    # make a pace instance(s) ---> returns obj, see convert_timedelta() bellow
    e = Pace(VDOT, "easy")
    m = Pace(VDOT, "marathon")
    t = Pace(VDOT, "tempo")

    e_timedelta = e.convert_timedelta()
    m_timedelta = m.convert_timedelta()
    t_timedelta = t.convert_timedelta()

    easy = e_timedelta[1]
    marathon = m_timedelta[1]
    tempo = t_timedelta[1]

    # query for peak mileage
    user = User.query.filter(User.user_id == user_id).first()
    peak_mileage = user.weekly_mileage
    # call gen_taining_plan()
    user_plan = gen_training_plan(str(easy), str(marathon), str(tempo), peak_mileage)


    # 11/3 this may need to live in another place
    # 11/3 will call all EMT through this function, as for loop?
    # see workspace.py for more "tests"


    return render_template("training-plan.html", training_plan=user_plan)

if __name__ == "__main__":
    #must set to true befor invoking DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # comment out to turn debug off
    DebugToolbarExtension(app)

    app.run()
