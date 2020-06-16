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
@app.route('/get_exercises')
def get_exercises():
    return render_template('exercises.html', exercises=mongo.db.exercises.find())

@app.route('/add_exercises')
def add_exercises():
    return render_template('add_exercise.html')


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)