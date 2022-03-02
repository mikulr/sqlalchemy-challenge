import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

from flask import Flask, jsonify



# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo=False)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table / creating the class
Measurement = Base.classes.measurement
Station = Base.classes.station

app=Flask(__name__)
    
@app.route("/")
@app.route("/home")
def home():
    return (
        f"<h1>Welcome to the Weather Analysis API!</h1><br/>"
        f"<h2>Available Routes:</h2><br/>"
        f"<h3>/api/v1.0/precipitation</h3><br/>" 
        f"<i>to see a dictionary of all dates and precipitation amounts.</i><br/>"
        f"<h3>/api/v1.0/stations</h3><br/>"
        f"<i>to see a list of all stations.</i><br/>"
        f"<h3>/api/v1.0/tobs</h3><br/>"
        f"<i>to see temperature observations of the most active station for the last year of data.</i><br/>"
        f"<h3>/api/v1.0/start/<start></h3><br/>"
        f"<i> to see a list of the minimum temperature, the average temperature, and the max temperature for all dates greater than and equal to the start date.</i><br/>"
        f"<i> **Please enter a date in YYYY-MM-DD format after the final '/' in the route to see results.**<i/> </br>"
        f"<h3>/api/v1.0/start/end/<start>/<end></h3><br/>"
        f"<i> to see a list of the minimum temperature, the average temperature, and the max temperature for dates between the start and end date, inclusive.</i><br/>"
        f"<i> ** Please enter two dates in YYYY-MM-DD format with the earlier date before the final '/' in the address and the later date after.**</i> </br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    #Query a list of all date & prcp values
    results = session.query(Measurement.date, Measurement.prcp).all()
   
    session.close()

    # Create a dictionary from the row data and append to a list of all_prcp
    #First create an empty list then iterate into by creating a dictionary with key
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipipation"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp) 

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Station names"""
    results2 = session.query(Station.name).all()
    #get use close, if we do another query we will open another one
    session.close()
    
    all_names = list(np.ravel(results2))
    
    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent= session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    dt1 = dt.datetime.strptime(recent, '%Y-%m-%d') - dt.timedelta(days=365)
    busiest= session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    station_no=busiest [0]
    #run query
    results3 = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date > dt1).filter(Measurement.station == station_no).all()
    #get use close, if we do another query we will open another one
    session.close()
    
    all_tobs = list(np.ravel(results3))
    
    return jsonify(all_tobs)


@app.route('/api/v1.0/start/<start>')
def start_dt(start):
    
    session = Session(engine)
    
    calcs= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    all_calcs = []
    for min, avg, max in calcs:
        calc_dict = {}
        calc_dict["Minimum Temp"] = min
        calc_dict["Average Temp"] = avg
        calc_dict["Maximum Temp"] = max
        all_calcs.append(calc_dict)
    
    return jsonify(all_calcs)

     
    


@app.route('/api/v1.0/start/end/<start>/<end>')
def st_stop(start,end):
    #start= request.args.get(start)
    #end=request.args.get(end)
    session = Session(engine)
    
    calcs= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start). filter(Measurement.date <= end).all()

    all_calcs = []
    for min, avg, max in calcs:
        calc_dict = {}
        calc_dict["Minimum Temp"] = min
        calc_dict["Average Temp"] = avg
        calc_dict["Maximum Temp"] = max
        all_calcs.append(calc_dict)
    
    return jsonify(all_calcs)
    
   # session.close()

if __name__ == "__main__":
    app.run(debug=True)
