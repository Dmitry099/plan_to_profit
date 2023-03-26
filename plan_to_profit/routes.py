from flask import Blueprint, render_template, flash, redirect, url_for

from .forms import LoginForm

plan_to_profit = Blueprint(
    "plan_to_profit", __name__, template_folder="templates"
)


@plan_to_profit.route("/")
@plan_to_profit.route("/index")
def index():
    return render_template("base.html", title="Entry Point")


@plan_to_profit.get("/login")
def login_get():
    form = LoginForm()
    return render_template("login.html", title="Sign In", form=form)


@plan_to_profit.post("/login")
def login_post():
    form = LoginForm()
    flash(
        "Login requested for user {}, remember_me={}".format(
            form.username.data, form.remember_me.data
        )
    )
    return redirect(url_for("index"))
