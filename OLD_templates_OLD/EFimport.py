import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("./EF_DB/Transport_EF_DB.csv")
    reader = csv.reader(f)
    next(reader)              # skips the top line
    for ef_id,gas,fuel,vehicle,technology,value,unit in reader:
        db.execute("INSERT INTO ef_transportation (ef_id,gas,fuel,vehicle,technology,value,unit) VALUES(:ef_id, :gas, :fuel, :vehicle, :technology, :value, :unit)",
                    {"ef_id": ef_id, "gas": gas, "fuel":fuel, "vehicle":vehicle, "technology":technology, "value":value, "unit":unit})
        print(f"Added item with gas: {gas}, fuel:{fuel}, vehicle:{vehicle} and value:{value} into the database.")
    db.commit()

if __name__ == "__main__":
    main()

