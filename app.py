from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ================= MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    status = db.Column(db.String(50))
    deadline = db.Column(db.String(50))
    assigned_to = db.Column(db.String(100))
    project = db.Column(db.String(100))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= ROUTES =================

@app.route('/')
def home():
    return redirect(url_for('login'))

# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'])

        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=hashed_password,
            role=request.form['role']
        )

        db.session.add(user)
        db.session.commit()

        flash("Signup successful")
        return redirect(url_for('login'))

    return render_template('signup.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))

        flash("Invalid credentials")

    return render_template('login.html')

# DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():

    tasks = Task.query.all()

    completed = Task.query.filter_by(status="Completed").count()
    pending = Task.query.filter_by(status="Pending").count()

    return render_template(
        'dashboard.html',
        tasks=tasks,
        completed=completed,
        pending=pending
    )

# CREATE PROJECT
@app.route('/create-project', methods=['GET', 'POST'])
@login_required
def create_project():

    if current_user.role != "Admin":
        return "Access Denied"

    if request.method == 'POST':

        project = Project(
            title=request.form['title'],
            description=request.form['description']
        )

        db.session.add(project)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('create_project.html')

# CREATE TASK
@app.route('/create-task', methods=['GET', 'POST'])
@login_required
def create_task():

    if current_user.role != "Admin":
        return "Access Denied"

    if request.method == 'POST':

        task = Task(
            title=request.form['title'],
            status=request.form['status'],
            deadline=request.form['deadline'],
            assigned_to=request.form['assigned_to'],
            project=request.form['project']
        )

        db.session.add(task)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('create_task.html')

# MY TASKS
@app.route('/my-tasks')
@login_required
def my_tasks():

    tasks = Task.query.filter_by(
        assigned_to=current_user.name
    ).all()

    return render_template('my_tasks.html', tasks=tasks)

# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ================= MAIN =================

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)