import os
import tensorflow as tf
import numpy as np
#import keras
from tensorflow import keras
from skimage import io
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array, load_img


# Flask utils
from flask import Flask, redirect, url_for, request, render_template,send_from_directory,jsonify,session
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
import pandas as pd
import csv

import firebase_admin
from firebase_admin import auth,credentials, firestore

import folium
from sklearn.cluster import KMeans
import time

# initialize Firebase app
cred = credentials.Certificate('plantcare-f3921-firebase-adminsdk-3lg2k-91d710c1bf.json')
firebase_admin.initialize_app(cred)

# get a reference to your Firestore database
db = firestore.client()
email=""
name=""
location=""


disease_info = pd.read_csv('disease_info.csv' , encoding='cp1252')
supplement_info = pd.read_csv('supplement_info.csv',encoding='cp1252')

model =tf.keras.models.load_model('cnn_model.h5',compile=False)

def prediction(image_path):
    img = image.load_img(image_path, grayscale=False, target_size=(224, 224))
    show_img = image.load_img(image_path, grayscale=False, target_size=(64, 64))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)*1./255
    #x = np.array(x, 'float32')
    #x /= 255
    preds = model.predict(x)
    probabilty = preds.flatten()
    max_prob = probabilty.max()
    index= preds.argmax(axis=-1)[0]
    return index

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'my_super_secret_key_1234'

@app.route('/')

def index():
    return render_template('cover.html')


@app.route('/api/login', methods=['POST'])
def login():
    global email, name, location  # make variables global to access in submit() function
    data = request.json
    token = data['token']

        # add a delay of 1 second to allow for token to become valid
    time.sleep(20)

    decoded_token = auth.verify_id_token(token)
    uid = decoded_token['uid']
    user = auth.get_user(uid)
    
    # get user data from Firestore
    # get document data from Firestore
    doc_ref = db.collection('users').document(uid)
    doc = doc_ref.get()
    if doc.exists:
        email = doc.to_dict()['email']
        name = doc.to_dict()['username']
        location = doc.to_dict()['location']

          
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/diseases')
def diseases():
    with open('user_data.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        rows = []
        for row in csv_reader:
            rows.append({
                'username': row['username'],
                'email':row['email'],
                'location': row['Location'],
                'disease': row['disease']
            })
    return render_template('diseases.html', rows=rows)


def create_map(userdetails_file, location_file):
    # Load userdetails.csv and location.csv into dataframes
    user_df = pd.read_csv(userdetails_file)
    location_df = pd.read_csv(location_file)
    
    # Merge the two dataframes on the 'location' column
    merged_df = pd.merge(user_df, location_df, on='Location', how='left')
    
    # Drop rows with missing latitude or longitude values
    merged_df.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    
    # Use KMeans clustering to create clusters based on latitude and longitude
    X = merged_df[['Latitude', 'Longitude']].values
    kmeans = KMeans(n_clusters=5, random_state=0).fit(X)
    merged_df['cluster'] = kmeans.labels_
    
    # Create a map centered on Kerala and add markers for each cluster
    kerala_coords = [10.8505, 76.2711]
    m = folium.Map(location=kerala_coords, zoom_start=8)
    colors = ['blue', 'green', 'purple', 'orange', 'red']
    
    for index, row in merged_df.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']],
                      popup=row['disease'],
                      icon=folium.Icon(color=colors[row['cluster']])).add_to(m)

     
    # Save the map as an HTML file and return the file path
    file_path = './static/map.html'
    if os.path.exists(file_path):
        os.remove(file_path)
    m.save(file_path)


@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact-us.html')

@app.route('/service')
def service():
    return render_template('Service.html')


@app.route('/index')
def ai_engine_page():
    return render_template('index.html')

@app.route('/mobile-device')
def mobile_device_detected_page():
    return render_template('mobile-device.html')


def check_leaf(image_path):
    # load the model
    binary_model = tf.keras.models.load_model('my_model.h5')


    # load the image and preprocess it
    img = load_img(image_path, target_size=(256, 256))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.

    # make a prediction
    prediction = binary_model.predict(img_array)

    # return the result
    if prediction[0][0] > 0.5:
        print("Leaf")
        return True
    else:
        print("No leaf")
        return False

@app.route('/noleaf/<image_filename>')
def no_leaf(image_filename):
    print(image_filename)
    return render_template('noleaf.html', image_filename=image_filename) 

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        image = request.files['image']
        filename = image.filename
        file_path = os.path.join('static/uploads', filename)
        image.save(file_path)
        print(file_path)
        
        if check_leaf(file_path):
            pred = prediction(file_path)
            title = disease_info['disease_name'][pred]
            description =disease_info['description'][pred]
            prevent = disease_info['Possible Steps'][pred]
            image_url = disease_info['image_url'][pred]
            supplement_name = supplement_info['supplement name'][pred]
            supplement_image_url = supplement_info['supplement image'][pred]
            supplement_buy_link = supplement_info['buy link'][pred]

            # store user data to CSV file
            file_exists = os.path.isfile('user_data.csv')
            with open('user_data.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(['email', 'username', 'location', 'disease'])
                writer.writerow([email, name, location, title])

            return render_template('submit.html', title=title, desc=description, prevent=prevent, 
                                    image_url=image_url, pred=pred, sname=supplement_name, simage=supplement_image_url, buy_link=supplement_buy_link)
        else:
            return redirect(url_for('no_leaf', image_filename=filename))
        
@app.route('/market', methods=['GET', 'POST'])
def market():
    return render_template('market.html', supplement_image = list(supplement_info['supplement image']),
                           supplement_name = list(supplement_info['supplement name']), disease = list(disease_info['disease_name']), buy = list(supplement_info['buy link']))

@app.route('/offhome')
def offhome():
    with open('user_data.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        rows = []
        for row in csv_reader:
            rows.append({
                'username': row['username'],
                'email':row['email'],
                'location': row['Location'],
                'disease': row['disease']
            })
    return render_template('offhome.html', rows=rows)

@app.route('/track')
def track():
    # Call the create_map function to generate the map
    map_html = create_map('user_data.csv', 'locations.csv')
    
           # Render the map_template.html and pass the map HTML as context variable
    return render_template('map_template.html')
    

        
@app.route('/offmarket', methods=['GET', 'POST'])
def offmarket():
    return render_template('offmarket.html', supplement_image = list(supplement_info['supplement image']),
                           supplement_name = list(supplement_info['supplement name']), disease = list(disease_info['disease_name']), buy = list(supplement_info['buy link']))



if __name__ == '__main__':
    app.run(debug=True)
