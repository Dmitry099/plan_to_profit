from flask import render_template

from plan_to_profit.routes import plan_to_profit
from plan_to_profit.models import db


@plan_to_profit.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@plan_to_profit.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500
