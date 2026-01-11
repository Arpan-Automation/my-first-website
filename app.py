import os
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'premium-zen-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    position = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        hashed_pwd = generate_password_hash(request.form['password'])
        new_user = User(username=request.form['username'], password=hashed_pwd)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created! Login now.', 'success')
            return redirect(url_for('home'))
        except: flash('User already exists!', 'danger')
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username']).first()
    if user and check_password_hash(user.password, request.form['password']):
        session['user'] = user.username
        return redirect(url_for('dashboard'))
    flash('Invalid credentials!', 'danger')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('home'))
    employees = Employee.query.all()
    return render_template('dashboard.html', user=session['user'], employees=employees)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if 'user' in session:
        new_emp = Employee(name=request.form['name'], email=request.form['email'], position=request.form['position'])
        db.session.add(new_emp)
        db.session.commit()
        flash('Employee Added!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
def delete(id):
    if 'user' in session:
        emp = Employee.query.get(id)
        db.session.delete(emp)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)