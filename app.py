import os 
import requests

from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from secrets import API_SECRET_KEY

from forms import UserAddForm, LoginForm, SearchPlantForm
from models import db, connect_db, User, Garden, Garden_Plant, Plant

CURR_USER_KEY = "curr_user"
API_BASE_URL = "http://trefle.io/api/v1"

app = Flask(__name__)
app.app_context().push()

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///romainecalm'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def seed_gardens(user_id):
    garden_names = ["My Garden", "My Future Garden"]
    date_of_creation = datetime.utcnow()

    for garden_name in garden_names:
        garden = Garden(
            garden_name=garden_name,
            user_id=user_id,
            date_of_creation=date_of_creation
        )
        db.session.add(garden)
    
    db.session.commit()



@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If there's already is a user with that username: flash message
    and re-present form.

    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]   

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)
        # After successfully creating a new user
        
        seed_gardens(user.id)
        do_login(user)
        
        return redirect("/search")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/search")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("You have successfully logged out.", "success")
    return redirect("login.html")


##############################################################################
#Plant routes 

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Show search form and display search results"""
    if request.method == 'POST':
        search_query = request.form.get("search_query")
        res = requests.get(f"{API_BASE_URL}/plants/search",
                           params={'token':API_SECRET_KEY, 'q': search_query})
        plantdata = res.json()
        plants=plantdata["data"]

        return render_template('search_form.html', plants=plants)
    
    return render_template('search_form.html')    


@app.route("/plants/<int:plant_id>", methods=['GET'])
def plant_info(plant_id):
    """fetches specific information about a plant from the Trefle API"""
    res = requests.get(f"{API_BASE_URL}/species/{plant_id}",
                           params={'token':API_SECRET_KEY})
    if res.status_code == 200:
        plant_info = res.json()
        plant=plant_info["data"]
        return render_template('plant_info.html',plant=plant)
    else:
        return "Failed to find plant information"
    
@app.route('/save', methods=['POST'])
def save_plant():
    """save the selected plant into the plant table and redirect to gardens"""
    name = request.form.get('name')
    api_id = request.form.get('api_id')

    # Check if the plant with the same api_id already exists in the table
    existing_plant = Plant.query.filter_by(api_id=api_id).first()
    if existing_plant:
        flash(f"This plant already exist in the database", "danger")
        return redirect(url_for('/search'))

    new_plant = Plant(plant_name_api=name, api_id=api_id)

    db.session.add(new_plant)
    db.session.commit()

    return redirect(url_for('select_garden',plant_id=new_plant.id))

######################################################################
#Garden routes

@app.route('/select-garden/<int:plant_id>', methods=['GET', 'POST'])
def select_garden(plant_id=None):
    """Select a garden where to save the plant"""   
    plant = Plant.query.get(plant_id)
        
    if request.method== 'POST':
        garden_type = request.form.get('garden_type')
        print("****************selecting a garden", garden_type)
        garden = get_garden(garden_type)
        
        if plant and garden:
            #create relationship between plant and garden
            garden.plants.append(plant)
            db.session.commit()
           
        flash(f"Plant saved to { garden_type}!", "success")
        return render_template('select_garden.html', plant_id=plant_id, plant=plant)
#Handle GET request
    return render_template('select_garden.html', plant_id=plant_id, plant=plant)

def get_garden(garden_type):
    """Get an existing garden by type """
    user_id=g.user.id
    
    if garden_type== 'New Garden':
            print('Inside the get_or_create_garden')
            existing_garden = Garden.query.filter_by(garden_name=garden_type, user_id=user_id).first()
            if existing_garden:
                return existing_garden
            else:           
                return create_new_garden(garden_type, user_id)                      
    else:
        return Garden.query.filter_by(garden_name=garden_type, user_id=g.user.id).first()
    

@app.route('/create-garden', methods=['GET', 'POST'])
def create_garden():
    if request.method == 'POST':  
        garden_name = request.form.get('garden_name')
        plant_id = request.args.get('plant_id')  # Retrieve plant_id from query string
    
        print("############Form Data:", request.form)
        print("############Query String - plant_id:", plant_id)
    
        if not plant_id:
            flash("Plant_id required", "danger")
            return redirect(url_for('create_garden'))
        
        user_id = g.user.id
        
        if plant_id:
            try:
                plant_id = int(plant_id)
            except ValueError:
                flash("Invalid plant_id", "danger")
                return redirect(url_for('create_garden'))
        
        garden = create_new_garden(garden_name, user_id)

        if garden:
            return redirect(url_for('select_garden', plant_id=plant_id))
            
    return render_template('create_garden.html')

def create_new_garden(garden_name, user_id):
    """Create a new garden or update and existing garden and return it"""
    existing_garden = Garden.query.filter_by(garden_name = garden_name, user_id=user_id).first()

    if existing_garden:
        #the garden already exist so update it's details
        existing_garden.date_of_creation = datetime.utcnow()
        db.session.commit()
        return existing_garden
    
    else:
        garden = Garden(garden_name=garden_name, user_id=user_id, date_of_creation=datetime.utcnow())
        db.session.add(garden)
        db.session.commit()
        return garden
   
@app.route('/gardens/<int:user_id>', methods=['GET'])
def list_gardens(user_id):
    """List all the users gardens and associated plants for a user """
    user =User.query.get(user_id)
    if user:
        gardens = user.gardens
        plants = Plant.query.all()
        return render_template('garden_list.html', user=user, gardens=gardens, plants=plants) 
    else:
        flash("User not found", "danger")
        return redirect(url_for('homepage'))

   
#################################################

@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        return render_template('home.html')

    else:
        return render_template('home-anon.html')

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND  page"""

    return render_template('404.html'), 404

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
