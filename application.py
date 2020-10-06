import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///wtm.db")


@app.route("/")
@login_required
def index():
    """Show all parties"""


    #collects info from parties table
    partyInfo = db.execute("SELECT partyName,time,location,spot,user_id FROM parties")

    parties = {}

    #inserts info into a dictionary to place into a table
    for row in partyInfo:
            aList = []
            aList.append(row["location"])
            aList.append(row["spot"])
            aList.append(row["time"])
            personName = db.execute("SELECT username FROM users WHERE userID = :user",user = row["user_id"])
            aList.append(personName[0]["username"])
            parties[row["partyName"]] = aList


    return render_template("index.html",parties=parties)

#Method that displays an error page
def apology(errorMessage):
    return render_template("apology.html",errorMessage=errorMessage)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["userID"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Log user in"""
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide a username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide a password")

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password must match")


        # Query database for username
        rows = db.execute("SELECT username FROM users")

        for row in rows:
            if row["username"] == request.form.get("password"):
                return apology("username already taken")


        #inserts user into table
        db.execute("INSERT INTO users(username,hash) VALUES (:username,:hash)",username=request.form.get("username"),hash=generate_password_hash(request.form.get("password")))


        # Redirect user to home page
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/make", methods = ["GET","POST"])
def make():
    """Make party page"""

    if request.method == "GET":
         return render_template("make.html")
    else:
        #gets information for a party and insures that the user fills out all the boxes
        if request.form.get("partyName") == None:
            return apology("Enter a name")
        if request.form.get("date") == None:
            return apology("Enter a date")
        if request.form.get("location") == None:
            return apology("Enter a location")
        if request.form.get("partyName") == None:
            return apology("Enter a Room number or Hall")

        #formats the date in a cleaner way
        time = datetime.strptime(request.form.get("date"),"%Y-%m-%dT%H:%M")

        #inserts party into party table
        db.execute("INSERT INTO parties (user_id,partyName,location,spot,time) VALUES (:user_id,:partyName,:location,:spot,:time)",user_id = session["user_id"],partyName=request.form.get("partyName"),location = request.form.get("location"),spot = request.form.get("spot"),time = time.strftime("%b %d %Y %-I:%M%p"))
        return render_template("make.html")


@app.route("/rsvp", methods = ["GET","POST"])
def rsvp():
    if request.method == "GET":
        #gets names of all the parties
        rows = db.execute("SELECT partyName FROM parties")
        listOfParties = []

        #puts info into a list to send to the html page
        for row in rows:
            listOfParties.append(row["partyName"])
        return render_template("rsvp.html",partyList=listOfParties)
    else:
        #ensures that the user inputs all info
        if not request.form.get("party") or request.form.get("party") == "0":
            return apology("Input a party!")
        if request.form.get("offering") == None :
            return apology("You have to bring something!")

        #gets info of user and party
        partyInfo = db.execute("SELECT partyID,user_id FROM parties WHERE partyName = :name", name = request.form.get("party"))

        #inserts RSVP into RSVP table
        db.execute("INSERT INTO rsvp (attendee_id,host_id,party_id,offering) VALUES (:attendee,:host,:party,:offering)",attendee = session["user_id"], host = partyInfo[0]["user_id"],party = partyInfo[0]["partyID"],offering = request.form.get("offering"))
        return render_template("rsvp.html")

@app.route("/password",methods=["GET", "POST"])
@login_required
def password():
    if request.method == "GET":
        return render_template("password.html")
    else:
         #changes password
        newPassword = request.form.get("password")
        db.execute("UPDATE users SET hash = :password WHERE id = :id",password=generate_password_hash(newPassword), id=session["user_id"])
        return render_template("password.html")


@app.route("/info",methods=["GET", "POST"])
@login_required
def info():
    if request.method == "GET":
        #gets names of all the parties
        rows = db.execute("SELECT partyName FROM parties")
        listOfParties = []

        #puts info into a list to send to the html page
        for row in rows:
            listOfParties.append(row["partyName"])
        return render_template("info.html",partyList=listOfParties)
    else:
        if not request.form.get("party") or request.form.get("party") == "0":
            return apology("Input a party!")

        #gets info of user and party
        partyInfo = db.execute("SELECT * FROM rsvp WHERE party_ID = (SELECT partyID FROM parties WHERE partyName = :name)", name = request.form.get("party"))


        party = {}
        #lets user know if no one has rsvpd
        if partyInfo == []:
            return apology("No one has RSVPd yet")

        #puts info into a list
        for row in partyInfo:
            aList = []
            name = db.execute("SELECT username FROM users WHERE userID = :id", id = row["attendee_ID"])
            aList.append(name[0]["username"])
            aList.append(row["offering"])
            party[aList[0]] = aList

        print(party)

        #returns a page with rsvp info
        return render_template("select.html", party = party)


@app.route("/parties")
@login_required
def parties():
    #json method to send a dictionary to a script in html
    return jsonify(session["parties"])


@app.route("/map")
@login_required
def map():
    #gets all info from parties
    partyInfo = db.execute("SELECT * FROM parties")

    parties = {}

    #puts said info into dictionary
    for row in partyInfo:
        if row["location"] not in parties:
            aList = []
            aList.append(1)
            x = coordinates(row["location"])
            aList.append(x[0])
            aList.append(x[1])
            parties[row["location"]] = aList

        else:
            parties[row["location"]][0] += 1

    #puts dictionary into a global variable
    session["parties"] = parties

    return render_template("map.html")

def coordinates(name):
    #this method essentially returns the coordinates of all the dorms in the yard
    coordinates = []
    if name == "Thayer" or name == "thayer":
        coordinates.append(42.375000)
        coordinates.append(-71.116766)
    elif name == "Canaday" or name == "canaday":
        coordinates.append(42.375457)
        coordinates.append(-71.115905)
    elif name == "Hollworthy" or name == "hollworthy":
        coordinates.append(42.375750)
        coordinates.append(-71.117192)
    elif name == "Stoughton" or name == "stoughton":
        coordinates.append(42.375440)
        coordinates.append(-71.117715)
    elif name == "Weld" or name == "weld":
        coordinates.append(42.373963)
        coordinates.append(-71.117117)
    elif name == "Hollis" or name == "hollis":
        coordinates.append(42.375060)
        coordinates.append(-71.117837)
    elif name == "Matthews" or name == "matthews":
        coordinates.append(42.374078)
        coordinates.append(-71.118132)
    else:
        coordinates.append(42.373650)
        coordinates.append(-71.117810)
    return coordinates


@app.route("/parties")
@login_required
def list(names):


    partyInfo = db.execute("SELECT partyName,time,location,spot,user_id FROM parties WHERE location = :name OR location = :otherName",name=names[0],otherName=names[1])

    parties = {}

    #this for loop places all information of the parties from a specfic house into a dictionary
    for row in partyInfo:
            aList = []
            aList.append(row["location"])
            aList.append(row["spot"])
            aList.append(row["time"])
            personName = db.execute("SELECT username FROM users WHERE userID = :user",user = row["user_id"])
            aList.append(personName[0]["username"])
            parties[row["partyName"]] = aList


    return render_template("parties.html",parties=parties)



#all of the routes bellow will show the parties in those dorms

@app.route("/stoughton")
@login_required
def stoughton():
    names=["stoughton","Stoughton"]
    return list(names)

@app.route("/thayer")
@login_required
def thayer():
    names=["thayer","Thayer"]
    return list(names)

@app.route("/grays")
@login_required
def grays():
    names=["grays","Grays"]
    return list(names)

@app.route("/weld")
@login_required
def weld():
    names=["weld","Weld"]
    return list(names)

@app.route("/matthews")
@login_required
def matthews():
    names=["matthews","Matthews"]
    return list(names)

@app.route("/hollworthy")
@login_required
def hollworthy():
    names = ["hollworthy","Hollworthy"]
    return list(names)

