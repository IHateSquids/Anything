from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager,
                         UserMixin, login_user,
                         login_required, logout_user,
                         current_user)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'.encode('utf-8')

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




# User model
class User(UserMixin, db.Model):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(80), unique=True, nullable=False)
   password = db.Column(db.String(120), nullable=False)
   email = db.Column(db.String(120), unique=True, nullable=False)


# Routes
@app.route('/')
def home():
   return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
   if request.method == 'POST':
       username = request.form['username']
       email = request.form['email']
       password = request.form['password']

       # Check if username or email already exists
       existing_user = User.query.filter_by(username=username).first()
       if existing_user:
           flash('Username already exists. Please choose another one.', 'error')
           return redirect(url_for('register'))

       existing_email = User.query.filter_by(email=email).first()  # Check if email already exists
       if existing_email:
           flash('Email already exists. Please choose another one.', 'error')
           return redirect(url_for('register'))

       # Create new user
       new_user = User(username=username, password=password, email=email)  # Include email here
       db.session.add(new_user)
       db.session.commit()

       flash('Registration successful! Please log in.', 'success')
       return redirect(url_for('login'))

   return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/users')
@login_required
def users():
   users = User.query.all()
   return render_template('users.html', users=users)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Run the application
if __name__ == '__main__':
   with app.app_context():
       db.create_all()
   app.run(debug=True)

