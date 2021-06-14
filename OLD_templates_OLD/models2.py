from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    kgCO2e_value = db.Column(db.Numeric, nullable=False)
    process_id = db.Column(db.Integer, db.ForeignKey("processes.id"), nullable=False)

class Process(db.Model):
    __tablename__ = "processes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    kgCO2e_value = db.Column(db.Numeric, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    

class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)


class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    ratings = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String, nullable=False)
    user_review = db.Column(db.String(25), nullable=False)
    book_review = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)


#########################################
# Emission Factors schemas:

class EF_Transportation(db.Model):
    __tablename__ = "ef_transportation"
    id = db.Column(db.Integer, primary_key=True)
    ef_id = db.Column(db.Integer, nullable=False)
    gas = db.Column(db.String, nullable=False)
    fuel = db.Column(db.String, nullable=False)
    vehicle = db.Column(db.String, nullable=False)
    technology = db.Column(db.String)
    value = db.Column(db.Numeric, nullable=False)
    unit = db.Column(db.String, nullable=False)
    

class EF_Electricity(db.Model):
    __tablename__ = "ef_electricity"
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, nullable=False)
    el_value = db.Column(db.Numeric, nullable=False)
    el_unit = db.Column(db.String, nullable=False)