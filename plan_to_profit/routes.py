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
from phonenumbers import region_code_for_country_code
from sqlalchemy_utils import PhoneNumber
from werkzeug.urls import url_parse

from plan_to_profit.email import send_password_reset_email
from plan_to_profit.forms import (
    ClientForm,
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
    PhotoPlaceForm,
)
from plan_to_profit.models import User, db, Client, PhotoPlace

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
        return redirect(
            url_for("plan_to_profit.user", username=current_user.username)
        )
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
            page=clients.next_num,
        )
        if clients.has_next
        else None
    )
    prev_url = (
        url_for(
            "plan_to_profit.clients_list",
            page=clients.prev_num,
        )
        if clients.has_prev
        else None
    )
    return render_template(
        "clients_list.html",
        title="Clients List",
        user=current_user,
        clients=clients.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@plan_to_profit.route("/create_client", methods=["GET", "POST"])
@login_required
def create_client():
    form = ClientForm()
    if form.validate_on_submit():
        number = PhoneNumber(form.phone_number.data)
        region_code = region_code_for_country_code(number.country_code)
        client = Client(
            name=form.name.data,
            _phone_number=number.national,
            phone_country_code=region_code,
            contact_details=form.contact_details.data,
            user_id=current_user.id,
        )
        if form.email.data:
            client.email = form.email.data
        db.session.add(client)
        db.session.commit()
        flash("New client was successfully added.")
        return redirect(url_for("plan_to_profit.clients_list"))
    return render_template(
        "client_creator.html", title="Create Client", form=form
    )


@plan_to_profit.route("/edit_client/<client_id>", methods=["GET", "POST"])
@login_required
def edit_client(client_id):
    current_client = Client.query.get(client_id)
    form = ClientForm()
    if form.validate_on_submit():
        number = PhoneNumber(form.phone_number.data)
        region_code = region_code_for_country_code(number.country_code)
        current_client.name = form.name.data
        current_client._phone_number = number.national
        current_client.phone_country_code = region_code
        current_client.contact_details = form.contact_details.data
        if form.email.data:
            current_client.email = form.email.data
        db.session.commit()
        flash("Client was successfully edited.")
        return redirect(url_for("plan_to_profit.clients_list"))
    elif request.method == "GET":
        form.name.data = current_client.name
        form.phone_number.data = current_client.phone_number.international
        form.email.data = current_client.email
        form.contact_details.data = current_client.contact_details
    return render_template(
        "client_editor.html", title="Edit Client", form=form
    )


@plan_to_profit.route("/photo_place_list")
@login_required
def photo_place_list():
    page = request.args.get("page", 1, type=int)
    photo_places = current_user.photo_places.order_by(
        PhotoPlace.name.asc()
    ).paginate(
        page=page,
        per_page=current_app.config["PLACES_PER_PAGE"],
        error_out=False,
    )
    next_url = (
        url_for(
            "plan_to_profit.photo_place_list",
            page=photo_places.next_num,
        )
        if photo_places.has_next
        else None
    )
    prev_url = (
        url_for(
            "plan_to_profit.photo_place_list",
            page=photo_places.prev_num,
        )
        if photo_places.has_prev
        else None
    )
    return render_template(
        "photo_places_list.html",
        title="Photo Places List",
        user=current_user,
        photo_places=photo_places.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@plan_to_profit.route("/create_photo_place", methods=["GET", "POST"])
@login_required
def create_photo_place():
    form = PhotoPlaceForm()
    if form.validate_on_submit():
        photo_place = PhotoPlace(
            name=form.name.data,
            country=form.country.data,
            address=form.address.data,
            user_id=current_user.id,
        )
        db.session.add(photo_place)
        db.session.commit()
        flash("New photo place was successfully added.")
        return redirect(url_for("plan_to_profit.photo_place_list"))
    return render_template(
        "photo_place_creator.html", title="Create Photo Place", form=form
    )


@plan_to_profit.route(
    "/edit_photo_place/<photo_place_id>", methods=["GET", "POST"]
)
@login_required
def edit_photo_place(photo_place_id):
    current_photo_place = PhotoPlace.query.get(photo_place_id)
    form = PhotoPlaceForm()
    if form.validate_on_submit():
        current_photo_place.name = form.name.data
        current_photo_place.country = form.country.data
        current_photo_place.address = form.address.data
        db.session.commit()
        flash("Photo place was successfully edited.")
        return redirect(url_for("plan_to_profit.photo_place_list"))
    elif request.method == "GET":
        form.name.data = current_photo_place.name
        form.country.data = current_photo_place.country
        form.address.data = current_photo_place.address
    return render_template(
        "photo_place_editor.html", title="Edit Photo Place", form=form
    )
