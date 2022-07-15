#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  if not venues:
    flash('Venue not found!! Create one!!!')
    return render_template('pages/venues.html', areas=data)
  data = []
  for venue in venues:
    num_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).count()
    venue_dict = {'id':venue.id, 'name':venue.name, 'num_upcoming_shows': num_upcoming_shows}
    currentData = [(d) for d in data if (d['city'] == venue.city and d['state'] == venue.state)]
    if not(currentData):
      cityStateVenue_dict  = {'city': venue.city, 'state': venue.state, 'venues': [venue_dict] }
      data.append(cityStateVenue_dict)
    else:
      venues_list = currentData[0]['venues']
      venues_list.append(venue_dict)
      data[data.index(currentData[0])]['venues'] = venues_list
  return render_template('pages/venues.html', areas=data)
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #  "venues": [{
  #      "id": 1,
  #     "name": "The Musical Hop",
  #    "num_upcoming_shows": 0,
  #  }, {
  #   "id": 3,
  #  "name": "Park Square Live Music & Coffee",
  #  "num_upcoming_shows": 1,
  # }]
  #}, {
  # "city": "New York",
  # "state": "NY",
  # "venues": [{
  #  "id": 2,
  #  "name": "The Dueling Pianos Bar",
  # "num_upcoming_shows": 0,
  #}]
  #}]
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  searchResult = request.form['search_term']
  data = []
  requiredVenues = Venue.query.filter(Venue.name.ilike('%'+searchResult+'%'))
  for venue in requiredVenues:
    data.append({
      "id" : venue.id,
      "name" : venue.name,
      "num_upcoming_shows" : db.session.query(Venue).join(Show).filter(
      Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).count()
    })
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id == venue_id).first()
  shows = []
  shows = db.session.query(
  Artist.id.label('artist_id'),
  Artist.name.label('artist_name'),
  Artist.image_link.label('artist_image_link'),
  Show.start_time).join(Show).filter(
  Show.venue_id == venue_id).filter(
  Show.start_time < datetime.now())
  past_shows = []
  for show in shows:
    past_shows.append(
      {
       'artist_id' :show['artist_id'],
       'artist_name' : show['artist_name'],
       'artist_image_link' : show['artist_image_link'],
       'start_time' : show['start_time'].strftime("%Y-%m-%dT%H:%M:%S.000Z")
      }
    )
  shows = db.session.query(
  Artist.id.label('artist_id'),
  Artist.name.label('artist_name'),
  Artist.image_link.label('artist_image_link'),
  Show.start_time).join(Show).filter(
  Show.venue_id == venue_id).filter(
  Show.start_time > datetime.now())
  upcoming_shows = []
  for show in shows:
    upcoming_shows.append(
      {
       'artist_id' :show['artist_id'],
       'artist_name' : show['artist_name'],
       'artist_image_link' : show['artist_image_link'],
       'start_time' : show['start_time'].strftime("%Y-%m-%dT%H:%M:%S.000Z")
      }
    )
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows" :past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    
    form = VenueForm(request.form)
    venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data)
    db.session.add(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
  except:
        db.session.rollback()
  finally:
        db.session.close()
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=db.session.query(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searchResult = request.form['search_term']
  data = []
  requiredVenues = Artist.query.filter(Artist.name.ilike('%'+searchResult+'%'))
  for artist in requiredVenues:
    data.append({
      "id" : artist.id,
      "name" : artist.name,
      "num_upcoming_shows" : db.session.query(Artist).join(Show).filter(
    Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).count()
    })
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter(Artist.id == artist_id).first()
    shows = []
    shows = db.session.query(
    Venue.id.label('venue_id'),
    Venue.name.label('venue_name'),
    Venue.image_link.label('venue_image_link'),
    Show.start_time).join(Show).filter(
    Show.artist_id == artist_id).filter(
    Show.start_time < datetime.now())
    past_shows = []
    for show in shows:
      past_shows.append(
      {
        'venue_id' :show['venue_id'],
        'venue_name' : show['venue_name'],
        'venue_image_link' : show['venue_image_link'],
        'start_time' : show['start_time'].strftime("%Y-%m-%dT%H:%M:%S.000Z")
        }
      )
    shows = db.session.query(
    Venue.id.label('venue_id'),
    Venue.name.label('venue_name'),
    Venue.image_link.label('venue_image_link'),
    Show.start_time).join(Show).filter(
    Show.artist_id == artist_id).filter(
    Show.start_time > datetime.now())
    upcoming_shows = []
    for show in shows:
      upcoming_shows.append(
        {
        'venue_id' :show['venue_id'],
        'venue_name' : show['venue_name'],
        'venue_image_link' : show['venue_image_link'],
        'start_time' : show['start_time'].strftime("%Y-%m-%dT%H:%M:%S.000Z")
        }
      )
    data={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.split(','),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows" :past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
      }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.filter(Artist.id == artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
     artist = Artist.query.get(artist_id)
     artist.name=request.form['name']
     artist.city=request.form['city']
     artist.state=request.form['state']
     artist.phone =request.form['phone'],
     artist.image_link=request.form['image_link']
     artist.facebook_link=request.form['facebook_link']
     artist.website =request.form['website_link'],
     artist.seeking_venue =bool(request.form.get('seeking_venue'))
     artist.seeking_description =request.form['seeking_description'],
     artist.genres=','.join([str(item) for item in request.form.getlist('genres')])
     db.session.add(artist)
     db.session.commit()
     flash('Artist ' + request.form['name'] + ' was successfully Updated!')
  except:
     db.session.rollback()
     flash('An error occurred. Artist  ' + request.form['name'] + ' could not be Update.')
  finally:
        db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.filter(Venue.id == venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
     venue = Venue.query.get(venue_id)
     venue.name=request.form['name']
     venue.city=request.form['city']
     venue.state=request.form['state']
     venue.address=request.form['address']
     venue.phone =request.form['phone'],
     venue.image_link=request.form['image_link']
     venue.facebook_link=request.form['facebook_link']
     venue.website =request.form['website_link'],
     venue.seeking_talent =bool(request.form.get('seeking_talent'))
     venue.seeking_description =request.form['seeking_description'],
     venue.genres=','.join([str(item) for item in request.form.getlist('genres')])
     db.session.add(venue)
     db.session.commit()
     flash('Venue ' + request.form['name'] + ' was successfully Updated!')
  except:
     db.session.rollback()
     flash('An error occurred. Venue  ' + request.form['name'] + ' could not be Update.')
  finally:
        db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  try:
    artist = Artist( name = request.form['name'], city = request.form['city'], 
    state = request.form['state'], phone = request.form['phone'],
    image_link = request.form['image_link'], facebook_link = request.form['facebook_link'], 
    website = request.form['website_link'], seeking_venue = bool(request.form.get('seeking_venue'))
    ,seeking_description =request.form['seeking_description'], 
    genres=','.join([str(item) for item in request.form.getlist('genres')]))
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append(
      {
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
      }
    )
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Show(
    artist_id = request.form['artist_id'],
    venue_id = request.form['venue_id'],
    start_time = request.form['start_time'])
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
