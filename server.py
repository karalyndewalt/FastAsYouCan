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
    new_user = User(email=email)
    db.session.add(new_user)
    db.session.commit()

    user_obj = User.query.filter(User.email == email).first()
    user_id = user_obj.user_id
    session["user_id"] = user_id

    new_race = Race(user_id=session["user_id"], distance=distance_in_meters, time=time)
    db.session.add(new_race)
    db.session.commit()

    session["VDOT"] = new_race.VDOT()

    return render_template("form-submit.html", VDOT=session["VDOT"])


if __name__ == "__main__":
    #must set to true befor invoking DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # comment out to turn debug off
    DebugToolbarExtension(app)

    app.run()
