
import os
from flask import Flask, redirect, render_template, request, session, url_for
from PIL import Image
import torchvision.transforms.functional as TF
import vit
import numpy as np
import torch
import pandas as pd
# from flask_mysqldb import MySQL
import bcrypt
from werkzeug.utils import secure_filename
from flask import Flask, send_from_directory
import mysql.connector
app = Flask(__name__)


app.secret_key = 'your_secret_key'

# MySQL configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'flaskdb'
}
connection = mysql.connector.connect(**mysql_config)
# Connect to MySQL server
# try:
#     connection = mysql.connector.connect(**mysql_config)
#     print("Connected to MySQL database")
# except mysql.connector.Error as e:
#     print("MySQL connection error:", e)

# app.secret_key = 'your_secret_key'

import os

# Get the current working directory
dir = os.path.dirname(os.path.abspath(__file__))
current_directory = dir

# # Print the current directory
# print("Current directory:", current_directory)


model = vit.vit(39)
# model_loc='D:/trained_model'
model_path=model.load_state_dict(torch.load(current_directory+ "/plant_disease_model_1_latest.pt"))
model.eval()



disease_info = pd.read_csv(current_directory+ '/disease_info.csv', encoding='cp1252')
supplement_info = pd.read_csv(current_directory+'/supplement_info.csv', encoding='cp1252')



# def create_upload_folder():
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)


def prediction(image_path):
    image = Image.open(image_path)
    image = image.resize((224, 224))
    input_data = TF.to_tensor(image)
    input_data = input_data.view((-1, 3, 224, 224))
    output = model(input_data)
    output = output.detach().numpy()
    index = np.argmax(output)
    return index


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/contact')
def contact():
    return render_template('contact-us.html')


# # Route for AI engine page
# @app.route('/index')
# def ai_engine_page():
#     return render_template('index.html')


from flask import redirect, render_template, session, url_for

@app.route('/index')
def ai_engine_page():
    # Check if the user is logged in (session variable is set)
    if 'logged_in' in session and session['logged_in']:
        # User is logged in, render the home page
        return render_template('index.html')
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))




# Route for mobile device page
@app.route('/mobile-device')
def mobile_device_detected_page():
    return render_template('mobile-device.html')


# Route for home (alias for index)
# @app.route('/home')
# def home():
#     return render_template('index.html')

from flask import redirect, render_template, session, url_for

@app.route('/home')
def home():
    # Check if the user is logged in (session variable is set)
    if 'logged_in' in session and session['logged_in']:
        # User is logged in, render the home page
        return render_template('index.html')
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))



# Route for form submission
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        image = request.files['image']
        filename = image.filename
        file_path = os.path.join(current_directory+'/static/uploads', filename)
        image.save(file_path)
        pred = prediction(file_path)
        title = disease_info['disease_name'][pred]
        description = disease_info['description'][pred]
        prevent = disease_info['Possible Steps'][pred]
        image_url = disease_info['image_url'][pred]
        supplement_name = supplement_info['supplement name'][pred]
        supplement_image_url = supplement_info['supplement image'][pred]
        supplement_buy_link = supplement_info['buy link'][pred]
        return render_template('submit.html', title=title, desc=description, prevent=prevent,
                               image_url=image_url, pred=pred, sname=supplement_name,
                               simage=supplement_image_url, buy_link=supplement_buy_link)


# Route for market page
@app.route('/market', methods=['GET', 'POST'])
def market():
    return render_template('market.html', supplement_image=list(supplement_info['supplement image']),
                           supplement_name=list(supplement_info['supplement name']),
                           disease=list(disease_info['disease_name']), buy=list(supplement_info['buy link']))



# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()  # Fetch one row

        # Consume any remaining results
        for _ in cur:
            pass

        cur.close()
        #  bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        if user and password ==user[3]:
            session['logged_in'] = True
            session['username'] = username
            return redirect('/')
        else:
            if user:
                # If a user is found, construct a message including the extracted values
                message = f'Invalid password for user: {username}.'
               
            else:
                # If no user is found, construct a message indicating that the username is invalid
                message = f'No user found with username: {username}.'

            return message

    return render_template('login.html')


# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # create_upload_folder()  # Create the upload folder if it doesn't exist

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
       

      

        # Hash password
        # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert user data into database
        cur = connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password))
        connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
#  map_location=torch.device('cpu')