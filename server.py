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
TRAINING_PLAN = [
    (0.60, "Easy runs @ {easy} to meet mileage goals"),
    (0.60, "Easy runs @ {easy} to meet mileage goals"),
    (0.60, "Easy runs @ {easy} to meet mileage goals"),
    (0.60, "Easy runs @ {easy} to meet mileage goals",
     "Long run @ {easy}, distance: {0.162 * peakmileage} "),
    (0.60, "Easy runs @ {easy} to meet mileage goals",
     "Long run @ {easy}, distance: {0.162 * peakmileage} "),
    (0.60, "Easy runs @ {easy} to meet mileage goals",
     "Long run @ {easy}, distance: {0.162 * peakmileage} "),
    (0.80, "Long run @ {easy}, distance: {0.216 * peakmileage} ",
     "Tempo - 20 minutes @ {tempo} broken into 2 x 10 minutes with 1 minutes rest"),
    (0.80, "Long run @ {easy}, distance: {0.216 * peakmileage} ",
     "Tempo - 20 minutes @ {tempo} broken into 2 x 10 minutes with 1 minutes rest"),
    (0.70, "Two Easy runs @ {easy}, total distance: {0.189 * peakmileage}",
     "Tempo - 30 minutes @ {tempo} broken into 3 x 10 minutes with 1 minutes rest"),
    (0.90, "Long run @ {easy}, distance: {0.243 * peakmileage} ",
     "Tempo - 30 minutes @ {tempo} broken into 3 x 10 minutes with 1 minutes rest"),
    (0.90, "Long run @ {easy}, distance: {0.243 * peakmileage} ",
     "Tempo - 30 minutes @ {tempo} broken into 2 x 15 minutes with 1 minutes rest"),
    (0.70, "Marathon run for 12 miles @ {marathon}. Finish with 5 to 6 20-30 second strides with 1 minutes rest.",
     "Tempo - 30 minutes @ {tempo} broken into 2 x 15 minutes with 1 minutes rest"),
    (1.0, "Tempo 3 x 5 minutes @ {tempo}, with 1 minute rest. Easy ({easy}) for 60 minutes. Tempo 3 x 5 minutes @ {tempo}, with 1 minute rest. ",
     "Tempo 2 x 10 minutes @ {tempo}, with 2 minute rest. Easy ({easy}) for 75 minutes."),
    (0.90, "Marthon pace ({marathon}), for 15 miles.",
     "Tempo 2 x 10 minutes @ {tempo}, with 2 minute rest. Easy ({easy}) for 75 minutes."),
    (1.0, "Long run @ {easy}, distance: {0.25 * peakmileage} ",
     "Tempo 2 x 10 minutes @ {tempo}, with 2 minute rest. Easy ({easy}) for 75 minutes."),
    (0.80, "Tempo 3 x 5 minutes @ {tempo}, with 1 minute rest. Easy ({easy}) for 60 minutes. Tempo 3 x 5 minutes @ {tempo}, with 1 minute rest. ",
     "Tempo 2 x 10 minutes @ {tempo}, with 2 minute rest. Easy ({easy}) for 75 minutes."),
    (0.80, "Marathon pace ({marathon}) for 12 miles.",
     "Easy pace ({easy}) for 2 miles. Tempo - 25 minutes @ {tempo} broken into 5 x 5 minutes with 1 minute rest"),
    (0.60, "Two Easy runs @ {easy}, total distance: {0.162 * peakmileage}",
     "Easy pace ({easy}) for 2 miles. Tempo - 25 minutes @ {tempo} broken into 5 x 5 minutes with 1 minute rest"),
]


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
    mileage = float(request.form.get("mileage"))
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
    new_user = User(email=email, weekly_mileage=mileage)
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


@app.route("/generate-calendar")
def creat_calendar():
    training_plan = TRAINING_PLAN

    return render_template("training-plan.html", training_plan=training_plan)

if __name__ == "__main__":
    #must set to true befor invoking DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # comment out to turn debug off
    DebugToolbarExtension(app)

    app.run()
