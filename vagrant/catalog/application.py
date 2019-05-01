# image project path and where image came from:
# [1] calvin_college.jpg - link: http://www.interkal.com/wp-content/uploads/2015/01/Calvin-College-1.jpg
# [2] Cheetah.jpg - link: https://i.imgur.com/S7k7HXu.jpg
# [3] cooper_union.jpg - link: https://cdn.modlar.com/photos/869/img/s_1920_x/cooper_1_55c4d13349c85.jpg
# [5] highpt_uni.jpg - link: https://www.commonapp.org/files/school/image/header_880333HPUop.jpg
# [6] uni_iowa.jpg - link: https://kubrick.htvapps.com/htv-prod/ibmig/cms/image/kcci/40130486-university-of-iowa-0060-jpg.jpg#
# [7] uni_montana.jpg - link: https://i3.wp.com/www.umt.edu/featured-stories/images/president_bodnar.jpg
# [8] uni_ozarks.jpg - link: https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/University_of_the_Ozarks_campus.jpg/1200px-University_of_the_Ozarks_campus.jpg

# [9] uniofiowa_tour.jpeg - link: https://www.edsmart.org/wp-content/uploads/2018/06/UofIowa.jpg
# [10] usc_college.jpg - link: http://www.uscannenbergmedia.com/resizer/E_WihMTLcUQFCXG1n_NE4PHdfWo=/1200x0
# [11] usc_tour.jpeg - link: https://s.hdnux.com/photos/01/01/13/20/17085481/3/rawImage.jpg
# [12] williams_college.jpg - link: https://www.bestcollegereviews.org/wp-content/uploads/2014/09/williams_college.jpg
# [13] williams_tour.jpeg - link: https://www.google.com/url?sa=i&source=images&cd=&cad=rja&uact=8&ved=2ahUKEwjpq9uyrvnhAhVxFzQIHYgxBXEQjRx6BAgBEAU&url=https%3A%2F%2Fwww.ussportscamps.com%2Ffieldhockey%2Fnike%2Fwilliams-college-nike-field-hockey-camp&psig=AOvVaw0ewArgwWD5DzyvPyd7vWal&ust=1556766796310759

# some imports done without Udacity course on Authetication and Authorization and Full Stack Foundations
# some imports done after referencing dacity course on Authetication and Authorization
import os
from flask import Flask, render_template, redirect, request, url_for, flash, jsonify, send_from_directory, current_app, jsonify
from flask import session as login_session
import random, string
from database_setup import College, Region, Base, User, Tours, Post
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# used Stack Overflow discussion: https://stackoverflow.com/questions/10637352/flask-ioerror-when-saving-uploaded-files/10638095#10638095
UPLOAD_FOLDER = os.path.basename('static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Udacity course on Authetication and Authorization
CLIENT_ID = json.loads( open('client_secrets.json','r').read())['web']['client_id']


# Udacity course on Full Stack Foundations
engine = create_engine('sqlite:///collegeswithusers.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Udacity course on Authetication and Authorization
@app.route('/login')
def showLogin():
    # gets random numbers and letters that would need to be guessed to forge request (anti forgery state tokend)
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    regions = session.query(Region).all()
    return render_template('login.html',STATE=state, regions=regions)


# ----------- independent using Fullstack Stack Foundations Course to develop understandings ----------- #
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
