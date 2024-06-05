
import os
from flask import Flask, redirect, render_template, request, session, url_for
from PIL import Image
import torchvision.transforms.functional as TF
import vit
import numpy as np
import torch
import pandas as pd
from flask_mysqldb import MySQL
import bcrypt
from werkzeug.utils import secure_filename
from flask import Flask, send_from_directory

app = Flask(__name__)


app.secret_key = 'your_secret_key'
mysql = MySQL(app)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskdb'
mysql = MySQL(app)

def is_mysql_connected():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        return True
    except Exception as e:
        print("MySQL connection error:", e)
        return False

app.secret_key = 'your_secret_key'

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


# Route for AI engine page
@app.route('/index')
def ai_engine_page():
    return render_template('index.html')


# Route for mobile device page
@app.route('/mobile-device')
def mobile_device_detected_page():
    return render_template('mobile-device.html')


# Route for home (alias for index)
@app.route('/home')
def home():
    return render_template('index.html')


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
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['logged_in'] = True
            session['username'] = username
           
            return redirect('/')
        else:
            return 'Invalid username or password'
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
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert user data into database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
#  map_location=torch.device('cpu')