"""serves Flask web application on specified port"""
import os
import random
import string
import json
from signal import signal, SIGPIPE, SIG_DFL
from flask import Flask, render_template, redirect, request, url_for, flash
from flask import make_response, current_app
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
from database_setup import College, Region, Base, User, Tours, Post, City
signal(SIGPIPE, SIG_DFL)

APP = Flask(__name__)

# used Stack Overflow discussion: https://stackoverflow.com/questions/10637352/flask-io
# error-when-saving-uploaded-files/10638095#10638095
UPLOAD_FOLDER = os.path.basename('static')
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Udacity course on Authetication and Authorization
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']


# Udacity course on Full Stack Foundations
ENGINE = create_engine('sqlite:///collegeswithusers.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = ENGINE
DBSESSION = sessionmaker(bind=ENGINE)
SESSION = DBSESSION()



# Udacity course on Authetication and Authorization
@APP.route('/login')
def showlogin():
    """make state token"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    regions = SESSION.query(Region).all()
    return render_template('login.html', STATE=state, regions=regions)

@APP.context_processor
def inject_user_img():
    """supply user image to all templates"""
    if 'username' in login_session:
        return dict(user_img=login_session['picture'])
    return dict(user_img='none')

@APP.route('/gconnect', methods=['GET', 'POST'])
def gconnect():
    """sign in using google provider"""
    print login_session['state']
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        # takes flow object and adds client info
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        # specify this is one time code server will send
        oauth_flow.redirect_uri = 'postmessage'
        # passing one time code as input initiates the exchange
        credentials = oauth_flow.step2_exchange(code)
        # if anything goes wrong will send error as json object
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    # now that we have a credential object will check if valid access
    # token by appending in order to have Google API verify
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    # two lines create get requests with url and access token and store as result
    variable_h = httplib2.Http()
    result = json.loads(variable_h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # checks if client ID's match
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # will check if user already logged in and set 200 succ
    # esful authentication without resetting log in variables
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info using the google API requesting info within scope and storing it as data
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    # stores data in login session
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]
    login_session['provider'] = 'google'
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '"style="width:300px;height:300px;-webkit-border-radius:150px;">'
    flash("You are now logged in as %s" % login_session['username'])
    return output


# user functions
def create_user(sess_obj):
    """add login session information to database"""
    new_user = User(name=sess_obj['username'], email=sess_obj['email'],
                    picture=sess_obj['picture'])
    SESSION.add(new_user)
    SESSION.commit()
    user = SESSION.query(User).filter_by(email=sess_obj['email']).one()
    # saves current user and gets user id
    return user.id

def get_user_id(email):
    """get user's id given email"""
    try:
        user = SESSION.query(User).filter_by(email=email).one()
        return user.id
    except StandardError:
        return None
# revoke a current users login and reset their login session
@APP.route('/gdisconnect')
def gdisconnect():
    """disconnect user with google provider"""
    access_token = login_session.get('access_token')
    # if credentials object is empty then no user to disconnect from and will send error message
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    var_h = httplib2.Http()
    result = var_h.request(url, 'GET')[0]
    if result['status'] == '200':
    # this will tell user if successfully disconnected
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    response.headers['Content-Type'] = 'application/json'
    return response

@APP.route('/disconnect')
def disconnect():
    """reset and clear login session"""
    if 'provider' in login_session:
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('home'))
    else:
        flash("You were not logged in")
        return redirect(url_for('home'))

@APP.route('/')
@APP.route('/home')
def home():
    """render home page"""
    return render_template('regionalcollegeslocation.html')

# coded with the OpenWeatherMap api and aid from https://www.youtube.com/watch?v=lWA0GgUN8kg
@APP.route('/weather')
def weather_call():
    """make calls to weather API"""
    cities = SESSION.query(City).all()
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=\
    imperial&appid=bfb6673821c8d44c9ba923d72274ef24'
    weather_data = []
    for city in cities:
        r_variable = requests.get(url.format(city.name)).json()
        weather = {
            'city': city,
            'temperature': r_variable['main']['temp'],
            'description': r_variable['weather'][0]['description'],
            'icon': r_variable['weather'][0]['icon']
        }
        weather_data.append(weather)
    return render_template('weather.html', weather_data=weather_data)


