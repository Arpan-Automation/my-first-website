from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Session ke liye zaroori hai
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# 1. User Table (Login/Signup ke liye)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# 2. Employee Table (Management ke liye)
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    position = db.Column(db.String(100), nullable=False)

# Database Create
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        hashed_pwd = generate_password_hash(pwd)
        new_user = User(username=user, password=hashed_pwd)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created! Please Login.', 'success')
            return redirect(url_for('home'))
        except:
            flash('Username already exists!', 'danger')
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    user = request.form['username']
    pwd = request.form['password']
    found_user = User.query.filter_by(username=user).first()
    if found_user and check_password_hash(found_user.password, pwd):
        session['user'] = user # Session mein user save kiya
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid Login Credentials', 'danger')
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        employees = Employee.query.all() # Saare employees fetch kiye
        return render_template('dashboard.html', user=session['user'], employees=employees)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# --- Employee Management Routes ---

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if 'user' in session:
        name = request.form['name']
        email = request.form['email']
        pos = request.form['position']
        new_emp = Employee(name=name, email=email, position=pos)
        db.session.add(new_emp)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('home'))

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    if 'user' in session:
        emp = Employee.query.get(id)
        db.session.delete(emp)
        db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)