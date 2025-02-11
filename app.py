from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Change to a secure key

db = SQLAlchemy(app)

# Model for User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Use hashing in production
    role = db.Column(db.String(20), nullable=False, default='Reporter')  # Default role is 'Reporter'

# Model for Incident
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    reporter = db.Column(db.String(80), nullable=False)
    endpoint = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Pending')

# Route: Dashboard (List all incidents)
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    incidents = Incident.query.all()
    return render_template('index.html', incidents=incidents, role=session.get('role'))

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = user.username
            session['role'] = user.role  # Store user role in session
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    return render_template('login.html')

# Route: Registration (Only allows Reporters)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password, role='Reporter')  # Only "Reporter" can register
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route: Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash('You have logged out.', 'info')
    return redirect(url_for('login'))

# Route: Report an Incident
@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_incident = Incident(
            date=request.form['date'],
            reporter=session['user'],
            endpoint=request.form['endpoint'],
            description=request.form['description'],
            category=request.form['category'],
            status='Pending'
        )
        db.session.add(new_incident)
        db.session.commit()
        flash('Incident successfully reported!', 'success')
        return redirect(url_for('index'))
    return render_template('report.html')

# Route: Update Incident Status (Only Responders)
@app.route('/update/<int:id>', methods=['POST'])
def update_status(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'Responder':  # Only Responders can update status
        flash('You do not have permission to update the status!', 'error')
        return redirect(url_for('index'))

    incident = Incident.query.get_or_404(id)
    incident.status = request.form['status']
    db.session.commit()
    flash('Incident status updated!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('incidents.db'):
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
