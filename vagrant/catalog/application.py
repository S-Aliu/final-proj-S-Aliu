import os
from flask import Flask, render_template, redirect, request, url_for, flash, jsonify, send_from_directory, current_app, jsonify
# new imports
from flask import session as login_session
import random, string
from database_setup import College, Region, Base, User
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from oauth2client.client import flow_from_clientsecrets
# use this method if run into error trying to exchance authorization token for access token and need to catch error
from oauth2client.client import FlowExchangeError
# http library in python
import httplib2
import json
# converts the return value from function into reponse object we many send to client
from flask import make_response
import requests

app = Flask(__name__)
# downloaded pictures go to static folder
UPLOAD_FOLDER = os.path.basename('static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CLIENT_ID = json.loads( open('client_secrets.json','r').read())['web']['client_id']

# Create session and connect to DB ##
engine = create_engine('sqlite:///collegeswithusers.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#
# # CHANGES FOR LOGIN
# @app.route('/login')
# def showLogin():
#     # gets random numbers and letters that would need to be guessed to forge request (anti forgery state tokend)
#     state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
#     login_session['state'] = state
#     regions = session.query(Region).all()
#     return render_template('login.html',STATE=state, regions=regions)
#
# @app.route('/github_connect', methods=['GET','POST'])
# def github_connect():
#     if request.args.get('state') != login_session['state']:
#         response = make_response(json.dumps('Invalid state parameter.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     code = request['code']
#     app_id = json.loads(open('github_client_secrets.json', 'r').read())['web']['app_id']
#     app_secret = json.loads(open('github_client_secrets.json', 'r').read())['web']['app_secret']
#     url = 'https://github.com/login/oauth/access_token'
#     payload = {
#         'client_id': app_id,
#         'client_secret': app_secret,
#         'code': request.args.get('code')
#     }
#     headers = {'Accept': 'application/json'}
#     r = requests.post(url, params=payload, headers=headers)
#     response = r.json()
#     # get access_token from response and store it in login_session
#     login_session['access_token'] = token
#     # Use access token to get user from github api
#     # This is done by sending a get request to 'https://api.github.com/user?access_token='
#     url = 'https://api.github.com/user?access_token=%s' % token
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]
#     data = json.loads(result)
#     # finish setting up login_session with info from the users
#     login_session['provider'] = 'github'
#     login_session['username'] = data["name"]
#     login_session['email'] = data["email"]
#     login_session['github_id'] = data["id"]
#     login_session['picture'] = data["avatar_url"]
#     # see if user exists in your database already
#     user_id = getUserID(login_session['email'])
#     if not user_id:
#         user_id = createUser(login_session)
#     login_session['github_id'] = user_id
#     output = ''
#     output += '<h1>Welcome, '
#     output += login_session['username']
#     output += '!</h1>'
#     output += '<img src="'
#     output += login_session['picture']
#     output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
#     flash("You are now logged in as %s" % login_session['username'])
#     return output
#     return redirect(url_for('showRegions'))
#     # welcome user and redirect
#
#
# @app.route('/gconnect', methods=['GET','POST'])
# def gconnect():
#     # Validate state token
#     if request.args.get('state') != login_session['state']:
#         response = make_response(json.dumps('Invalid state parameter.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     # Obtain authorization code
#     code = request.data
#     try:
#         # Upgrade the authorization code into a credentials object
#         # takes flow object and adds client info
#         oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
#         # specify this is one time code server will send
#         oauth_flow.redirect_uri = 'postmessage'
#         # passing one time code as input initiates the exchange
#         credentials = oauth_flow.step2_exchange(code)
#         # if anything goes wrong will send error as json object
#     except FlowExchangeError:
#         response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     # Check that the access token is valid.
#     access_token = credentials.access_token
#     # now that we have a credential object will check if valid access token by appending in order to have Google API verify
#     url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
#     # two lines create get requests with url and access token and store as result
#     h = httplib2.Http()
#     result = json.loads(h.request(url, 'GET')[1])
#     # if the result has any errors then will send 500 error otherwise we have working access token
#     if result.get('error') is not None:
#         response = make_response(json.dumps(result.get('error')), 500)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     gplus_id = credentials.id_token['sub']
#     if result['user_id'] != gplus_id:
#         response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#         # checks if client ID's match
#     if result['issued_to'] != CLIENT_ID:
#         response = make_response(json.dumps("Token's client ID does not match app's."), 401)
#         print "Token's client ID does not match app's."
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     # will check if user already logged in and set 200 succesful authentication without resetting log in variables
#     stored_access_token = login_session.get('access_token')
#     stored_gplus_id = login_session.get('gplus_id')
#     if stored_access_token is not None and gplus_id == stored_gplus_id:
#         response = make_response(json.dumps('Current user is already connected.'), 200)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     # Store the access token in the session for later use.
#     login_session['access_token'] = credentials.access_token
#     login_session['gplus_id'] = gplus_id
#     # Get user info using the google API requesting info within scope and storing it as data
#     userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
#     params = {'access_token': credentials.access_token, 'alt': 'json'}
#     answer = requests.get(userinfo_url, params=params)
#     data = json.loads(answer.text)
#     # stores data in login session
#     login_session['username'] = data["name"]
#     login_session['picture'] = data["picture"]
#     login_session['email'] = data["email"]
#     login_session['provider'] = 'google'
#     user_id = getUserID(login_session['email'])
#     if not user_id:
#         user_id = createUser(login_session)
#     login_session['user_id'] = user_id
#     output = ''
#     output += '<h1>Welcome, '
#     output += login_session['username']
#     output += '!</h1>'
#     output += '<img src="'
#     output += login_session['picture']
#     output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
#     flash("You are now logged in as %s" % login_session['username'])
#     return output
#
# # revoke a current users login and reset their login session
# @app.route('/gdisconnect')
# def gdisconnect():
#     access_token = login_session.get('access_token')
#     # if credentials object is empty then no user to disconnect from and will send error message
#     if access_token is None:
#         response = make_response(json.dumps('Current user not connected.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[0]
#     if result['status'] == '200':
#     # this will tell user if successfully disconnected
#         response = make_response(json.dumps('Successfully disconnected.'), 200)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     else:
#         response = make_response(json.dumps('Failed to revoke token for given user.', 400))
#         response.headers['Content-Type'] = 'application/json'
#         return response
#
# @app.route('/fbconnect', methods = ['POST','GET'])
# def fbconnect():
#     if request.args.get('state') != login_session['state']:
#         response = make_response(json.dumps('Invalid state parameter.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     access_token = request.data
#     print "access token received %s " % access_token
#     # exchange shortlived token for long term tokens
#     app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
#     app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
#     url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]
#     # Use token to get user info from API
#     userinfo_url = "https://graph.facebook.com/v3.2/me"
#     token = result.split(',')[0].split(':')[1].replace('"', '')
#     login_session['provider'] = 'facebook'
#     url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % token
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]
#     data = json.loads(result)
#     login_session['username'] = data["name"]
#     login_session['email'] = data["email"]
#     login_session['facebook_id'] = data["id"]
#     # The token must be stored in the login_session in order to properly logout
#     login_session['access_token'] = token
#     # Get user picture uses a separate call for pictures
#     url = 'https://graph.facebook.com/v3.2/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]
#     data = json.loads(result)
#     login_session['picture'] = data["data"]["url"]
#     # see if user exists
#     user_id = getUserID(login_session['email'])
#     if not user_id:
#         user_id = createUser(login_session)
#     login_session['user_id'] = user_id
#
#     output = ''
#     output += '<h1>Welcome, '
#     output += login_session['username']
#
#     output += '!</h1>'
#     output += '<img src="'
#     output += login_session['picture']
#     output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
#
#     flash("You are now logged in as %s" % login_session['username'])
#     return output
#
# @app.route('/fbdisconnect')
# def fbdisconnect():
#     facebook_id = login_session['facebook_id']
#     # The access token must me included to successfully logout
#     access_token = login_session['access_token']
#     url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
#     h = httplib2.Http()
#     result = h.request(url, 'DELETE')[1]
#     return "You have been logged out"
#
#
# @app.route('/disconnect')
# def disconnect():
#     if 'provider' in login_session:
#         del login_session['username']
#         del login_session['email']
#         del login_session['picture']
#         del login_session['user_id']
#         if login_session['provider'] == 'google':
#             gdisconnect()
#             del login_session['gplus_id']
#             del login_session['access_token']
#         if login_session['provider'] == 'facebook':
#             fbdisconnect()
#             del login_session['provider']
#             del login_session['facebook_id']
#         del login_session['provider']
#         flash("You have successfully been logged out.")
#         return redirect(url_for('showRegions'))
#     else:
#         flash("You were not logged in")
#         return redirect(url_for('showRegions'))
#
# # user functions
# def createUser(login_session):
#     newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
#     session.add(newUser)
#     session.commit()
#     user = session.query(User).filter_by(email=login_session['email']).one()
#     # saves current user and gets user id
#     return user.id
#
# def getUserInfo(user_id):
#     user = session.query(User).filter_by(id=user_id).one()
#     return user
#
# def getUserID(email):
#     try:
#         user = session.query(User).filter_by(email=email).one()
#         return user.id
#     except:
#         return None



