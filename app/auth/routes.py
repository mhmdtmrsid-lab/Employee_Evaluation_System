from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.auth import auth
from app.auth.forms import LoginForm
from app.models import Supervisor

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        # Check domain explicitly again just in case, though form handles it
        if not (form.email.data.endswith('@groupatlantic') or '@groupatlantic.' in form.email.data):
             flash('Invalid email domain. Must be @groupatlantic.', 'danger')
             return render_template('auth/login.html', title='Login', form=form)

        user = Supervisor.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
