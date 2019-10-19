import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station


app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return "<h1>Surf's Up API: Home Page </h1><br><hr> \
            <h3>Available routes:</h3><br> \
            <ul>\
                <li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a> </li> \
                <li><a href ='/api/v1.0/stations'>/api/v1.0/stations</a></li> \
                <li><a href = '/api/v1.0/tobs'>/api/v1.0/tobs</a></li> \
                <li><a href = '/api/v1.0/1-1-2001'>/api/v1.0/*start date*</a></li> \
                <li><a href = '/api/v1.0/5-15-2015/7-5-2016'>/api/v1.0/*start date*/*end date*</a></li>\
            </ul><br>\
            <hr>\
            <h3> Notes: </h3><br>\
            <p> The <b>'/precipitation'</b> route returns all dates and corresponding precipitation. <br><br>\
                The <b>'/stations'</b> route returns data on all stations. <br><br>\
                The <b>'/tobs'</b> route returns dates and temperature observations for the most active station for a year prior to the last data \
                    point. <br><br>\
                To search for minimum temperature, average temperature, and max temperature for a given date range, enter the dates <br> \
                    in the format <b>m-d-yyyy</b>.\
            </p>\
            <hr>"


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' page...")
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).all()
    session.close()
    data = []
    for date,prcp in results:
        data_dict = {}
        data_dict["date"] = date
        data_dict["prcp"] = prcp
        data.append(data_dict)

    return jsonify(data)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page...")
    session = Session(engine)
    results = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    session.close()
    data = []
    for stat, name, latitude, longitude, elevation in results:
        data_dict = {}
        data_dict["station"] = stat
        data_dict["name"] = name
        data_dict["lat"] = latitude
        data_dict["lng"] = longitude
        data_dict["elev"] = elevation
        
        data.append(data_dict)

    return jsonify(data)


@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...") 
    session = Session(engine)
    results = session.query(measurement.station, measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281')\
        .filter(measurement.date > datetime.datetime(2016, 8, 23, 00, 00)).all()
    session.close()
    data = []
    for stat, date, tobs in results:
        data_dict = {}
        data_dict["station"] = stat
        data_dict["date"] = date
        data_dict["tobs"] = tobs
        data.append(data_dict)

    return jsonify(data)

# if the data in the files included recent years, this variable could be used as the datetime 
# object to calculate a year prior to the current date:
#last_year = datetime.datetime.now() - datetime.timedelta(days = 365)

@app.route("/api/v1.0/<start>")
def start_date(start):
    datemask = '%m-%d-%Y'
    date = datetime.datetime.strptime(start, datemask)
    print("Server received request for 'start_date' page...")
        
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
        .filter(measurement.date >= date)
    session.close()
    
    data = []
    for min, avg, max in results:
        data_dict = {}
        data_dict["tmin"] = min
        data_dict["tavg"] = avg
        data_dict["tmax"] = max
        data.append(data_dict)

    return jsonify(data)


@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
    datemask = '%m-%d-%Y'
    date1 = datetime.datetime.strptime(start, datemask)
    date2 = datetime.datetime.strptime(end, datemask)
    print("Server received request for 'start_date' page...")
        
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
        .filter(measurement.date.between(date1, date2))
    session.close()
    
    data = []
    for min, avg, max in results:
        data_dict = {}
        data_dict["tmin"] = min
        data_dict["tavg"] = avg
        data_dict["tmax"] = max
        data.append(data_dict)

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug = True)



