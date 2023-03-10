import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
#    Correctly generate the engine to the correct sqlite file (2 points)
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#    Use automap_base() and reflect the database schema (2 points)
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine=engine, reflect=True)

#    Correctly save references to the tables in the sqlite file (measurement and station) (2 points)
# Save reference to the tables
measurement = Base.classes.measurement
station = Base.classes.station

#   calculating 1 year before the data
year_before = dt.date(2017, 8 ,23) - dt.timedelta(days=365)
final_date = dt.date(2017, 8 ,23)

app = Flask(__name__)

#    Display the available routes on the landing page (2 points)
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"api/v1.0/start/2017-8-23<br/>"
    )

#   Returns json with the date as the key and the value as the precipitation (3 points)
#   Only returns the jsonified precipitation data for the last year in the database (3 points)
@app.route("/api/v1.0/precipitation")
def precipitation():
    #opening session from python to db
    session = Session(engine)
    #query the precipitation data for the year
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_before).order_by(measurement.date).all()
    session.close()

    #creating a dictionary from the row data and appending to a list with the date as the key and the value as the amount of precipitation
    precipt_data = []
    for rows in results:
        results_dict = {}
        results_dict[rows.date] = rows.prcp
        precipt_data.append(results_dict)

    return jsonify(precipt_data)


#   Returns jsonified data of all of the stations in the database (3 points)
@app.route("/api/v1.0/stations")
def stations():
    #opening, closing the session and querying all data from the stations
    session = Session(engine)
    results = session.query(station)
    session.close()

    #creating a dictionary from the raw data and appending to a list
    station_data = []
    for rows in results:
        station_dict={}
        station_dict['station'] = rows.station
        station_dict['name'] = rows.name
        station_dict['latitude'] = rows.latitude
        station_dict['longitude'] = rows.longitude
        station_dict['elevation'] = rows.elevation
        station_data.append(station_dict)
    
    return jsonify(station_data)
        
#   Returns jsonified data for the most active station (USC00519281) (3 points)
#   Only returns the jsonified data for the last year of data (3 points)
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(measurement).filter(measurement.station=='USC00519281').filter(measurement.date>=year_before)
    session.close()

    #I wasnt sure what data to pull because it didn't specify so i just put all of it in
    tobs_data = []
    for rows in results:
        tobs_dict ={}
        tobs_dict['station'] = rows.station
        tobs_dict['date'] = rows.date
        tobs_dict['prcp'] = rows.prcp
        tobs_dict['tobs'] = rows.tobs
        tobs_data.append(tobs_dict)
    
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
    #splitting the input variable start date by -
    start = start.split('-')
    #creating the datetime variable
    year = start[0]
    month = start[1]
    day = start[2]
    start_date = dt.date(year,month,day)
    #this didn't specify to jsonify the data so I didn't. calling my helper function
    return temp_data_func(start_date, final_date)



@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    #splitting the input variable start date by -
    start = start.split('-')
    #creating the y,m,d variables
    s_year = start[0]
    s_month = start[1]
    s_day = start[2]


    #splitting the input variable start date by -
    end = start.split('-')
    #creating the y,m,d variables
    e_year = end[0]
    e_month = end[1]
    e_day = end[2]

    #creating datetime objects
    start_date = dt.date(s_year, s_month, s_day)
    end_date = dt.date(e_year, e_month, e_day)

    #calling my helper function
    return temp_data_func(start_date, end_date)




#created a helper function to get min, avg, max
def temp_data_func(start_date, end_date):
    session = Session(engine)
    lowest = session.query(func.min(measurement.tobs)).filter(end_date>=start_date).first()
    highest = session.query(func.max(measurement.tobs)).filter(end_date>=start_date).first()
    average = session.query(func.avg(measurement.tobs)).filter(end_date>=start_date).first()
    session.close()

    temp_data =[
        {'TMIN':lowest},
        {'TAVG':average},
        {'TMAX':highest}
            
    ]

    return temp_data

if __name__ == "__main__":
    app.run(debug=True)