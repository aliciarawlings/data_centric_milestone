import pymongo
import os
from flask import Flask, render_template, redirect,request, url_for 
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["MONGO_DBNAME"] = 'before_and_after'

mongo= PyMongo(app)




@app.route('/')
@app.route('/index_page')
def index_page():
    return render_template('index.html')


## Displays all exercises added to the database
@app.route('/get_exercises')
def get_exercises():
    return render_template('exercises.html', exercises=mongo.db.exercises.find())

    
## Form Page to allow users to add an exercise
@app.route('/add_exercise')
def add_exercise():
    return render_template('add_exercise.html', muscle_categories=mongo.db.muscle_categories.find())

    
## this route is used to post the information form the form into the database
@app.route('/insert_exercise', methods=['POST'])
def insert_exercise():
    exercises = mongo.db.exercises
    exercises.insert_one(request.form.to_dict())
    return redirect(url_for('userprofile'))    

##This is fetching the muscle categories from the Mongodb
@app.route('/muscle_categories')
def muscle_categories():
    return render_template('exercises.html', muscle_categories=mongo.db.muscle_categories.find())   
 

##this is called once the edit button is clicked, redirects to edit page
@app.route('/edit_exercise/<exercises_id>')
def edit_exercise(exercises_id):
    the_exercise = mongo.db.exercises.find_one({"_id:ObjectId(exercises_id)"})
    all_muscle_categories= mongo.db.muscle_categories.find()
    return render_template('editexercise.html', exercises=the_exercise, muscle_categories=all_muscle_categories)


##This is the login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('userprofile'))
    return render_template('login.html', error=error)

@app.route('/login_page')
def login_page():
    return render_template('login.html')


##The users Profile they see when they login 
@app.route('/userprofile')
def userprofile():
    return render_template('userprofile.html')    

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)