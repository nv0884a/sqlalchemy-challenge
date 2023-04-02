# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import create_engine, func, and_
from datetime import datetime, timedelta
import matplotlib.pyplot as plt




#################################################
# Database Setup
#################################################
app = Flask(__name__)


engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()


Base.prepare(engine, reflect=True)

station = Base.classes.station
measurement = Base.classes.measurement






@app.route("/")
def welcome():
    """List all available api routes."""
        
    return (
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/aggregate/&lt;start&gt;<br>"
        "/api/v1.0/aggregate/&lt;start&gt;/&lt;end&gt;<br>"
    )
    

#The below code is essentially the same as the one via pandas
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    most_recent_date = session.query(func.max(measurement.date)).scalar()

    most_recent_datetime = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_from_last_date = most_recent_datetime - timedelta(days=365)

    precepitation_data = session.query(measurement.date, measurement.prcp)\
    .filter(and_(measurement.date>one_year_from_last_date, measurement.date < most_recent_datetime))\
    .group_by(measurement.date)\
    .order_by(measurement.date).all()

    prcp_dict = {x[0]:x[1] for x in precepitation_data}

    session.close()

    return jsonify(prcp_dict)

#The below code is essentially the same as the one via pandas
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_query = session.query(measurement.station,func.count(measurement.station))\
    .group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    station_dict = {x[0]:x[1] for x in station_query}

    session.close()

    return jsonify(station_dict)


#The below code is essentially the same as the one via pandas
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)


    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_datetime = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_from_last_date = most_recent_datetime - timedelta(days=365)

    most_active_station_query = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).\
    limit(1)

    most_active_station_id = most_active_station_query.first()[0]

    temps = session.query(measurement.date,measurement.tobs).\
    filter(measurement.station == most_active_station_id).\
    filter(measurement.date >= one_year_from_last_date).all()
    

    tobs_dict = {x[0]:x[1] for x in temps}



    session.close()

    return jsonify(tobs_dict)


#For the below code, I received help from my classmates as well as my tutor Kourt Bailey
@app.route('/api/v1.0/aggregate/<start>', defaults = {'end':None})
@app.route("/api/v1.0/aggregate/<start>/<end>")
def aggregate_data(start, end):

    session = Session(engine)
    if end != None:
        min_temp = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        max_temp = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        
    else:
        min_temp = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).all()
        max_temp = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).all()
        avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    

    min_temp = min_temp[0][0]
    max_temp = max_temp[0][0]
    avg_temp = avg_temp[0][0]

    results = {
        "Min temp": min_temp,
        "Max temp": max_temp,
        "Average temp": avg_temp
     }
    session.close()
    return jsonify(results)


if __name__ == "__main__":
    app.run()
