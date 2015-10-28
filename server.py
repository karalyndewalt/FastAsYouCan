"""Training generator"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

#required for Flask session and the debug toolbar
app.secret_key = "ABC"

# so undefined variable in Jinga2 doesn't fail silently
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""

    return render_template("home.html")



if __name__ == "__main__":
    #must set to true befor invoking DebugToolbarExtension
    app.debug = True

    # connect_to_db(app)

    # comment out to turn debug off
    DebugToolbarExtension(app)

    app.run()
