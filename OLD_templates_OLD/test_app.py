import os
import requests
import simplejson as json
import serial

from flask import Flask, session, render_template, jsonify, request, redirect, url_for, flash
from flask_session import Session
from flask_sqlalchemy import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import *

from passlib.hash import sha256_crypt


app = Flask(__name__)

# Set the secret key to some random bytes.
# python3 -c 'import os; print(os.urandom(16))'
app.secret_key = b"\x04\x02\xd7 \xd4.\xb0\x9a\x08\xe4E\xe2\x91\x12i'"



# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


DATABASE_URL = 'sqlite:///EF_schema.db'

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))



@app.route("/", methods=["GET", "POST"])
def main():

    # Query for electricity EFs:
    ef_el_value = db.execute("SELECT country, el_value FROM ef_electricity").fetchall()

    # Create object for query
    da, nu = {}, [] # define a json object and a dict
    for rowproxy in ef_el_value:
    # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
        # build up the tuples
            da = {**da, **{column: value}}
        nu.append(da) # append json to the dict
        json_nu = json.dumps(nu)
    #print(nu)

    contents = ["On-site fuel use",
                "Fugitive Emission",
                "Purchased Energy",
                "Material Inputs",
                "Inbound Logistics",
                "Outbound Logistics",
                "Business Travel",
                "Employee Commuting",
                "Waste and Water",
                "Customer Apportionment",
                "Product Apportionment",
                "Results"]


    
    return render_template("main.html", nu=nu)



@app.route("/process_footprint", methods=["GET", "POST"])
def index():
    # Query for electricity EFs:
    ef_el_value = db.execute("SELECT country, el_value FROM ef_electricity").fetchall()

    # Create object for query
    da, nu = {}, [] # define a json object and a dict
    for rowproxy in ef_el_value:
    # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
        # build up the tuples
            da = {**da, **{column: value}}
        nu.append(da) # append json to the dict
        json_nu = json.dumps(nu)
    #print(nu)


    # Query for transportation EFs:
    ef_trans_value = db.execute("SELECT DISTINCT vehicle, fuel, technology, value FROM ef_transportation WHERE gas='CARBON DIOXIDE'").fetchall()
    print(ef_trans_value)

    da_trans, nu_trans = {}, [] # define a json object and a dict
    for rowproxy in ef_trans_value:
    # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
        # build up the tuples
            da_trans = {**da_trans, **{column: value}}
        nu_trans.append(da_trans) # append json to the dict

    print(nu_trans)


    return render_template("process_footprint.html", nu=nu, nu_trans=nu_trans)


@app.route("/getValue", methods=["GET", "POST"])
def getValue():
    # find the port on mac: " ls /dev/cu.usbmodem* "
    # uno = serial.Serial('/dev/cu.usbmodem1421', 115200)
    uno = serial.Serial('COM5', 115200)


    arduino_data1 = uno.readline().decode('ascii').split()
 
    for item in arduino_data1:
        arduino_data = float(item)

    print(arduino_data)
    #return render_template("main.html", arduino_data=arduino_data)
    return jsonify({"success": True, "rate": arduino_data})
    

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        secure_password = sha256_crypt.encrypt(str(password))

        if password == confirm:
            db.execute("INSERT INTO users(name,username,password) VALUES(:name,:username,:password)",
                            {"name":name,"username":username,"password":secure_password})
            db.commit()
            flash("you are registered and can login", "sucess")
            return redirect(url_for('login'))

        else:
            flash("password does not match", "danger")
            return render_template("register.html")

    return render_template("register.html")


#login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
     
        usernamedata = db.execute("SELECT username FROM users WHERE username=:username", {"username":session['username']}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username", {"username":session['username']}).fetchone()

        if usernamedata is None:
            flash("The username does not exist", "danger")
            return render_template("login.html")
        else:
            for password_data in passworddata:
                if sha256_crypt.verify(session['password'],password_data):
                    session["log"] = True
                    #cookies = request.cookies
                    #print(cookies)

                    flash("You are now logged in", "success")
                    return redirect(url_for('search'))
                else:
                    flash("Incorect username or password", "danger")
                    return render_template("login.html")

    else:
        return render_template("login.html")


#logout
@app.route("/logout")
def logout():
    session.pop('username', None)
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for('index'))


#after login
@app.route("/search", methods=["GET", "POST"])
def search():

    if not session.get('username') is None:

        search_value = request.form.get("search_string")
        #print(search_value)
        if search_value == '':
            return render_template('search.html', message='Please enter required fields')

        query = "SELECT * FROM books WHERE title ILIKE '%{}%'".format(search_value)
        titledata = db.execute(query).fetchall()
        return render_template("search.html", results=titledata)

    else:
        flash("You must be logged in to access this page", "danger")
        return redirect(url_for("login"))



@app.route("/search/<result_id>")
def details(result_id):
    # Search for a book by title of a book
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": result_id}).fetchone()
    
    isbn = book.isbn
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "pCA9kPipjgDPJpxSwIRBDA", "isbns": isbn})
    data=res.json()
    #print(data)

    nr_ratings = data["books"][0]['work_ratings_count']
    avg_rating = data["books"][0]['average_rating']

    return render_template("book.html", book=book, ratings=nr_ratings, avg_rating=avg_rating)



@app.route("/submit/<book_id>", methods=["POST"])
def submit(book_id):

        rating = request.form.get("ratings")
        comment = request.form.get("comments")
        sesion_var = session['username']

        if rating == '' or comment == '':
            #return render_template('search.html', message='Please enter required fields')
            flash("Please enter required fields", "danger")

        user_cookie = db.execute("SELECT * FROM reviews WHERE user_review = :sesion_var AND book_review = :book_review", {"sesion_var": sesion_var, "book_review":book_id}).fetchone()

        if user_cookie is None:
            # Add review
            db.execute("INSERT INTO reviews (ratings, comments, user_review, book_review) VALUES (:rating, :comment, :user_review, :book_review)", 
                    {"rating": rating, "comment":comment, "user_review":sesion_var, "book_review":book_id})
            print(f"Added comment: {comment} and rating: {rating} for user {sesion_var}")
            db.commit()
        else:
            flash("You have already submitted a review for this book", "danger")
        
        #return render_template("book.html", book=book, ratings=nr_ratings, avg_rating=avg_rating, commentary=comment)
        return redirect(url_for('details', result_id=book_id, commentary=comment))



#@app.route("/books")
#def booklist():
#    """List all flights."""
#    book_list = db.execute("SELECT * FROM books LIMIT 10").fetchall()
#   return render_template("books.html", books=book_list)


@app.route("/books/<int:book_id>")
def book(book_id):
    """List details about a single book."""

    if not session.get('username') is None:

        # Make sure book exists.
        book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        if book is None:
            return render_template("error.html", message="No such book.")

        return render_template("book.html", book=book)
    else:

        flash("Please login first", "danger")
        return redirect(url_for("login"))


if __name__ == '__main__':
    app.debug = True
    app.run()

#     export DATABASE_URL=postgres://khxxfluukbyqoh:1084ea7b53f5ce4fdbdef299f6c0fc5f334adc6d9d3400e3761b43bf93878c8e@ec2-54-75-246-118.eu-west-1.compute.amazonaws.com:5432/d62ujht21ufg6u
