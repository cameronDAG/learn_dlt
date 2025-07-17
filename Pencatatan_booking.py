import pandas as pd
from datetime import datetime
from pandas.tseries.offsets import MonthEnd
import pymysql

#connect ke server MySQL
conn =  pymysql.connect( 
    host="localhost",
    user="root",
    password="1234",
    database="database"
)

#membuat table
cursor = conn.cursor()
create_table = """
CREATE TABLE IF NOT EXISTS booking_apartment(
    apartment_id varchar(10),
    room_id varchar(10),
    user_id varchar(10),
    start_date date,
    end_date date
);
"""

cursor.execute(create_table)
conn.commit()

#load data dari csv
data_awal = pd.read_csv(r"BelajarDLT/booking apartment.csv")

#ganti data type supaya perbedaan hari bisa diitung
data_awal['start_date'] = pd.to_datetime(data_awal['start_date']) 
data_awal['end_date'] = pd.to_datetime(data_awal['end_date'])

#insert data ke table booking_apartment
insert_data_awal = "INSERT INTO booking_apartment(apartment_id,room_id,user_id,start_date,end_date) VALUES(%s,%s,%s,%s,%s);"

for _, r in data_awal.iterrows():
    cursor.execute(insert_data_awal, (
        r['apartment_id'], r['room_id'], r['user_id'], r['start_date'], r['end_date']
    ))

conn.commit()
conn.close()