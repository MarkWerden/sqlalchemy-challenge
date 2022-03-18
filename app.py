# Importing Flask (required to run)
from flask import Flask, jsonify # ("jsonify" was hinted at needing to be used in the directions)

# Importing Dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base         # (A good majority of this code will mirror the data in the jupyter assignment, as the
from sqlalchemy.orm import Session                      # server will need to calculate the values as well to display to the user.)
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool

# Creating engine for the server
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)

# Reflecting existing database into model and reflecting tables for server
Base = automap_base()
Base.prepare(engine, reflect=True)

# Saving references for the table
measurement = Base.classes.measurement
station = Base.classes.station

# Creating temporary link between Python and the Database
session = Session(engine)

# Setting up Flask and its routes
app = Flask(__name__)

@app.route("/") # (The homepage)
def welcome():
    print("Listing all avalible API routes...") # (Only the server will see this)
    return (
        f"Avalible Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start) (Enter as: YYYY-MM-DD)<br/>"
        f"/api/v1.0/(start)/(end) (Enter as: YYYY-MM-DD/YYYY-MM-DD)"
    )

@app.route("/api/v1.0/precipitation") # (The precipitation route)
def precipitation():
    print("Retrieving precipitation data...")
    session = Session(engine)
    results = (session.query(measurement.date, measurement.tobs).order_by(measurement.date))
    
    precipitation_data = [] # (A list is used instead of a pandas dataframe cause the user will not be able to see the dataframe created within it)
    for row in results:
        dt_dict = {}
        dt_dict["date"] = row.date
        dt_dict["tobs"] = row.tobs
        precipitation_data.append(dt_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations") # (The stations route)
def stations():
    print("Retrieving station data...")
    session = Session(engine)
    results = session.query(station.name).all()
    station_details = list(np.ravel(results)) # (This was converted into a tuple for better data storage)
    return jsonify(station_details)

@app.route("/api/v1.0/tobs") # (The observation data route)
def tobs():
    print("Retrieving observation data...")
    year_prior = dt.date(2017,8,23) - dt.timedelta(days=365)
    tobs_data = session.query(measurement.date, measurement.tobs).filter(measurement.date >= year_prior).order_by(measurement.date).all() 
    tobs_data_list = list(np.ravel(tobs_data))
    return jsonify(tobs_data_list)

@app.route("/api/v1.0/<start>") # (The starting day route) [note that it will list all dates before the last date in the dataset]
def start_day(start): # (Basically saying that it will use the starting day that is provided by the user, if its a valid date)
    print("Retrieving defined starting date data...")
    start_day = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).group_by(measurement.date).all()
    start_day_list = list(np.ravel(start_day))
    return jsonify(start_day_list)

@app.route("/api/v1.0/<start>/<end>") # (The ranged date route) [note that starting date must be lower than ending date]
def start_end_day(start, end):
    print("Retrieving defined ranged date data...")
    start_end_day = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).group_by(measurement.date).all()
    start_end_day_list = list(np.ravel(start_end_day))
    return jsonify(start_end_day_list)

# (The core behavior of the flask API, needed to run)
if __name__ == '__main__':
    app.run(debug=True)