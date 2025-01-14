from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import db, User
from run import app, login_manager

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        # password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
        password = request.form.get('password')
        display_name = request.form.get('display_name')
        bio = request.form.get('bio')
        gender = request.form.get('gender') if request.form.get('gender') else None
        age = request.form.get('age', type=int) if request.form.get('age') else None
        location = request.form.get('location')
        profile_pic = request.files.get('profile_pic')

        # Save profile picture if uploaded
        profile_pic_path = None
        if profile_pic:
            profile_pic_path = f'static/uploads/{secure_filename(profile_pic.filename)}'
            profile_pic.save(profile_pic_path)

        # Create user
        new_user = User(
            username=username,
            email=email,
            password=password,
            display_name=display_name,
            bio=bio,
            gender=gender,
            age=age,
            location=location,
            profile_pic=profile_pic_path if profile_pic_path else "/static/images/default_profile.png"
        )

        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')

        if not display_name or display_name.strip() == "":
            new_user.display_name = f"user{new_user.id}"
            db.session.commit()  # Commit again to update the display_name

        return redirect(url_for('login'))

    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        # if user and check_password_hash(user.password, password):
        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()

    # Clear flashed messages explicitly
    session.pop('_flashes', None)

    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
