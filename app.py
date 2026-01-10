from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "arpan_next_zen_secret_key" 

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        uname = request.form.get('username').strip()
        passw = request.form.get('password').strip()
        user = User.query.filter_by(username=uname).first()
        if user and user.password == passw:
            session['user'] = user.username
            return redirect(url_for('dashboard'))
        return "<h3>Invalid Access! <a href='/'>Try Again</a></h3>"
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uname = request.form.get('username').strip()
        passw = request.form.get('password').strip()
        if User.query.filter_by(username=uname).first():
            return "Identity exists! <a href='/signup'>Try another</a>"
        new_user = User(username=uname, password=passw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        all_users = User.query.all()
        return render_template('dashboard.html', name=session['user'], users=all_users)
    return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete_user(id):
    if 'user' in session:
        user_to_delete = User.query.get_or_404(id)
        db.session.delete(user_to_delete)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)