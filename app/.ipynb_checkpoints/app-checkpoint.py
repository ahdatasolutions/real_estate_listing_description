# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import time
import pandas as pd
import replicate  # Add this line to import the necessary package

# Flask configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = 'mysecret'
db = SQLAlchemy(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-Login's user loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Index route
@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Add Room route
@app.route('/add-room', methods=['GET', 'POST'])
@login_required
def add_room():
    if request.method == 'POST':
        room_names = request.form.getlist('room-name')
        room_files = request.files.getlist('room-file')
        
        output_dataframe = pd.DataFrame(columns=['Room Name', 'Description', 'Time Taken'])

        for room_name, room_file in zip(room_names, room_files):
            if room_file:
                file_path = os.path.join('uploads', room_file.filename)
                room_file.save(file_path)
                
                start_time = time.time()
                room_description = get_room_description(room_name, file_path)
                end_time = time.time()

                output_dataframe = output_dataframe.append({
                    'Room Name': room_name,
                    'Description': room_description,
                    'Time Taken': end_time - start_time
                }, ignore_index=True)
        print(output_dataframe)  # Print the dataframe in console for now
    return render_template('add-room.html')

def get_room_description(room_name, file_path):
    client = replicate.Client(api_token='APIKEY')  # Add your actual API key here
    result = client.generate(
        input={
            "image": open(file_path, "rb"),
            "prompt": f'This is a {room_name}. Describe it like a realtor would for a listing description.',
            "temperature": 2
        }
    )
    return result  # Make sure this is the actual description from the result

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Main function
if __name__ == "__main__":
    app.run(debug=True)
