import os
from flask import Flask, render_template, redirect, request, url_for, flash, jsonify, send_from_directory, current_app, jsonify
# new imports
from flask import session as login_session
import random, string
from database_setup import College, Region, Base, User, Tours, Post
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
    session = DBSession()
    return render_template('regionalcollegeslocation.html')

@app.route('/college/<int:college_id>/')
def eachCollege(college_id):
    session = DBSession()
    colleges = session.query(College).filter_by(college_id=college_id).one()
    return render_template('eachcollegepage.html', college_id=college_id, colleges=colleges)

@app.route('/colleges')
def allColleges():
    session = DBSession()
    colleges = session.query(College).all()
    return render_template('allcollegepage.html',colleges=colleges)

@app.route('/Forum', methods=['GET', 'POST'])
def Forum():
    session = DBSession()
    AllPosts = session.query(Post).all()
    return render_template('allposts.html', AllPosts=AllPosts)

@app.route('/posts', methods=['GET', 'POST'])
def NewPost():
    session = DBSession()
    AllPosts = session.query(Post).all()
    if request.method == 'POST':
        NewPost = Post(author = request.form['author'], college = request.form['college'], date = request.form['date'], notes = request.form['notes'])
        session.add(NewPost)
        flash('New Post %s Successfully Published' %NewPost.date)
        session.commit()
        return redirect(url_for('Forum'))
    else:
        return render_template('new_post.html', AllPosts=AllPosts)

@app.route('/posts/edit/<int:id>/', methods=['GET', 'POST'])
def editPost():
    session = DBSession()
    AllPosts = session.query(Post).all()
    posts = session.query(Post).filter_by(id=id).first()
    editPost = session.query(Post).filter_by(id=id).one()
    if request.method == 'POST':
        if request.form['author']:
            editPost.author = request.form['author']
        if request.form['college']:
            editPost.college = request.form['college']
        if request.form['date']:
            editPost.date = request.form['date']
        if request.form['notes']:
            editPost.notes = request.form['notes']
        session.add(editedPost)
        session.commit()
        return redirect(url_for('Forum'))
    else:
        return render_template('edit_post.html', AllPosts=AllPosts, posts=posts)

@app.route('/tours')
def allTours():
    session = DBSession()
    tours = session.query(Tours).all()
    return render_template('alltours.html', tours=tours)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
