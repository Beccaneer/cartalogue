from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Artist, Artwork, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from forms import ArtistForm, ArtworkForm
import random
import string
import httplib2
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///art.db'
db = SQLAlchemy(app)


# Create token for user logging on


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Function for logging in user through Google


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print("in gconnect function")
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'
        ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['email']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; '
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['email'])
    return output

# Store te user in the database


def createUser(login_session):
    newUser = User(email=login_session[
                   'email'], picture=login_session['picture'])
    db.session.add(newUser)
    db.session.commit()
    user = db.session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# Retrieve user from database


def getUserInfo(user_id):
    user = db.session.query(User).filter_by(id=user_id).one()
    return user

# Get the user email, if it exists


def getUserID(email):
    try:
        user = db.session.query(User).filter_by(email=email).one()
        return user.id
    except AttributeError:
        return None


# Revoke a current user's token and reset their login_session


@app.route('/logout')
def disconnect():
    access_token = login_session['access_token']
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['user_id']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON endpoints

# View an artist


@app.route('/artist/<int:artist_id>/JSON')
def artist(artist_id):
    artist = db.session.query(Artist).filter_by(id=artist_id).one()
    return jsonify(Artist=[a.serialize for a in artist])

# View the artwork belonging to a particular artist


@app.route('/artist/<int:artist_id>/artwork/JSON')
def artworkJSON(artist_id):
    artwork = db.session.query(Artwork).filter_by(
        artist_id=artist_id).all()
    return jsonify(Artwork=[a.serialize for a in artwork])

# View a particular artwork


@app.route('/artist/<int:artist_id>/artwork/<int:artwork_id>/JSON')
def artPieceJSON(artist_id, artwork_id):
    art_piece = db.session.query(Artwork).filter_by(id=artwork_id).one()
    return jsonify(ArtPiece=art_piece.serialize)

# View all artists


@app.route('/artist/JSON')
def artistsJSON():
    artists = db.session.query(Artist).all()
    return jsonify(Artists=[a.serialize for a in artists])

# View all artwork


@app.route('/artwork/JSON')
def allArtworkJSON():
    artwork = db.session.query(Artwork).all()
    return jsonify(Artwork=[a.serialize for a in artwork])


# Show all artists
@app.route('/')
@app.route('/artist/')
@app.route('/artists/')
def showArtists():
    artists = db.session.query(Artist).all()
    # Check if user owns artist,
    # this info is used to decide if edit/delete buttons should be shown
    if 'user_id' not in login_session:
        user_id = None
    else:
        user_id = login_session['user_id']
    return render_template('artists.html', artists=artists, user_id=user_id)


# Create a new artist
@app.route('/artist/new/', methods=['GET', 'POST'])
def newArtist():
    # Only logged in users can create an artist
    if 'email' not in login_session:
        return redirect('/login')
    # Using the form located in forms.py
    form = ArtistForm(request.form)
    if request.method == 'POST' and form.validate():
        newArtist = Artist(
            name=form.name.data,
            year_of_birth=form.year_of_birth.data,
            year_of_death=form.year_of_death.data,
            country=form.country.data,
            art_movement=form.art_movement.data,
            user_id=login_session['user_id']
        )
        db.session.add(newArtist)
        db.session.commit()
        return redirect(url_for('showArtists'))
    else:
        return render_template('newartist.html', form=form)


# Edit an artist
@app.route('/artist/<int:artist_id>/edit/', methods=['GET', 'POST'])
def editArtist(artist_id):
    # Checking if user is logged in
    if 'email' not in login_session:
        return redirect('/login')
    editedArtist = db.session.query(
        Artist).filter_by(id=artist_id).one()
    # Checking if artist belongs to logged in user
    if editedArtist.user_id != login_session['user_id']:
        return """<script>function myFunction()
        {alert('You are not authorized to edit this artist.
         Please create your own artist in order to edit.');}
        </script><body onload='myFunction()'>"""
    # Using the same form as artist creation for artist editing
    form = ArtistForm(request.form, editedArtist)
    if request.method == 'POST' and form.validate():
        editedArtist.name = form.name.data
        editedArtist.year_of_birth = form.year_of_birth.data
        editedArtist.year_of_death = form.year_of_death.data
        editedArtist.country = form.country.data
        editedArtist.movement = form.art_movement.data
        db.session.add(editedArtist)
        db.session.commit()
        return redirect(url_for('showArtists'))
    else:
        return render_template(
            'editArtist.html', form=form, artist=editedArtist)


