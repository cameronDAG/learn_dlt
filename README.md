# Apartment occupancy rate calculator
Aplikasi untuk menghitung occupancy rate masing-masing apartemen per-bulan dan menyimpan datanya ke dalam 
database MySQL.

[Fitur](##Fitur)

[Instalasi](##Instalasi)

[Cara Kerja Aplikasi](#cara-kerja-aplikasi)

[Changes](#changes)

## Fitur
- Menghitung Occupancy Rate perbulan
- Mencatat data ke MySQL

## Instalasi
1. Pastikan Python sudah terinstall

2. Pastikan MySQL sudah terinstall

3. Lakukan intalasi library berikut di Python:
- pandas
- datetime
- MonthEnd
- pymysql

4. Lakukan cloning git repository dengan
```bash
git clone https://github.com/CammyVictoria/BelajarDLT
```
## Cara Kerja Aplikasi
### Step 1 - Menghubungkan koneksi ke database
set up koneksi ke database dengan konfigurasi berikut:
```python
conn =  pymysql.connect( 
    host="localhost",
    user="root",
    password="password",
    database="database"
)
```
konfigurasi tersebut dapat diubah sesuai dengan kebutuhan

### Step 2 - Membuat table untuk pencatatan raw data booking apartment
Jalankan query SQL untuk membuat tabel tersebut, berikut contoh dari code untuk membuat tabel booking_apartment
```python
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
```

### Step 3 - load data dari csv menggunakan pandas
pada step ini, data dari booking apartment.csv diload ke python menggunakan library pandas
```python
data_awal = pd.read_csv(r"booking apartment.csv") 
``` 

### Step 4 - pastikan kolom start_date dan end_date sudah menjadi bentuk datetime
hal ini dilakukan agar data lebih mudah diolah
```python
data_awal['start_date'] = pd.to_datetime(data_awal['start_date'])
data_awal['end_date'] = pd.to_datetime(data_awal['end_date'])
```

### Step 5 - Melakukan eksekusi input data booking apartment ke dalam tabel database
Memasukkan data awal ke dalam database MySQL
```python
insert_data_awal = "INSERT INTO booking_apartment(apartment_id,room_id,user_id,start_date,end_date) VALUES(%s,%s,%s,%s,%s);"
for _, r in data_awal.iterrows():
    cursor.execute(insert_data_awal, (
        r['apartment_id'], r['room_id'], r['user_id'], r['start_date'], r['end_date']
    ))
```
### Step 6 - Membuat table untuk pencatatan data hasil analisis occupancy rate
Jalankan query SQL untuk membuat tabel tersebut, berikut contoh dari code untuk membuat tabel booking_apartment
```python
create_table_hasil = """
CREATE TABLE IF NOT EXISTS occupancy_apartment(
    apartment_id varchar(10),
    month char(2),
    occupancy_rate float(10,5)
);
"""
```

### Step 7 - mengambil data booking apartment dari database untuk dianalisa
```python
query = "SELECT apartment_id,room_id,user_id,start_date,end_date FROM booking_apartment"
data = pd.read_sql(query, conn)
```

### Step 8 - pisahkan pemesanan yang bersifat overlapping pada setiap bulan 
contoh: kalau ada 1 row pemesanan dengan
start_date 20 Juni dan end_date 10 Juli, maka dipisah menjadi 2 rows:
rows 1: start_date = 20 Juni, end_date = 30 Juni
rows 2: start_date = 1 Juli, end_date= 10 Juli
```python
def split_rows_by_month(data_awal):
        expanded_rows = []

        for _, row in data_awal.iterrows():
            start = row['start_date']
            end = row['end_date']
            current_start = start

            while current_start <= end:
    ...
```

### Step 9 - hitung perbedaan start_date dan end_date untuk mengetahui berapa hari hotel dibooking
Mengetahui berapa lama hotel ditempati (dalam hitungan hari)
```python
data['day_booked'] = (data['end_date'] - data['start_date']).dt.days + 1
```

### Step 10 - hitung jumlah total unit apartment dibooking setiap bulannya dan bagi dengan 30 (jumlah hari perbulan)
Dilakukan untuk mengetahui occupancy rate setiap unit
```python
grouped = data.groupby(['apartment_id', 'room_id', 'month'])['day_booked'].sum().reset_index()

grouped['occupancy_rate'] = grouped['day_booked']/30
```

### Step 11 - hitung occupancy rate dengan mencari mean dari kolom occupancy_rate untuk setiap apartment di bulan tertentu
Mencari tahu rata-rata occupancy rate setiap hotel perbulan
```python
final_occupancy_rate = grouped.groupby(['apartment_id','month'])['occupancy_rate'].mean()reset_index()
```

### Step 12 - Melakukan eksekusi input data occupancy rate ke dalam tabel database
Memasukkan data hasil analisis ke dalam database MySQL
```python
insert_final_occupancy = "INSERT INTO occupancy_apartment(apartment_id,month,occupancy_rate) VALUES(%s,%s,%s);"

for _, r in final_occupancy_rate.iterrows():

    cursor.execute(insert_final_occupancy, (
        r['apartment_id'], str(int(r['month'])), r['occupancy_rate']
    ))
```
## Edge Case
### Terjadi pembaruan data
#### Metode 1 - scd2 (Slowly Changing Dimensions Type 2)
Pada metode ini, data historikal akan ditambahkan sebagai rows baru dan tidak dihapus.

Untuk menggunakan metode ini, pada setiap tabel ditambahkan kolom baru, yaitu surrogate_key, effective_start_date, effective_end_date, dan active_flag

- surrogate_key = Memberikan id untuk setiap versi data
- effective_start_date = Tanggal efektif data tersebut mulai berlaku
- effective_end_date = Tanggal data tersebut terakhir kali berlaku
- active_flag = Status berlakunya data tersebut (bisa Y/N atau 1/0)

Contoh:
Terdapat tabel employee yang mencakup data sebagai berikut:
```
|surrogate_key|emp_id|emp_name|emp_address|effective_start_date|effective_end_date|active_flag|
|S0001        |E0001 |Agus    |Indonesia  |07/08/2025          |12/31/9999        |Y          |
```
Lalu employee tersebut ingin mengganti alamatnya, maka data dengan surrogate_key S0001 tidak akan dihapus, hanya saja effective_end_date dan active_flagnya berubah menjadi seperti berikut:

```
|surrogate_key|emp_id|emp_name|emp_address|effective_start_date|effective_end_date|active_flag|
|S0001        |E0001 |Agus    |Indonesia  |07/08/2025          |07/10/2025        |N          |
|S0002        |E0001 |Agus    |USA        |07/10/2025          |12/31/9999        |Y          |
```

#### Metode 2 - Compare Table
Membandingkan data di table staging dan di dalam table database yang telah disimpan untuk mengetahui apakah terjadi perubahan data. Di MySQL, bisa dijalankan query sebagai berikut.

```SQL
(SELECT column_1, column_2, 'staging' AS source
FROM staging_table
EXCEPT                                                  --Menemukan data yang ditambahkan
SELECT column_1, column_2, 'staging' AS source
FROM old_table)
UNION ALL
(SELECT column_1, column_2, 'old' AS source
FROM old_table
EXCEPT                                                  --Menemukan data yang dikurangi
SELECT column_1, column_2, 'old' AS source
FROM staging_table)
```

### Terjadi Penambahan/Pengurangan/Perubahan Kolom
Apabila perubahan terjadi pada struktur tabel, bisa diatasi juga menggunakan konsep metode berikut:
[Compare Table](#metode-2---compare-table)

#### Case 1 - Penambahan kolom
```SQL
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'old_table'
EXCEPT
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'staging_table'
```

#### Case 2 - Pengurangan kolom
```SQL
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'staging_table'
EXCEPT
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'old_table'
```

#### Case 3 - Pergantian nama kolom
Membandingkan data yang tersimpan di dalam kolom database untuk memastikan bahwa benar kolom tersebut merupakan kolom yang diganti namanya. Contoh: Kolom user_name berubah nama menjadi name, maka bisa dicek melalui query berikut
```SQL
SELECT COUNT(*) as diff_count
FROM old_table o
JOIN staging_table s
ON o.user_id = s.user_id
WHERE o.user_name != s.name
```
Apabila jumlah diff_count 0 atau mendekati 0, kemungkinan besar sudah benar bahwa kolom tersebut merupakan kolom yang namanya diganti.

## Changes
### Version 1
1. algoritma transformasi data di database.py diubah menjadi fungsi transforming()
2. Membuat variabel baru untuk data awal agar data awal dapat disimpan di dalam database
ke dalam tabel
2. Menghubungkan dengan server mysql menggunakan library pymysql
3. Membuat tabel booking_apartment untuk menyimpan data awal
4. Membuat tabel occupancy_apartment untuk menyimpan hasil perhitungan occupancy rate

### Version 2
1. memisahkan proses untuk melakukan transfer raw data ke dalam MySQL (Pencatatan_booking.py) dan proses untuk menganalisa hasil occupancy rate (Analisa_occupancy_rate.py)
2. menghapus file booking.py dan database.py karena prosesnya sudah disimpan pada Pencatatan_booking.py dan Analisa_occupancy_rate.py

### Version 3
1. Penambahan file query.sql, sebuah file sql yang ketika dijalankan akan menghitung langsung occupancy_rate tanpa harus melalui logika python.

# Linux File Permission

## 1. Cara Mengecek Permission File

Gunakan perintah berikut di terminal:
```bash
ls -l
```
## 2. Struktur
```
rwxrw-r–
```

3 huruf pertama: permission buat user (yang buat file)
3 huruf tengah: permission buat grup
3 huruf terakhir: permission buat other member

r = baca
w = nulis/ubah
x = menjalankan

## 3. Cara mengubah akses
### Cara pertama
```
chmod [kode] [nama-file]
```
### Cara Kedua
```
chmod [user][+/-/=][tipe akses]
```
# Cron
## Cara memanggil
crontab -e

## Cara menyetel
strukturnya akan seperti ini

```
minute hour day month weekday <command-to-execute>
```

### Contoh
1. jalan setiap hari, setiap bulan, setiap jam 5
```
15 * * * * command
```

2. jalan setiap jam 5.30pm di hari jumat
```
30 17 * * 5 command
```

3. jalan setiap waktu kerja(jam 9-5, senin-jumat)
```
0 9-17 * * 1-5 command
```

4. jalan setiap interval 2 jam
```
0 */2 * * * command
```
# Piping dan Redirection
## Piping
Piping biasa ditandai dengan simbol | dan digunakan untuk mengalirkan output dari 1 perintah sebagai input untuk perintah lainnya.

contoh:
```bash
ls | sort
```

maka program akan mengambil semua directory yang ada terlebih dahulu sebelum melakukan sorting.

## Redirection
Digunakan untuk mengarahkan input dan output dari suatu perintah.

```bash
ls -a > contents.txt
```

- '>' mengarahkan output ke suatu file/perintah
- '<' mengarahkan input ke suatu perintah
- '>>' mengarahkan output ke suatu file/perintah dan memasukkan output ke baris baru apabila filenya sudah memiliki isi
- '2>' mengarahkan hasil error ke suatu file/perintah
- '2>>' mengarahkan hasil error ke suatu file/perintah dan memasukkan error message ke baris baru apabila filenya sudah memiliki isi
- '&>' mengarahkan output dan error ke suatu file/perintah
- '&>>' mengarahkan output dan error dan menambahkan baris baru apabila file sudah memiliki isi

# Data Orchestration and Data Scheduler
Data orchestration merupakan proses pembuatan sebuah flow data dalam data environment secara otomatis.

Data orchestration tools biasanya memiliki fungsi sebagai berikut:
1. Scheduling: Menjadwalkan kapan sebuah proses akan dijalankan
2. Dependency management: Menentukan urutan eksekusi
3. Monitoring and retry: Memantau workflow, memberikan notifikasi error, dan otomatis retry
4. Logging and debugging: Menyediakan log untuk analisis kesalahan

Workflow data biasanya divisualisasikan sebagai DAG (Directed Acyclic Graph), dimana setiap task merupakan node yang akan menunjuk ke node lainnya sebagai task yang akan dilakukan selanjutnya.

## Tipe Workflow
### Task-Centric
Motto: "Jalankan tugas ini"

### Asset-Centric
Motto: 

## Tools
### Airflow
Apache airflow merupakan sebuah tools open-sources untuk mejadwalkan and memonitor kegiatan workflow.

#### Konsep dasar Airflow
1. Task: Proses yang akan dijalankan
2. Task Instances: Status dari task (running,success,failed)
3. DAG (Directed Acyclic Graph)
4. DAG run: Eksekusi individual masing-masing node DAG

### Dagster
#### Konsep dasar Dagster
1. op: Unit kerja terkecil
2. graph: Rangkaian op yang saling terhubung
3. job: Eksekusi dari garph dan penjadwalannya
4. asset: Reprensentasi data sebagai "produk" yang dihasilkan dan digunakan
5. schedule/sensor: Untuk memastikan kapan job akan berjalan

##### Asset
Merepresentasikan sumber data yang terdapat di dalam pipeline.
Snippet:
```python
@dg.asset()
def duckdb_table(
    context: dg.AssetExecutionContext,
    database: DuckDBResource,
    import_file,
):
    table_name = "raw_data"
    with database.get_connection() as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                date DATE,
                share_price FLOAT,
                amount FLOAT,
                spend FLOAT,
                shift FLOAT,
                spread FLOAT
            )
        """)
        conn.execute(f"COPY {table_name} FROM '{import_file}';")
```

##### Asset check
Digunakan untuk memvalidasi data dalam suatu asset
Snippet:
```python
@dg.asset_check(
    asset=import_file,
    blocking=True,
    description="Ensure file contains no zero value shares",
)
def not_empty(
    context: dg.AssetCheckExecutionContext,
    import_file,
) -> dg.AssetCheckResult:
    with open(import_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        data = (row for row in reader)

        for row in data:
            if float(row["share_price"]) <= 0:
                return dg.AssetCheckResult(
                    passed=False,
                    metadata={"'share' is below 0": row},
                )

    return dg.AssetCheckResult(
        passed=True,
    )
```

kode tersebut digunakan untuk mengecek apakah terdapat value null pada kolom share_price

##### Definitions
Digunakan untuk menyatakan dan menghubungkan segala aspek dalam dag, seperti asset, resource, sensor, job, dll.
Snippet:
```python
@dg.definitions
def my_definitions():
    return dg.Definitions(
        assets=[import_file, duckdb_table],
        resources=get_resources()
    )

```