# ____________________________________________________________________________________________________________________________________________________________________________________________________________________________________


#show all regions
# @app.route('/')
# @app.route('/region/')
# def showRegions():
#     regions = session.query(Region).all()
#     # if 'username' in login_session:
#         # current_user_picture = login_session['picture']
#         # return render_template('availableregions.html', regions=regions, pic=current_user_picture)
#     # else:
#     return render_template('availableregions.html', regions=regions)

# Making API Endpoint (Get Request)
# @app.route('/region/<region>/JSON/')
# def regionCollegeJson(region):
#     regions = session.query(Region).all()
#     region_info = session.query(Region).filter_by(name=region).one()
#     regioncolleges = session.query(College).filter_by(college_region_id=region_info.id)
#     return jsonify(RegionColleges=[i.serialize for i in regioncolleges])


#show all colleges for region
@app.route('/home')
def showRegionCollegesLocation():
    return render_template('regionalcollegeslocation.html')

@app.route('/<college>/<int:college_id>/')
def eachCollege(college, college_id):
    college = session.query(College).filter_by(college_id=college_id).one()
    regions = session.query(Region).all()
    return render_template('eachcollegepage.html', college=college, regions=regions,)
# # create new college in same region by clicking link on page that shows all colleges for region
# @app.route('/region/<region>/new/', methods=['GET','POST'])
# # region is a string not an object!
# def addNewCollege(region):
#     regions = session.query(Region).all()
#     if 'username' not in login_session:
#         return redirect('/login')
#     else:
#         current_user_picture = login_session['picture']
#     if request.method == 'POST':
#         file = request.files['image']
#         f= os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(f)
#         file_n = file.filename
#         this_region = session.query(Region).filter_by(name=region).one()
#         newCollege = College(name = request.form['college_name'], college_region=this_region, location = request.form['location'], phone_number = request.form['phone_number'], college_type = request.form['college_type'], notes = request.form['client_notes'], user_id=login_session['user_id'], image_filename=file_n)
#         session.add(newCollege)
#         session.commit()
#         flash('Added '+str(newCollege.name)+' ('+str(newCollege.college_region.name+')'))
#         return redirect(url_for('showRegionColleges', region=region, regions=regions))
#     else:
#         return render_template('addregionalcollege.html', region=region, regions=regions, pic=current_user_picture)

