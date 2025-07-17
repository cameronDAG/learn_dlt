import pandas as pd
import pymysql
from pandas.tseries.offsets import MonthEnd

#connect ke server MySQL
conn =  pymysql.connect( 
    host="localhost",
    user="root",
    password="1234",
    database="database"
)

#membuat tabel
cursor = conn.cursor()

create_table_hasil = """
CREATE TABLE IF NOT EXISTS occupancy_apartment(
    apartment_id varchar(10),
    month char(2),
    occupancy_rate float(10,5)
);
"""
cursor.execute(create_table_hasil)
conn.commit()

#mengambil data dari booking_apartment untuk dianalisa
query = "SELECT apartment_id,room_id,user_id,start_date,end_date FROM booking_apartment"
data = pd.read_sql(query, conn)
print(data)

#memisahkan data yang bulannya overlapping
def split_rows_by_month(data):
    expanded_rows = []

    for _, row in data.iterrows():
        start = row['start_date']
        end = row['end_date']
        current_start = start
        current_start = pd.Timestamp(current_start)
        end = pd.Timestamp(end)

        while current_start <= end:
            # Get end of the current month or actual end date
            current_end = min(end, current_start + MonthEnd(0))
            expanded_rows.append({
                'apartment_id': row['apartment_id'],
                'room_id': row['room_id'],
                'user_id': row['user_id'],
                'start_date': current_start,
                'end_date': current_end
            })
            current_start = current_end + pd.Timedelta(days=1)

    return pd.DataFrame(expanded_rows)

data = split_rows_by_month(data)

#menambahkan kolom month
data['month'] = data['start_date'].dt.month

#mencari jumlah hari unit dibooking
data['day_booked'] = (data['end_date'] - data['start_date']).dt.days + 1

#mencari jumlah occupancy rate setiap unit
grouped = data.groupby(['apartment_id', 'room_id', 'month'])['day_booked'].sum().reset_index()
grouped['occupancy_rate'] = grouped['day_booked']/30

#mencari rata-rata occupancy rate setiap apartment perbulannya
final_occupancy_rate = grouped.groupby(['apartment_id','month'])['occupancy_rate'].mean().reset_index()

#memasukkan hasil analisis ke dalam database
insert_final_occupancy = "INSERT INTO occupancy_apartment(apartment_id,month,occupancy_rate) VALUES(%s,%s,%s);"

for _, r in final_occupancy_rate.iterrows():
    
    cursor.execute(insert_final_occupancy, (
        r['apartment_id'], str(int(r['month'])), r['occupancy_rate']
    ))

conn.commit()
conn.close()