@APP.route('/cities', methods=['GET', 'POST'])
def new_city():
    """Call city API to find weather for a new city"""
    if request.method == 'POST':
        url = 'http://api.openweathermap.org/data/2.5/weather?q\
        ={}&units=imperial&appid=bfb6673821c8d44c9ba923d72274ef24'
        r_variable = requests.get(url.format(request.form['name'])).json()
        if r_variable['cod'] == 200:
            new_city_variable = City(name=request.form['name'])
            SESSION.add(new_city_variable)
            SESSION.commit()
            return redirect(url_for('weather_call'))
        # Need to handle invalid city input
        flash('New City %s is invalid' % request.form['name'])
        return render_template('new_city.html')
    return render_template('new_city.html')

@APP.route('/college/<int:college_id>/<int:college_city_id>/')
def each_college(college_id, college_city_id):
    """query a college and its information"""
    colleges = SESSION.query(College).filter_by(college_id=college_id).first()
    city_college = SESSION.query(College).filter_by(
        college_city_id=college_city_id).first()
    city = city_college.college_city.name
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=\
    imperial&appid=bfb6673821c8d44c9ba923d72274ef24'
    r_variable = requests.get(url.format(city)).json()
    weather = {'city': city,
               'temperature': r_variable['main']['temp'],
               'description': r_variable['weather'][0]['description'],
               'icon': r_variable['weather'][0]['icon']
              }
    print weather
    return render_template('eachcollegepage.html', college_id=college_id, city=city,
                           colleges=colleges, weather=weather)


@APP.route('/colleges')
def all_colleges():
    """query all colleges"""
    colleges = SESSION.query(College).all()
    return render_template('allcollegepage.html', colleges=colleges)

@APP.route('/college/<int:college_id>/delete', methods=['GET', 'POST'])
def delete_college(college_id):
    """"delete a college"""
    if "username" not in login_session:
        return redirect('/login')
    college = SESSION.query(College).filter_by(college_id=college_id).first()
    deleted_college = SESSION.query(College).filter_by(college_id=college_id).first()
    if request.method == 'POST':
        SESSION.delete(deleted_college)
        SESSION.commit()
        flash('Deleted '+str(deleted_college.name))
        return redirect(url_for('all_colleges'))
    return render_template('deletecollege.html', college_id=college_id, college=college)

@APP.route('/college/new', methods=['GET', 'POST'])
def new_college():
    """make a new college using form data"""
    if "username" not in login_session:
        return redirect('/login')
    colleges = SESSION.query(College).all()
    cities = SESSION.query(City).all()
    regions = SESSION.query(Region).all()
    all_tours_objects = SESSION.query(Tours).all()
    if request.method == 'POST':
        file_download = request.files['image_filename']
        college_r = SESSION.query(Region).filter_by(name=request.form['college_region']).first()
        college_c = SESSION.query(City).filter_by(name=request.form['college_city']).first()
        print request.form['college_city']
        college_t = SESSION.query(Tours).filter_by(type=request.form['tours']).first()
        var_f = os.path.join(current_app.root_path, APP.config['UPLOAD_FOLDER'],
                             file_download.filename)
        file_download.save(var_f)
        file_n = file_download.filename
        new_college_object = College(name=request.form['name'],
                                     college_city=college_c,
                                     tours=college_t,
                                     image_filename=file_n,
                                     college_region=college_r,
                                     location=request.form['location'],
                                     phone_number=request.form['phone_number'],
                                     college_type=request.form['college_type'],
                                     notes=request.form['notes'],
                                     college_city_id=college_c.id,
                                     user_id=1)
        SESSION.add(new_college_object)
        flash('New College %s Successfully Created' % new_college_object.name)
        SESSION.commit()
        return redirect(url_for('all_colleges'))

    return render_template('new_college.html', colleges=colleges, cities=cities, regions=regions,
                           all_tours=all_tours_objects)


