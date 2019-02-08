import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

###########################################
# Setup Database
###########################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

#Create references to Measurement and Station tables

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

####################################
# Setup Flask app
####################################
app = Flask(__name__)

################################
#Setup Flask Routes
################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"<H3>Welcome to the Hawaii Climate Analysis API!<br/><br />"
        f"Available Routes:<br/>"
        f"This API returns dates and precipitation:     "
        f"/api/v1.0/precipitation<br/>"
        f"This API returns a list of stations:      "
        f"/api/v1.0/stations<br/>"
        f"This API returns dates and temperature observations from a year from the last data point:      "
        f"/api/v1.0/tobs<br/>"
        f"This API allows you to consult average, min and max temperatures entering a start date. <br/>"
        f"Please enter start date as YYYY-mm-dd: "
        f"/api/v1.0/<start><br/>"
        f"This API allows you to consult average, min and max temperatures between two dates: <br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns dates and precipitation"""
    prcp = session.query(Measurement.date, Measurement.prcp).all()

# Create a list of dicts with `date` and `prcp` as the keys and values
    all_prcp = []
    for result in prcp:
        row = {}
        row["date"] = prcp[0]
        row["prcp"] = prcp[1]
        all_prcp.append(row)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations from the station table
    station_results = session.query(Station.station, Station.station.name).all()

    station_list = list(np.ravel(station_results))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #query for the dates and temperature observations from a year from the last data point.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_all = []
    for result in tobs:
        row = {}
        row["date"] = tobs[0]
        row["tobs"] = tobs[1]
        temperature_all.append(row)

    return jsonify(temperature_all)
#This one works sometimes :(
@app.route("/api/v1.0/<start>")
def start_temp(start):
    startdate=dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= startdate).all()

#Create JSON
    data_list = []
    for result in results:
        row = {}
        row['date'] = result[0]
        row['avg'] = float(result[1])
        row['max'] = float(result[2])
        row['min'] = float(result[3])
        data_list.append(row)

    return jsonify(data_list)

@app.route("/api/v1.0/<start>/<end>")
def between_temp(start, end):
    start_date=dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end, '%Y-%m-%d')
    results = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all().all()

#Create JSON
    data_list = []
    for result in results:
        row = {}
        row['date'] = result[0]
        row['avg'] = float(result[1])
        row['max'] = float(result[2])
        row['min'] = float(result[3])
        data_list.append(row)

    return jsonify(data_list)

if __name__ == '__main__':
    app.run(debug=True)


