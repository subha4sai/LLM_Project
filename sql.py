import sqlite3

## Connect to sqlite
connection=sqlite3.connect("D_TE_SAMPLE.db")

## Create a cursor object to insert record,Create table,retrieve
cursor=connection.cursor()

## Create the table 


## Insert Some more records



## Display all the records 

data=cursor.execute('''Select * from T_TE_SAMPLE_DATA''')

for row in data:
    print(row)

## Close the connection 

connection.commit()
connection.close()
