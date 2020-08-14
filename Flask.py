import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime as dt, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end"
        
    )

@app.route("/api/v1.0/precipitation")
def prcp():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all prcp data
    prcp_results =  session.query(Measurement.date, Measurement.prcp).all()

    prcp_result_list = []
    
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_result_list.append(prcp_dict)
    
    session.close()


    return jsonify(prcp_result_list)


#------------------------------------------------
@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to the DB
    session = Session(engine)

    # Query for list of stations
    results = session.query(Station.station, Station.name).all()

    session.close()
    
    station_data = []
    for station, name in results:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        station_data.append(station_dict)
    
    return jsonify(station_data)


#------------------------------------------------
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to the DB
    session = Session(engine)
    
    # Latest date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_dt = dt.strptime(last_date[0], '%Y-%m-%d').date()
    
    
    # Date 12 months ago
    date_year_ago = last_date_dt - timedelta(days=365)

    # Query for temperature in the last 12 months
    precip_records = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >=date_year_ago).all()

    session.close()
    
    temperature_data = []
    for date, tobs in precip_records:
        temperature_dict = {}
        temperature_dict["Date"] = date
        temperature_dict["Temperature"] = tobs
        temperature_data.append(temperature_dict)  

    return jsonify(temperature_data)

#------------------------------------------------
@app.route("/api/v1.0/<start>")

# Create session from Python to the DB
def startdate(start):
    
    session = Session(engine)

    start_date = '2016-07-01'

    results = session.query(  Measurement.date,\
            func.min(Measurement.tobs), \
            func.avg(Measurement.tobs), \
            func.max(Measurement.tobs)).\
            filter(and_(Measurement.date >= start, Measurement.date <= end)).\
            group_by(Measurement.date).all()

    results_list = list(np.ravel(results))
    
    t_min = (results_list)[0]
    t_max = (results_list)[1]
    t_avg = (results_list)[2]
    
    results_data= []
    results_list_dict =[{"Start Date": start},
                       {"Minimum Temperature": t_min},
                       {"Maximum Temperature": t_max},
                       {"Average Temperature": t_avg}]

    results_data.append(results_list_dict)
    
    return jsonify(results_data)

#------------------------------------------------

@app.route("/api/v1.0/<start>/<end>")

# Create session from Python to the DB
def startend(start,end):

    session = Session(engine)
    start_date = '2016-07-01'
    end_date = '2016-07-10'


   #temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
      # filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    temp_stats= session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(and_(Measurement.date >= start, Measurement.date <= end)).\
                        group_by(Measurement.date).all()

    temp_stats_list = list(np.ravel(temp_stats))
    min_temp =  temp_stats_list[0]
    avg_temp =  temp_stats_list[1]
    max_temp=  temp_stats_list[2]
        
        temp_stats_data = []
        temp_stats_dict = [{"Start Date": start_date},
                        {"End Date": end_date},
                        {"Minimum Temperature": min_temp},
                        {"Maximum Temperature": max_temp},
                        {"Average Temperature": avg_temp}]

        temp_stats_data.append(temp_stats_dict)
    
    return jsonify(results_list)


if __name__ == '__main__':
    app.run(debug=True)