@APP.route('/Forum', methods=['GET', 'POST'])
def forum():
    """provide all posts to html template"""
    all_posts = SESSION.query(Post).all()
    if 'username' not in login_session:
        return render_template('publicallposts.html', all_posts=all_posts)
    return render_template('allposts.html', all_posts=all_posts)


@APP.route('/posts', methods=['GET', 'POST'])
def new_post():
    """make new post with form data"""
    all_posts = SESSION.query(Post).all()
    if request.method == 'POST':
        new_post_variable = Post(author=request.form['author'], college=request.form['college'],
                                 date=request.form['date'], notes=request.form['notes'],
                                 user_id=login_session['user_id'])
        SESSION.add(new_post_variable)
        flash('New Post by %s Successfully Published!' % new_post_variable.author)
        SESSION.commit()
        return redirect(url_for('forum'))

    return render_template('new_post.html', all_posts=all_posts)


@APP.route('/posts/edit/<int:var_id>/', methods=['GET', 'POST'])
def edit_post(var_id):
    """allow user to edit post"""
    edit_post_item = SESSION.query(Post).filter_by(id=var_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != edit_post_item.user_id:
        flash('You may only edit your own post.')
        return redirect(url_for('forum'))
    if request.method == 'POST':
        if request.form['author']:
            edit_post_item.author = request.form['author']
        if request.form['college']:
            edit_post_item.college = request.form['college']
        if request.form['date']:
            edit_post_item.date = request.form['date']
        if request.form['notes']:
            edit_post_item.notes = request.form['notes']
        SESSION.add(edit_post_item)
        SESSION.commit()
        return redirect(url_for('forum'))
    else:
        return render_template('editpost.html', post=edit_post_item)


@APP.route('/delete/<int:variable_id>', methods=['GET', 'POST'])
def delete_post(variable_id):
    """delete a post in the database"""
    item_to_delete = SESSION.query(Post).filter_by(id=variable_id).one()
    all_posts = SESSION.query(Post).all()
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != item_to_delete.user_id:
        flash('You may only delete your own post.')
        return render_template('allposts.html', all_posts=all_posts)
    if request.method == 'POST':
        SESSION.delete(item_to_delete)
        SESSION.commit()
        flash('Deleted '+str(item_to_delete.author)+"'s post made on "+ str(item_to_delete.date))
        return redirect(url_for('forum'))
    return render_template('deletepost.html', post_delete=item_to_delete)



@APP.route('/tours')
def all_tours():
    """provide all tours to html template"""
    tours = SESSION.query(Tours).all()
    return render_template('alltours.html', tours=tours)

@APP.route('/tours/<int:v_id>/edit', methods=['GET', 'POST'])
def edit_tour(v_id):
    """allow user to edit tours"""
    tour = SESSION.query(Tours).filter_by(id=v_id).first()
    edited_tour = SESSION.query(Tours).filter_by(id=v_id).first()
    if "username" not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['notes']:
            edited_tour.notes = request.form['notes']
        if request.form['popularity']:
            edited_tour.popularity = request.form['popularity']
        if request.form['virtual_tour']:
            edited_tour.virtual_tour = request.form['virtual_tour']
        SESSION.add(edited_tour)
        SESSION.commit()
        flash('Edited '+str(edited_tour.type)+ ' tour')
        return redirect(url_for('all_tours'))
    else:
        return render_template('edit_tour.html', id=id, edited_tour=edited_tour, tour=tour)





# Udacity course on Full Stack Foundations
if __name__ == '__main__':
    APP.secret_key = 'super_secret_key'
    APP.debug = True
    APP.run(host='0.0.0.0', port=5000)
