# Python SQL toolkit and Object Relational Mapper - ORM
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import datetime as dt
from flask_ngrok import run_with_ngrok
from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
# reflect the tables

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save reference to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#  Flask Setup
app = Flask(__name__)
run_with_ngrok(app)

#  Create session link from Python to the SQLite DB
session = Session(engine)

###  Route to Welcome page

@app.route("/")
def welcome():
    print("Server received request for 'Welcome' page...")
    return (f"Welcome to my Precipitation API<br/>"
           f" <br/>" 
           f"The 5 available routes are listed below:<br/>"
           f" <br/>"
           f"This route will show precip data from 1 yr ago:<br/>"
           f"/api/v1.0/precipitation<br/>"
           f" <br/>"
           f"This route will list all of the stations:<br/>"
           f"/api/v1.0/stations<br/>"
           f" <br/>"
           f"This route will show all the temp observations for the most active station:<br/>"
           f"/api/v1.0/tobs<br/>"
           f" <br/>"
           f"Enter your travel date(s) below in the format shown:<br/> "
           f" <br/>"
           f"This route will display the low, avg and high temperatures for all dates > = to the date entered:<br/>"
           f"/api/v1.0/yyyy-mm-dd<br/>"
           f" <br/>"
           f"This route accepts a date range.  Be sure to separate the 2 dates you enter with a space or a dash:<br/>"
           f"It will display the low, avg and high temperatures for the date range.<br/>"
           f"/api/v1.0/yyyy-mm-dd yyyy-mm-dd")

# Precipitation Route
# Return the precipitation data from 1 year ago as json

@app.route("/api/v1.0/precipitation")
def precip():
    
#  Create session link from Python to the SQLite DB
    session = Session(engine)

    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    
# Create a dictionary from the row data using date as the key and prcp as the value and return a json object.    
    
    # for date, prcp in year_prcp:
    #     prcp_dict = {}
    #     prcp_dict[date] = prcp

    session.close()           
    #return jsonify(prcp_dict)
    return jsonify(year_prcp)

# Station route showing all stations:

@app.route("/api/v1.0/stations")
def Stations():

#  Create session link from Python to the SQLite DB
    session = Session(engine)

    all_stations = session.query(Station.station).order_by(Station.station).all()
    
    session.close()
    
    return jsonify(all_stations)

# TOBS - Temperature Observations Route:
# Return the TOBS for the last year for the most active station 

@app.route("/api/v1.0/tobs")
def tobs():

# Find the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station
# find the latest date for this station is - 2017-08-18

#  Create session link from Python to the SQLite DB
    session = Session(engine)    

    most_active_station = session.query(Measurement.station).group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).first()
    
    latest_date2 = session.query(Measurement.date).filter(Measurement.station == most_active_station[0]).\
            order_by(Measurement.date.desc()).first()
    one_year_ago2 = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    
    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago2).\
            order_by(Measurement.date).group_by(Measurement.date).all()

    session.close()
    
    return jsonify(tobs)
    

# Create a session link from Python to the DB.
# Return the min, avg and max temps starting with the given start date provided by user

@app.route("/api/v1.0/<start>")
def start(start):

#  Create session link from Python to the SQLite DB
    session = Session(engine)    
    
    sel = [func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)]
    tobs_mam = session.query(*sel).filter(Measurement.date >= start).all()

    session.close()

    return jsonify(tobs_mam)

# Create a session link from Python to the DB.
# Return the min, avg and max temps for a given date range

@app.route("/api/v1.0/<start>/<stop>")
def start_stop(start, stop):

#  Create session link from Python to the SQLite DB
    session = Session(engine)

    sel = [func.min(tobs),
           func.avg(tobs),
           func.max(tobs)]

    tobs_mam = session.query(*sel).filter(Measurement.date >= start).\
            filter(Measurement.date <= stop).order_by(Measurement.date).all()
    
    session.close()

    return jsonify(tobs_mam)

if __name__ == "__main__":
    app.run()