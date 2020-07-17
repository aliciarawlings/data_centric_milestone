import pymongo
import enum 
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import bcrypt
import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.binary import Binary
import base64

if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["MONGO_DBNAME"] = 'before_and_after'
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

class add_exercise_form(Form):
    exercise_type= StringField('exercise_type',[validators.length(min=4, max=25)])


class MuscleCategory(enum.Enum):
    Chest = 1
    Abdominals = 2
    Arms = 3
    Back = 4
    Shoulders = 5
    Legs = 6

# homepage
@app.route('/')
@app.route('/index_page')
def index_page():
    return render_template('index.html')


# Displays all exercises added to the database
# This route allows users to search via muscle category 
@app.route('/get_exercises/<category_id>')
def get_exercises(category_id):
    selected_category_name = MuscleCategory(int(category_id)).name
    all_exercises = list(mongo.db.exercises.find({ "muscle_category": selected_category_name }))
    #for loop iterates through mongo to find relevant image and is then decoded 
    #to be displayed. 
    for exercises in all_exercises:
         exercises["exercise_image"] = exercises["exercise_image"].decode()
    return render_template('exercises.html', exercises=all_exercises)


# combines all documents within the exercise database which have matching muscle_categories.
@app.route('/get_exercises/<muscle_category_id>')
def get_exercise_category(muscle_category_id):
    the_muscle_category = mongo.db.exercises.find_one( {"_id": ObjectId(muscle_category_id)})
    return render_template("exercises.html",exercises=the_muscle_category)
    


# Form Page to allow users to add an exercise
@app.route('/add_exercise')
def add_exercise():
    return render_template('add_exercise.html', muscle_categories=mongo.db.muscle_categories.find())




# this route is used to post the information from the form into the database
@app.route('/insert_exercise', methods=['POST'])
def insert_exercise():
    form=add_exercise_form(request.form)
    if request.method == 'POST' and form.validate():
        exercise =(form.exercise_type.data)
    exercises = mongo.db.exercises
    exercise_request = request.form.to_dict()
    exercise_request['user_id'] = ObjectId(session['user_id'])
    #image has to be encoded using base64 in order to be sent to database,file then needs to be read. 
    encoded_string = base64.b64encode(request.files["exercise_image"].read())
    exercise_request["exercise_image"] = encoded_string
    exercises.insert_one(exercise_request)
   
    return redirect(url_for('userprofile'))




# this is the logout function so users can logout of their account 
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('index_page'))



# This is fetching the muscle categories from the Mongodb
@app.route('/muscle_categories')
def muscle_categories():
    return render_template('exercises.html', muscle_categories=mongo.db.muscle_categories.find())



# this is called once the edit button is clicked, redirects to edit page.
@app.route('/edit_exercise/<user_exercise_id>')
def edit_exercise(user_exercise_id):
    the_exercise = mongo.db.exercises.find_one({"_id": ObjectId(user_exercise_id)})
    
    all_categories= mongo.db.muscle_categories.find()
    return render_template('editexercise.html', exercises=the_exercise, muscle_categories=all_categories,user_exercise_id=user_exercise_id)


# update the task function
@app.route('/update_exercise/<exercises_id>', methods=["POST"])
def update_exercise(exercises_id):
    exercises = mongo.db.exercises
    # this is the update object which contains all the fields within the edit form which I would like to update.
    update_exercise_data = {
        'user_id': ObjectId(session['user_id']),
        'muscle_category': request.form.get('muscle_category'),
        'exercise_type': request.form.get('exercise_type'),
        'amount_of_reps': request.form.get('amount_of_reps'),
        'amount_of_sets': request.form.get('amount_of_sets'),
        'exercise_duration': request.form.get('exercise_duration'),
        'workout_description': request.form.get('workout_description'),
    }
    #if statement to see whether or not the user has selected a new image, if yes then we update the "update_exercise_data" object and encode it. 
    if request.files["exercise_image"]:
        update_exercise_data['exercise_image'] =base64.b64encode(request.files["exercise_image"].read())
                                                    #using $set allows me to select which fields I want updated.
    exercises.update({'_id': ObjectId(exercises_id )}, { "$set": update_exercise_data })
    
    return redirect(url_for('userprofile'))





# delete exercise function
@app.route('/delete_exercise/<user_exercise_id>')
def delete_exercise(user_exercise_id):
    mongo.db.exercises.remove({'_id': ObjectId(user_exercise_id)})
    return redirect(url_for('userprofile',user_exercise_id=user_exercise_id))



# login index page
@app.route('/login')
def login_index():
    if 'username' in session:
        return redirect('userprofile')

    return render_template('login.html')





# This is the login functionality route
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    #looks for user with corresponding username in mongodb
    account_user = users.find_one({'name': request.form['username']})
    print (account_user)
    #if username is correct, password is checked against the account user name.
    #password is hashed 
    if account_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), account_user
        ['password']) == account_user['password']:
        #user login is stored in session cookie 
        #The users id is placed here in order to attach their _id to any submissions
        #they make to the database 
            session['username'] = account_user['name']
            session['user_id'] = str(account_user['_id'])

            return redirect('userprofile')

    return 'Invalid username/password combination'   
    





# This is the register form which posts all the users data to the database. Password
@app.route('/register', methods=['POST','GET'])
def register():
    if request.method =='POST':
        users=mongo.db.users
        # checking to see if name is already registered in the database
        present_user = users.find_one({'name': request.form['username']})
      #username is stored in session cookie as to eliminate the need to fetch the user information from the database at all times.Password is always hashed with gensalt. 
        if present_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'),bcrypt.gensalt())
            #here the users info is submitted from the request form.
            user_id = users.insert_one({'name': request.form['username'],'password': hashpass, 'email':request.form['email']})
            session['username'] = request.form['username']
            #inserts the users id to each submission from their account
            session['user_id'] = str(user_id.inserted_id)
            

            return redirect('userprofile')

        return 'That username already exists!'

    return render_template('register.html')    






# The users Profile they see when they login 
@app.route('/userprofile')
def userprofile():     
    #retrieves exercises from the database that users created and displays on userprofile and search exercises page
    #cursor converted to a list so image in database can be decoded from binary and displayed.
    #for loop iterates through exercise_images
    user_exercises = list(mongo.db.exercises.find({ 'user_id': ObjectId(session['user_id']) }))
    user_info = mongo.db.users.find({'_id':ObjectId(session['user_id'])}, {'name':1, 'email':1})
    for user_exercise in user_exercises:
        user_exercise["exercise_image"]= user_exercise["exercise_image"].decode()
    return render_template('userprofile.html', user_exercises= user_exercises,user_info=user_info)    




if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)