# Delete an artist
@app.route('/artist/<int:artist_id>/delete/', methods=['GET', 'POST'])
def deleteArtist(artist_id):
    # Checking if user is logged in
    if 'email' not in login_session:
        return redirect('/login')
    artistToDelete = db.session.query(
        Artist).filter_by(id=artist_id).one()
    # Ensuring artist belongs to currently logged in user
    if artistToDelete.user_id != login_session['user_id']:
        return """<script>function myFunction()
        {alert('You are not authorized to edit this artist.
         Please create your own artist in order to edit.');}
        </script><body onload='myFunction()'>"""
    if request.method == 'POST':
        db.session.delete(artistToDelete)
        # Also deletes the artwork belonging to the artist
        # Bad things can happen without this step
        db.session.query(Artwork).filter_by(
            artist_id=artistToDelete.id).delete()
        db.session.commit()
        return redirect(url_for('showArtists'))
    else:
        return render_template('deleteartist.html', artist=artistToDelete)


# Show the artwork belonging to an artist
@app.route('/artist/<int:artist_id>/artwork/')
def showArtwork(artist_id):
    artist = db.session.query(Artist).filter_by(id=artist_id).one()
    artwork = db.session.query(Artwork).filter_by(
        artist_id=artist_id).all()
    # Checking if user owns the artwork (and associated artist)
    # Used to decide if edit/delete icons should be displayed
    if 'user_id' not in login_session:
        user_id = None
    else:
        if login_session['user_id'] == artist.user_id:
            user_id = login_session['user_id']
        else:
            user_id = None
    return render_template(
        'artwork.html',
        artwork=artwork,
        artist=artist,
        user_id=user_id
    )


# Show all artwork
@app.route('/artwork')
def showAllArtwork():
    artwork = db.session.query(Artwork).all()
    # If user owns the artwork, show edit/delete buttons
    if 'user_id' not in login_session:
        user_id = None
    else:
        user_id = login_session['user_id']
    return render_template('artwork.html', artwork=artwork, user_id=user_id)


# Create a new artwork


@app.route(
    '/artist/<int:artist_id>/artwork/new/', methods=['GET', 'POST'])
def newArtPiece(artist_id):
    # Checking if user is logged in
    if 'email' not in login_session:
        return redirect('/login')
    artist = db.session.query(Artist).filter_by(id=artist_id).one()
    user_id = login_session['user_id']
    # Ensuring user owns the artist
    if user_id != artist.user_id:
        return """""<script>function myFunction()
        {alert('You are not authorized to add artwork for this artist.
         Please create your own artist in order to add artwork.');}
        </script><body onload='myFunction()'>"""
    # Using form in forms.py
    form = ArtworkForm(request.form)
    if request.method == 'POST' and form.validate():
        newPiece = Artwork(
            title=form.title.data,
            medium=form.medium.data,
            size=form.size.data,
            year_created=form.year_created.data,
            artist_id=artist_id,
            user_id=user_id
        )
        db.session.add(newPiece)
        db.session.commit()

        return redirect(url_for('showArtwork', artist_id=artist_id))
    else:
        return render_template('newartwork.html', form=form, artist=artist)


# Edit an art piece


@app.route('/artist/<int:artist_id>/artwork/<int:artwork_id>/edit',
           methods=['GET', 'POST'])
def editArtPiece(artist_id, artwork_id):
    # Checking if user is logged in
    if 'email' not in login_session:
        return redirect('/login')
    editedArtPiece = db.session.query(Artwork).filter_by(id=artwork_id).one()
    # Ensuring user owns the artist/artwork
    if editedArtPiece.user_id != login_session['user_id']:
        return """<script>function myFunction()
        {alert('You are not authorized to edit this art piece.');}
        </script><body onload='myFunction()'>"""
    # Using the same form as artwork creation
    form = ArtworkForm(request.form, editedArtPiece)
    if request.method == 'POST' and form.validate():
        editedArtPiece.title = form.title.data
        editedArtPiece.medium = form.medium.data
        editedArtPiece.size = form.size.data
        editedArtPiece.year_created = form.year_created.data
        editedArtPiece.artist_id = artist_id
        editedArtPiece.user_id = login_session['user_id']
        db.session.add(editedArtPiece)
        db.session.commit()
        return redirect(url_for('showArtwork', artist_id=artist_id))
    else:
        return render_template(
            'editartwork.html',
            form=form,
            editedArtPiece=editedArtPiece
        )


# Delete an art piece
@app.route('/artist/<int:artist_id>/artwork/<int:artwork_id>/delete',
           methods=['GET', 'POST'])
def deleteArtPiece(artist_id, artwork_id):
    # Checking if user is logged in
    if 'email' not in login_session:
        return redirect('/login')
    pieceToDelete = db.session.query(Artwork).filter_by(id=artwork_id).one()
    # Ensuring user owns the artwork
    if pieceToDelete.user_id != login_session['user_id']:
        return """<script>function myFunction()
        {alert('You are not authorized to delete this artwork.');}
        </script><body onload='myFunction()'>"""
    if request.method == 'POST':
        db.session.delete(pieceToDelete)
        db.session.commit()
        return redirect(url_for('showArtwork', artist_id=artist_id))
    else:
        return render_template('deleteArtwork.html', artwork=pieceToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
