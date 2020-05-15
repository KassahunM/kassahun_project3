import os
from flask import Flask,render_template,request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app=Flask(__name__)

engine=create_engine(os.getenv("DATABASE_URL")) #url where Database is hosted (can be localhost or internet)
db=scoped_session(sessionmaker(bind=engine))    #creating different sessions for different people accessing or working on the darabase

@app.route("/")
def index():
    flights=db.execute("SELECT * FROM flights").fetchall()
    return render_template("index.html",flights=flights)

@app.route("/book", methods=["POST"])
def book():
    """ book flight """
    #get form information
    name = request.form.get("name")
    try:
        flight_id = request.form.get("flight_id")
    except ValueError:
        return render_template("error.html", message="Invalid flight number.")
    #make sure flight exists
    if db.execute("SELECT * FROM flights WHERE id=:id",{"id":flight_id}).rowcount==0:
        return render_template("error.html",message="No such flight with that id number.")
    
    db.execute("INSERT INTO passengers (name,flight_id) VALUES (:name, :flight_id)",{"name":name, "flight_id":flight_id})

    db.commit()

    return render_template("success.html")


@app.route("/flights")
def flights():
    """List all flights """
    flights=db.execute("SELECT * FROM flights").fetchall()
    return render_template("flights.html", flights=flights)


@app.route("/flights/<int:flight_id>")
def flight(flight_id):

    """list details of a single flight """

    #make sure flight exists
    flight=db.execute("SELECT * FROM flights WHERE id=:id",{"id": flight_id}).fetchone()
    if flight is None:
        return render_template("error.html", message="No such flight")
        
    #Get all passengers

    passengers=db.execute("SELECT name FROM passengers WHERE flight_id=:flight_id",{"flight_id":flight_id}).fetchall()
    #passengers=flight.passengers  #when applying ORM
    return render_template("flight.html",flight=flight,passengers=passengers)
    #return render_template("flight.html",flight=flight,passengers=passengers) #when applying ORM
    
if __name__ == "__main__":
    app.run(debug = True)
   
