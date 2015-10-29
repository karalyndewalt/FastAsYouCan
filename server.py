"""Training generator"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from datetime import timedelta
import calculator
from model import connect_to_db, db, User

app = Flask(__name__)

#required for Flask session and the debug toolbar
app.secret_key = "ABC"

# so undefined variable in Jinga2 doesn't fail silently
# app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""

    return render_template("home.html")


 #     return render_template("home.html", blah=blah)

@app.route("/calculate-VDOT")
def create_table():
    hr = float(request.args.get("hours"))
    mm = float(request.args.get("minutes"))
    ss = float(request.args.get("seconds"))
    units = request.args.get("units")
    distance = float(request.args.get("distance"))
    mileage = float(request.args.get("mileage"))

    # have function in calculator.py (with doctest) would it be clear to call .calculator.function()?
    time = mm + (hr * 60) + (ss / 60)


    VDOT = calculator.user_VDOT(distance, units, time)
    print VDOT
    # session["VDOT"] = VDOT

    new_user = User(distance=distance, time=time, VDOT=VDOT, weekly_mileage=mileage)
    db.session.add(new_user)
    db.session.commit()

    return render_template("form-submit.html")




if __name__ == "__main__":
    #must set to true befor invoking DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # comment out to turn debug off
    DebugToolbarExtension(app)

    app.run()
