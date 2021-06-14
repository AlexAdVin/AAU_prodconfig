import sqlite3
import pandas as pd
from sqlalchemy import create_engine

EF = {}

myfile = "new_Transport_EF_DB.xlsx"
output = 'Transport_EF_DB.xlsx'

engine = create_engine('sqlite://', echo=False) #stored in RAM

dataframe = pd.read_excel(myfile, sheet_name='Sheet1')

#g = dataframe.groupby(['Description', 'Fuel 2006'])

#for name, group in g:
#        print(name)
#        print(group)

# Specific value type
# dataframe['Value']=dataframe['Value'].astype('float64')

dataframe.to_sql('EF_Transport', engine, if_exists='replace', index=False)

results = engine.execute("SELECT * FROM EF_Transport WHERE Unit = 'g/km' \
        AND IPCC_2006_Source_Sink_Category = '1.A.3.b - Road Transportation' \
        GROUP BY 'Gas'")

final=pd.DataFrame(results, columns=dataframe.columns)
final.to_excel(output, index=False)

print(final)