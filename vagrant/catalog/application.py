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

@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['provider']
            del login_session['facebook_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('Home'))
    else:
        flash("You were not logged in")
        return redirect(url_for('Home'))


@app.route('/login')
def showLogin():
    # gets random numbers and letters that would need to be guessed to forge request (anti forgery state tokend)
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    regions = session.query(Region).all()
    return render_template('login.html',STATE=state, regions=regions)

#show all colleges for region
@app.route('/')
@app.route('/home')
def Home():
    return render_template('home.html')

@app.route('/<college>/<int:college_id>/')
def eachCollege(college, college_id):
    college = session.query(College).filter_by(college_id=college_id).one()
    regions = session.query(Region).all()
    return render_template('eachcollegepage.html', college=college, region=regions,)


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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
