from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# -------------------- DATABASE MODELS --------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100))
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))

# -------------------- LOGIN --------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- ROUTES --------------------

@app.route('/')
def home():
    visitor_ip = request.remote_addr
    new_visitor = Visitor(ip_address=visitor_ip)
    db.session.add(new_visitor)
    db.session.commit()

    photos = Photo.query.all()
    return render_template("home.html", photos=photos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")

    return render_template("login.html")

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    visitors = Visitor.query.all()

    if request.method == 'POST':
        file = request.files['photo']
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_photo = Photo(filename=filename)
            db.session.add(new_photo)
            db.session.commit()

    return render_template("dashboard.html", visitors=visitors)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# --------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create default user (only once)
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", password="admin123")
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
