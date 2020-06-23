import pymongo
import bcrypt
import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["MONGO_DBNAME"] = 'before_and_after'
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# homepage
@app.route('/')
@app.route('/index_page')
def index_page():
    return render_template('index.html')


# Displays all exercises added to the database
@app.route('/get_exercises')
def get_exercises():
    return render_template('exercises.html', exercises=mongo.db.exercises.find())




# Form Page to allow users to add an exercise
@app.route('/add_exercise')
def add_exercise():
    return render_template('add_exercise.html', muscle_categories=mongo.db.muscle_categories.find())



# this route is used to post the information form the form into the database
@app.route('/insert_exercise', methods=['POST'])
def insert_exercise():
    exercises = mongo.db.exercises
    exercises.insert_one(request.form.to_dict())
    return redirect(url_for('userprofile'))



# This is fetching the muscle categories from the Mongodb
@app.route('/muscle_categories')
def muscle_categories():
    return render_template('exercises.html', muscle_categories=mongo.db.muscle_categories.find())




# this is called once the edit button is clicked, redirects to edit page
@app.route('/edit_exercise/<exercises_id>')
def edit_exercise(exercises_id):
    the_exercise = mongo.db.exercises.find_one({"_id:ObjectId(exercises_id)"})
    all_muscle_categories = mongo.db.muscle_categories.find()
    return render_template('editexercise.html', exercises=the_exercise, muscle_categories=all_muscle_categories)


# login index page
@app.route('/login')
def login_index():
    if 'username' in session:
        return 'you are logged in as' + session['username']

    return render_template('login.html')



# This is the login page route
@app.route('/login', methods=['POST','GET'])
def login():
    users = mongo.db.users
    account_user = users.find_one({'name': request.form['username']})
    
    if account_user:
        print(request.form['password'].encode('utf-8'))
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), account_user['password']) == account_user['password']:
            session['username']= request.form['username']
            return redirect (url_for('login'))

    return 'Invalid username/password combination'   
    




@app.route('/register', methods=['POST','GET'])
def register():
    if request.method =='POST':
        users=mongo.db.users
        present_user = users.find_one({'name': request.form['username']})
        

        if present_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'),bcrypt.gensalt())
            users.insert({'name': request.form['username'],'password': hashpass, 'email':request.form['email']})
            session['username']= request.form['username']
            return redirect('userprofile')
           
            

        return 'That username already exists!' 


    return render_template('register.html')    


# The users Profile they see when they login 
@app.route('/userprofile')
def userprofile():
    return render_template('userprofile.html', userprofile= mongo.db.users.find)    




if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
