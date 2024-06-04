import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user
from werkzeug.security import generate_password_hash, check_password_hash

# Create a logger instance for the app
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # Set the logging level to the lowest level DEBUG

# Set up the logging configuration for the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Initialize SQLAlchemy for database operations
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# User model for database representation
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes for Progressive Web App (PWA)

@app.route('/')
def home():
    return render_template('index.html')  # Render the main home page

@app.route('/offline.html')
def offline():
    return render_template('offline.html')  # Render the offline page for PWA

@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')  # Serve the service worker file

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, max-age=0'  # Set appropriate caching headers
    return response

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            if check_password_hash(user.password, password):
                login_user(user)  # Login the user if credentials match
                flash('Login successful!', 'success')  # Flash success message
                logger.info(f'User {username} logged in')  # Log user login with INFO level
                return redirect(url_for('home'))  # Redirect to the home page
            else:
                flash('Invalid password. Please try again.', 'error')  # Flash error for incorrect password
        else:
            flash('User not found. Please sign up first.', 'error')  # Flash error for user not found

    return render_template('login.html')  # Render the login page

# Other routes and functions...

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)