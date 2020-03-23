import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
session = Session(engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last data point in the database
    date = dt.date(2017,8,23)-dt.timedelta(days = 365)
    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= date).all()
    
    results = {date:prcp for date,prcp in precipitation}
    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    station = session.query(Station.station).all()
    results = list(np.ravel(station))
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= previous_year).all()
    tobs = list(np.ravel(results))
    return jsonify(tobs)


@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps(start_date = '2012-02-28', end_date = '2012-03-05'):
    session = Session(engine)
# Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end_date:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).filter(Measurement.date >= start_date).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        session.close()
        return jsonify(temps)
        # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    session.close()
    return jsonify(temps)

session.close()



if __name__ == '__main__':
    app.run(debug=True)
