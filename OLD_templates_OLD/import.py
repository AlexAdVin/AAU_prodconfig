import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader)              # skips the top line
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES(:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author":author, "year":int(year)})
        print(f"Added book with isbn: {isbn}, title:{title}, author:{author} and year:{year} into the database.")
    db.commit()

if __name__ == "__main__":
    main()