# show college by clicking link on page that shows all colleges for region
# @app.route('/region/<region>/<int:college_id>/')
# def showMyCollege(region, college_id):
#     # get region colleges to provide for render template
#     regions = session.query(Region).all()
#     region_info = session.query(Region).filter_by(name=region).one()
#     regioncolleges = session.query(College).filter_by(college_region_id=region_info.id)
#     # get college to view
#     college = session.query(College).filter_by(college_id=college_id).one()
#     # get creator
#     creator = getUserInfo(college.user_id)
#     if 'username' in login_session and login_session['user_id'] != creator.id:
#         current_user_picture = login_session['picture']
#         return render_template('publicmycollege.html', college=college, creator=creator, colleges=regioncolleges, region=region, regions=regions, image=college.image_filename, pic=current_user_picture)
#     else:
#         if 'username' in login_session and login_session['user_id'] == creator.id:
#             current_user_picture = login_session['picture']
#             return render_template('mycollege.html', college=college, creator=creator, colleges=regioncolleges, region=region, regions=regions, image=college.image_filename, pic=current_user_picture)
#         else:
#             return render_template('publicmycollege.html', college=college, creator=creator, colleges=regioncolleges, region=region, regions=regions, image=college.image_filename)
#

# may go to another page to edit any of college info provided
# @app.route('/region/<region>/<int:college_id>/edit/', methods=['GET','POST'])
# def editMyCollege(region, college_id):
#     editedItem = session.query(College).filter_by(college_id=college_id).one()
#     regions = session.query(Region).all()
#     if 'username' not in login_session:
#         return redirect('/login')
#     if request.method == 'POST':
#         # change college_name  phone_number college_type client_notes
#         if request.form['college_name']:
#             editedItem.name = request.form['college_name']
#         # change location
#         if request.form['location']:
#             editedItem.location = request.form['location']
#         # change phone_number
#         if request.form['phone_number']:
#             editedItem.phone_number = request.form['phone_number']
#         # change college_type
#         if request.form['college_type']:
#             editedItem.college_type = request.form['college_type']
#         # change client_notes
#         if request.form['client_notes']:
#             editedItem.notes = request.form['client_notes']
#         session.add(editedItem)
#         session.commit()
#         flash('Edited '+str(editedItem.name)+' ('+str(editedItem.college_region.name+')'))
#         return redirect(url_for('showMyCollege', region=region, regions=regions, college_id=college_id))
#     else:
#         current_user_picture = login_session['picture']
#         return render_template('editregionalcollege.html',region=region, regions=regions, college_id=college_id, item=editedItem, pic=current_user_picture)

# this page allows user to delete colleges
# @app.route('/region/<region>/<int:college_id>/delete/', methods=['GET','POST'])
# def deleteMyCollege(region, college_id):
#     itemToDelete = session.query(College).filter_by(college_id=college_id).one()
#     regions = session.query(Region).all()
#     if 'username' not in login_session:
#         return redirect('/login')
#     if login_session['user_id'] != itemToDelete.user_id:
#         return render_template('publicdeletemycollege.html', region=region, item=itemToDelete, regions=regions)
#     if request.method == 'POST':
#         session.delete(itemToDelete)
#         session.commit()
#         flash('Deleted '+str(itemToDelete.name)+' ('+str(itemToDelete.college_region.name+')'))
#         return redirect(url_for('showRegionColleges', region=region, regions=regions))
#     else:
#         current_user_picture = login_session['picture']
#         # if get request (including going to the website)
#         return render_template('deletemycollege.html', region=region, item=itemToDelete, regions=regions, pic=current_user_picture)
#

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
