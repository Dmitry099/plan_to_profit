from flask import (
    Blueprint,
    current_app,
    render_template,
    flash,
    redirect,
    url_for,
    request,
)
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from plan_to_profit.email import send_password_reset_email
from plan_to_profit.forms import (
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
)
from plan_to_profit.models import User, db, Client

plan_to_profit = Blueprint(
    "plan_to_profit", __name__, template_folder="templates"
)


@plan_to_profit.route("/")
@plan_to_profit.route("/index")
@login_required
def index():
    return render_template("index.html", title="Home Page")


@plan_to_profit.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("plan_to_profit.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("plan_to_profit.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("plan_to_profit.index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@plan_to_profit.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("plan_to_profit.index"))


@plan_to_profit.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("plan_to_profit.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("plan_to_profit.login"))
    return render_template("register.html", title="Register", form=form)


@plan_to_profit.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)


@plan_to_profit.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("plan_to_profit.edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
    return render_template(
        "profile_editor.html", title="Edit Profile", form=form
    )


@plan_to_profit.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("plan_to_profit.index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instructions to reset your password")
        return redirect(url_for("plan_to_profit.login"))
    return render_template(
        "reset_password_request.html", title="Reset Password", form=form
    )


@plan_to_profit.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("plan_to_profit.index"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("plan_to_profit.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.")
        return redirect(url_for("plan_to_profit.login"))
    return render_template("reset_password.html", form=form)


@plan_to_profit.route("/clients_list")
@login_required
def clients_list():
    page = request.args.get("page", 1, type=int)
    clients = current_user.clients.order_by(Client.name.asc()).paginate(
        page=page,
        per_page=current_app.config["CLIENTS_PER_PAGE"],
        error_out=False,
    )
    next_url = (
        url_for(
            "plan_to_profit.clients_list",
            username=user.username,
            page=clients.next_num,
        )
        if clients.has_next
        else None
    )
    prev_url = (
        url_for(
            "plan_to_profit.clients_list",
            username=user.username,
            page=clients.prev_num,
        )
        if clients.has_prev
        else None
    )
    return render_template(
        "clients_list.html",
        title="Clients List",
        user=user,
        clients=clients.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@plan_to_profit.route("/edit_client", methods=["GET", "POST"])
@login_required
def edit_client():
    return None
