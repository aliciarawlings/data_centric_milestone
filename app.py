import pymongo
import os
from flask import Flask, render_template, redirect,request, url_for 
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


MONGODB_URI = os.getenv("MONGO_URI")
DBS_NAME = "Before&After"
COLLECTION_NAME = "exercises"


## Starting connection with MONGODB
def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        print("Mongo is connected!")
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s") % e
        
conn = mongo_connect(MONGODB_URI)

coll = conn[DBS_NAME][COLLECTION_NAME]

@app.route('/')
@app.route('/get_exercises')
def get_exercises():
    return render_template('exercises.html', recipes=mongo.db.exercises.find())


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)