# cARTalogue

cARTalogue is a Flask app designed to store artists and associated artwork through a sqlite database.
Artists own artwork, and each artist is owned by a user. Only the owner can edit or delete artists, 
add artwork and edit or delete artwork belonging to their artists. Users are authenticated with Google Accounts.

## Getting Started

Here is how to get up and running...

### Prerequisites

* [Python 2.7](https://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [WTForms](https://flask-wtf.readthedocs.io/en/stable/)
* [OAuth2client](https://pypi.org/project/oauth2client/)

### Usage

1. Ensure the above prerequisites are installed.
2. In the project root, execute `python database_setup.py` to create the art sqlite database.
3. (Optional) execute `python artitems.py` if you want the database populated with some sample data.
4. Execute `python cartalogue.py` to start the server.
5. Navigate to `localhost:5000` to start using the app by UI.

Note: To create artists/artwork you will need a [Google Account](https://account.google.com).
Log in by using the login button in the top navigation bar.

### JSON Endpoints
You can also retrieve JSON data from the database by using the following endpoints:
* `/artist/<int:artist_id>/JSON` Retrieves information of an artist
* `/artist/<int:artist_id>/artwork/<int:artwork_id>/JSON` Retrieves information of an artwork
* `/artist/JSON` Retrieves all artists
* `/artwork/JSON` Retrieves all artwork

## Authors

* **Rebecca Anderson** - [beccaneer](https://github.com/beccaneer)

## Acknowledgments

* Sample art data taken from Wikipedia.
* Commenting and code for login/logout functions used from Udacity Full Stack Developer class, Lesson 4.
* README template adapted from [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
