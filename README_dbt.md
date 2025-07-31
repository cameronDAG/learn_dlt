# Model
disimpan dalam bentuk file sql yang berisi query untuk transformasi data sesuai yang dibutuhkan.

Di dalam DBT, sudah disediakan folder bernama models. Apabila ingin membuat models baru, bisa langsung create file sql baru di dalam foldernya saja. Dan diatur di dalam file .yml atau di dalam file tersebut, configurationnya biasa diatur menggunakan bahasa jinja.

## Cara kerja
Apabila terdapat model yang dimaterialisasi, lalu terdapat perubahan dalam model, dan model dimaterialisasi lagi, maka yang terjadi adalah:

1. DBT mengecek apakah terdapat perubahan terhadap model yang baru dijalankan
2. Model yang lama dihapus, lalu diganti dengan isi model yang baru

## Ref function
Buat select dari model lain yang sudah dibuat

## Compile
Memberi tahu kode lengkap sql nya. Misal kita memakai fungsi ref di salah satu model, apabila kita compile, akan ketahuan isi query penuhnya apabila dijalankan.

## Fact vs Dimension models
Fact: Sesuatu yang terjadi (pembelian yang terjadi pada tanggal sekian)
Dimension: Penjelasan akan suatu konteks (user yang tinggal di daerah tertentu)

## File management
Model .sql sebaiknya dipisahkan di folder-folder sesuai dengan kegunaannya masing-masing untuk memudahkan configuration dan materialization

# Source
Deklarasi sumber datanya darimana

## Freshness
Memastikan kapan data terupdate
```
version: 2

sources:
  - name: raw
    tables:
      - name: customers
        freshness:
          warn_after: { count: 1, period: hour }
          error_after: { count: 2, period: hour }

```

warn_after: memberi notifikasi kalau data terakhir kali diupdate 1 jam yang lalu
error_after: jadikan sebagai error kalau terakhir kali data diupdate adalah 2 jam yang lalu

# Test
## Generic testing
pake file .yml
1. unique
2. not null
3. relationships
4. accepted_value

Kalau dijalankan, akan memberikan list row yang melanggar ketentuan tersebut dalam bentuk view

## Singular testing
pake file .sql
nantinya di declare syntax sql yang diperlukan untuk test (misal syntax buat mastiin kalau semua payment nggak ada yang minus)

## dbt test vs run vs build
1. test: validasi apakah isi kolom sudah sesuai
2. run: materialisasi model
3. build: materialisasi model, kemudian menjalankan test

# Documentation
Disimpan dalam bentuk .yml, caranya adalah dengan memberikan keterangan description untuk model yang dituju. Dijalankan dengan dbt docs generate

## doc blocks
Digunakan apabila dokumentasi sebuah model terlalu panjang, disimpan dalam bentuk file .md. Nantinya tinggal di panggil saja menggunakan fungsi doc

# Deployment
Menjalankan dbt secara terjadwal di lingkungan produksi.

## Cara membuat lingkungan deployment
1. General Settings: Pilih versi dbt dan branch yang digunaka
2. Data Warehouse Connection: Konfigurasi koneksi ke warehouse, bisa memilih warehouse khusus untuk produksi.
3. Masukkan credential yang dibutuhkan

## Job
Berfungsi dalam menjalankan perintah dbt sesuai penjadwalannya.

# Refactoring SQL for Modularity
Table yang mau digunakan sebaiknya jadikan source

## CTE grouping
Struktur:
1. Import CTE
2. Staging
3. Logical CTE
4. Final CTE

Intinya:
- Gunakan CTE (WITH) untuk setiap transformasi logis.
- Kelompokkan per bagian: source → filtering → transformation → output.
- Hindari SELECT *, beri alias yang jelas.

## Centralized Logic in Staging Table
Intinya:
- 1:1 mapping dari tabel raw.
- Rename field agar konsisten.
- Lakukan type casting dan basic cleanup di sini.

## Intermediate model
Intinya:
- Join antar staging.
- Hitung kolom turunan.
- Pisahkan dari final model untuk modularitas.

## Final model
Intinya:
- Fokus pada satu business use case.
- Gabungkan intermediate & staging jika perlu.

## Audit
Intinya:
- Tambahkan tests di schema.yml: not_null, unique, relationships
- Bisa juga buat audit model yang cek data kualitas (e.g. duplicate, null count, unexpected value).

# Materialization
Tipe:
1. Table
``` 
{{ config(
    materialized='table'
)}}
```
2. View
```
{{ config(
    materialized='view'
)}}
```
3. Ephemeral
```
{{ config(
    materialized='ephemeral'
)}}
```
# Incremental model
```
{{
    config(
        materialized='incremental'
    )
}}

select * from {{ ref('example_model') }}
{% if is_incremental() %}
where 
updated_at >= (select max(updated_at) from {{this}} 
{% endif %}
```

## Strategy
1. Append: menambahkan kolom baru ke dalam tabel tanpa mengecek duplikat
2. Merge: mengecek primary key, apabila primary key yang dicek ada di dalam tabel, maka update row. Kalau tidak ada, menambahkan row baru
3. Delete+Insert: menghapus data yang primary keynya sudah ada di dalam penyimpanan dan memasukkan data yang baru
4. Insert Overwrite: melakukan replace data untuk seluruh partisi
5. Microbatch: membagi proses loading incremental model berdasarkan satuan waktu tertentu

## Schema change
Apabila terjadi perubahan pada schema, incremental model dapat mencantumkan value dalam on_schema_change sebagai berikut:

1. ignore: mengabaikan perubahan skema
2. fail: apabila terdapat perubahan dalam skema, proses run akan digagalkan
3. append_new_column: menambahkan kolom baru ke tabel target, tapi tidak update kolom yang sudah ada
4. sync_all_column: sinkronkan seluruh skema (kolom baru ditambah, tipe yang berubah diubah juga, dll)

# Snapshot
Command: dbt snapshot

Run pertama: membuat tabel dengan tambahan kolom: dbt_scd_id, dbt_updated_at, dbt_valid_from, and dbt_valid_to

Run Selanjutnya: Menambahkan baris record baru

## Strategy
1. Timestamp Strategy : melihat perubahan di kolom updated_at
2. Check Strategy : untuk table yang tidak memiliki kolom updated_at

# Analyses and Seeds

1. Analyses: file .sql yang berisi query untuk keperluan analisis yang tidak akan ter-materialize
2. Seeds: file .csv yang isinya diload ke dalam database

# Exposures
Dokumentasi bagaimana data digunakan di downstream
```
exposures:
  - name: orders_data
    label: orders_data
    type: notebook
    maturity: high
    url: https://tinyurl.com/jaffle-shop-reporting
    description: 'Exposure for orders data'
    depends_on:
      - ref('fct_orders')
    owner:
      name: Michael McData
      email: data@jaffleshop.com
```

# State
konsep ini memungkinkan dbt untuk tidak perlu menjalankan kembali semua model dari awal apabila terjadi model yang gagal.

# dbt retry
eksekusi command dari titik kegagalan terakhir

# dbt mesh
strategi arsitektur untuk membagi proyek dbt besar menjadi beberapa proyek kecil (modular), tapi tetap bisa saling terhubung satu sama lain.

## Model Contract
dideklarasikan untuk memastikan tipe data dan bentuk table.

```
models:
  - name: model_name
    config:
      contract:
        enforced: true
    columns:
      - name: column_name
        data_type: int
        constraints:
          - type: not_null
      - name: another_column_name
        data_type: string
      ...
```

## Model Version
Cara membuat: buat file .sql baru yang format namanya seperti ini
```
model_v2.sql
```

tambahkan keterangan version juga di dalam file .yml

1. Inlcude
2. Exclude
3. Old column configs

```
models:
  - name: file_name
    latest_version: 2 #you can specify any version as the latest version
    columns:
      - name: column_name
        data_type: its_data_type
     - name: a_different_column_name
         data_type: that_columns_data_type
    versions:
      - v: 2
      - v: 1
        defined_in: file_name_v1
        config:
          alias: file_name
        columns:
          - include: *
            exclude: a_different_column_name
          - name: a_different_column_name
            data_type: that_columns_data_type
```

# Group and Access Modifiers
1. Group: Kumpulan beberapa resources yang dapat diakses atau dimiliki oleh sekelompok orang tertentu
```
groups:
  - name: finance_group
    owner:
      name: Person’s Name
      email: TheirEmail@email.com
  - name: Marketing 
    owner:
      name: Marketing Group
      email: marketing@jaffle.com
```

2. Access: Punya 3 jenis, yaitu Public, Protected (bisa diakses oleh orang dalam project), dan Private (hanya bisa diakses orang dalam group)

# Advanced testing
## What to test
1. Test Isi & Struktur dari Satu Objek Database
Memastikan kolom dan struktur tabel sesuai ekspektasi.

2. Test Hubungan Antar Tabel
Memastikan data terkait satu sama lain dengan benar, misalnya foreign key yang valid.

3. Test Logika Bisnis Khusus
Gunakan singular test saat validasi yang kamu perlukan terlalu spesifik untuk generic test.

4. Test Freshness dari Source
Cek apakah data yang masuk ke pipeline kita masih segar.

## When to test
1. Pada saat mengubah atau menambahkan kode DBT
2. Pada saat data di-deploy ke production
3. Pada saat melakukan pull request
4. pada saat code masih di QA branch dan belum dimerge ke main branch

## Testing Command
```
dbt test --select nama_test
```
Supaya tidak perlu melakukan semua test yang ada di dalam repository

Atau biasanya lebih baik melakukan dbt build saja

## Storing test failures in the database
Menyimpan hasil data yang tidak memenuhi kriteria testing dalam database yang nantinya bisa dipanggil lagi menggunakan query
```
  - not_null:
      column_name: customer_id
      store_failures: true
```

hasil:
```
dbt_test__not_null_orders_customer_id_d38f03e2
```

Hasil tersebut dapat dipanggil dengan menjalankan
```
select * from analytics.dbt_test__audit.dbt_test__not_null_orders_customer_id_d38f03e2;
```

## Custom generic test
```
{% test average_dollars_spent_greater_than_one( model, column_name, group_by_column) %}

select 
    {{ group_by_column }},
    avg( {{ column_name }} ) as average_amount

from {{ model }}
group by 1
having average_amount < 1


{% endtest %}
```
Supaya bisa disebut di dalam file .yml kayak generic test. Untuk reusability

## Overwriting native test
Kalau dibuat custom generic test yang namanya sama kayak generic test (uniqu, not null, relationships, accepted_values), maka ketika test dijalankan akan mengikuti logika test yang baru dibuat.

## DBT Utils dan DBT Expectations
sebuah package yang menyiapkan fungsi testing yang cukup beragam.

## Audit Helper
Package untuk membandingkan dua tabel dalam keperluan auditing dan validasi data.

# DBT dan dagster
Models dalam dbt dapat menjadi asset di dagster menggunakan @dbt_asset. Ketika proses materialize dalam dagster dijalankan, asset-asset yang berasal dari dbt dianggap menjadi satu proses. Hal ini dikarenakan dalam dbt, kita biasa menjalankan dbt run atau dbt build untuk semua modelnya sekaligus.


# Dokumentasi
## Setting dbt untuk connect ke snowflake
Tanggal dilakukan: 22 Juli 2025


### Membuat akun snowflake dengan region MIDDLE EAST CENTRAL
Mengikuti step yang diberikan pada course dbt fundamentals untuk menyambungkan akun dbt ke snowflake

Masalah yang terjadi:
1. Tidak tersedia partner connect dari snowflake ke dbt untuk region tersebut.

Solusi:
1. Membuat akun snowflake baru dengan region berbeda(US EAST 4)

### Membuat akun snowflake baru dengan region US EAST 4
Masalah yang terjadi:
Tidak ada

## Membuat pipeline dlt
Tanggal dilakukan: 29 Juli 2025

### Mencoba mendapatkan data dari API yang diberikan
Pada step ini, dilakukan perancangan fungsi dekorator @resource untuk mengambil data dari API properties dan subscriptions

``` python
@dlt.resource(name="properties", write_disposition="replace", table_name="property_list")
def get_properties():
    page = 1
    while True:
        response = requests.get(
            f"{BASE_URL}/api/properties",
            headers={"X-API-Key": API_KEY},
            params={"page": page, "limit": 10, "city": "Jakarta"},
            verify=False
        )
        raw = response.json()
        items = raw.get("data", {}).get("data", [])
        print(f"Page {page} - {len(items)} records")
        if not items:
            break
        yield items
        page += 1
```
### Melakukan pengetesan dengan cara menjadikan duckdb sebagai destination terlebih dahulu
Dari step ini, didapatkan file properties_pipeline.duckdb yang ketika dicek menggunakan dbeaver, isi filenya sudah sesuai dengan API yang di-return.


## Membuat directory file untuk dagster
Tanggal dilakukan: 29 Juli 2025 - 30 Juli 2025

### Membuat directory dengan ```dg project scaffold --name my_project```

Masalah yang terjadi:
1. dagster dev harus dijalankan dengan menunjuk nama project (dagster dev -m my_project)
2. Definition tidak dapat memanggil seluruh asset sehingga menyebabkan error "no assets, no jobs, no definitions found"

Solusi:
1. Membuat directory baru dengan ```uvx -U create-dagster project my-project```

### Membuat directory dengan ```uvx -U create-dagster project my-project```
Pada saat command line tersebut dijalankan, terbentuk sebuah directory seperti berikut
```
.
└── my-project
   ├── pyproject.toml
   ├── src
   │   └── my_project
   │       ├── __init__.py
   │       ├── definitions.py
   │       └── defs
   │           └── __init__.py
   ├── tests
   │   └── __init__.py
   └── uv.lock
```

lalu, ditambahkan file assets ke dalam directory tersebut secara manual untuk menyimpan asset-asset yang tersedia. File python asset pertama dinamakan kos.py yang menyimpan asset dagster untuk memanggil fungsi dlt yang dibuat. Directory akhir akan menjadi seperti ini

```
.
└── my-project
   ├── pyproject.toml
   ├── src
   │   └── my_project
   │       ├── __init__.py
   │       ├── definitions.py
   │       └── defs
   │       |  └── __init__.py
   |       └── assets
   │       |  └── kos.py
   ├── tests
   │   └── __init__.py
   └── uv.lock
   ├── .dlt
   │   └── config.toml
   │   └── secrets.toml
   ├── dlt_pipeline
   │   └── kos_pipeline.py
   ```
  
  Masalah yang terjadi:
1. Ketika file kos_pipeline.py dipindahkan dalam directory tersebut pada dalam kondisi destinationnya masih duckDB, filenya masih mengarah ke directory yang lama.
Misal: seharusnya file berada dalam ```~/my_project/properties_pipeline.duckdb```, namun file masih disimpan ke dalam ```~/learn_dlt/properties_pipeline.duckdb```

Solusi:
1. Mengubah nama pipeline
  - properties_pipeline -> properties
  - subscriptions_pipeline -> subscriptions

### Mengganti destination ke snowflake
Untuk menyesuaikan keperluan project, destination diubah ke snowflake dengan cara:
1. Membuat database, warehouse, schema, dan user baru di snowflake
``` sql
-- create database with standard settings
CREATE DATABASE dlt_data;
-- create new user - set your password here
CREATE USER loader WITH PASSWORD='<password>';
-- we assign all permissions to a role
CREATE ROLE DLT_LOADER_ROLE;
GRANT ROLE DLT_LOADER_ROLE TO USER loader;
-- give database access to new role
GRANT USAGE ON DATABASE dlt_data TO DLT_LOADER_ROLE;
-- allow `dlt` to create new schemas
GRANT CREATE SCHEMA ON DATABASE dlt_data TO ROLE DLT_LOADER_ROLE;
-- allow access to a warehouse named COMPUTE_WH
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO DLT_LOADER_ROLE;
-- grant access to all future schemas and tables in the database
GRANT ALL PRIVILEGES ON FUTURE SCHEMAS IN DATABASE dlt_data TO DLT_LOADER_ROLE;
GRANT ALL PRIVILEGES ON FUTURE TABLES IN DATABASE dlt_data TO DLT_LOADER_ROLE;
```
2. Melakukan pembuatan folder .dlt yang berisi secrets.toml dengan menjalankan ```dlt init snowflake```
3. Memasukkan credential akun snowflake ke dalam file tersebut.
```
[destination.snowflake.credentials]
database = "dlt_data"
password = "<password>"
username = "loader"
host = "kgiotue-wn98412"
warehouse = "COMPUTE_WH"
role = "DLT_LOADER_ROLE"
```

Pada saat ini, directory project kurang lebih seperti ini
```
└── learn_dlt
   ├── dlt_pipeline.py
   ├── .dlt
   │   └── config.toml
   │   └── secrets.toml
```

3. Menyesuaikan fungsi untuk menjalankan pipeline dengan destination snowflake
```py
def run_properties_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="properties",
        destination="snowflake",
        dataset_name="raw_properties"
        
    )
    load_info = pipeline.run(properties_source())
    print(load_info)
```

### Mendefinisikan fungsi dlt sebagai asset dalam dagster
Mmebuat asset yang ketika di-materialize akan menjalankan fungsi yang sudah dibuat menggunakan dlt

```py
@asset
def run_property_list_asset():
    print("Running DLT pipeline for properties")
    run_properties_pipeline()

@asset
def run_subscription_list_asset():
    print("Running DLT pipeline for subscriptions")
    run_subscriptions_pipeline()
```
## Membuat directory project dbt
### Melakukan dbt init
Ketika menjalankan ```dbt init property_management```, akan membuat folder baru yang berisi struktur project dbt. Sehingga directory berubah menjadi

```
.
└── my-project
   ├── pyproject.toml
   ├── src
   │   └── my_project
   │       ├── __init__.py
   │       ├── definitions.py
   │       └── defs
   │       |  └── __init__.py
   |       └── assets
   │       |  └── kos.py
   ├── tests
   │   └── __init__.py
   └── uv.lock
   ├── .dlt
   │   └── config.toml
   │   └── secrets.toml
   ├── dlt_pipeline
   │   └── kos_pipeline.py
   ├── project_management
   │   └── analyses
   │   └── logs
   │   └── macros
   │   └── models
   │        └── __sources.yml              <-- ditambahkan secara manual
   │        └── schema.yml                 <-- ditambahkan secara manual
   │        └── dim_properties.sql         <-- ditambahkan secara manual
   │        └── dim_subscriptions.sql      <-- ditambahkan secara manual
   │   └── seeds
   │   └── snapshots
   │   └── target
   │   └── tests
   │   └── .gitignore
   │   └── dbt_project.yml
   │   └── profiles.yml       <-- ditambahkan secara manual

```


### Melakukan setting koneksi ke snowflake
Dilakukan dengan cara mengubah konfigurasi di file profiles.yml

Masalah yang dialami:
1. Akun snowflake tidak dapat mengakses tabel yang telah dibuat menggunakan pipeline dlt di snowflake karena masalah akses

Solusi:
1. Menjalankan query grant access di snowflake seperti berikut
``` sql
GRANT USAGE ON DATABASE MANAJEMEN_KOS TO ACCOUNTADMIN;
GRANT CREATE SCHEMA ON DATABASE MANAJEMEN_KOS TO ROLE ACCOUNTADMIN;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ACCOUNTADMIN;
GRANT ALL PRIVILEGES ON FUTURE SCHEMAS IN DATABASE MANAJEMEN_KOS TO ACCOUNTADMIN;
GRANT ALL PRIVILEGES ON FUTURE TABLES IN DATABASE MANAJEMEN_KOS TO ACCOUNTADMIN;

GRANT SELECT ON TABLE MANAJEMEN_KOS.RAW_SUBSCRIPTIONS.SUBSCRIPTION_LIST TO ROLE ACCOUNTADMIN;
```
### Melakukan dbt build
Menjalankan ```dbt build``` di terminal di dalam directory ```property_management```

Masalah yang terjadi:
1. Tidak dapat menemukan "property_management" di file profiles.yml

Solusi:
1. Menyinkronkan variabel name di dalam dbt_project.yml dan profiles.yml menjadi "property_management"

### Melakukan dbt parse
Menjalankan ```dbt parse``` di terminal di dalam directory ```property_management```

### Membuat file project.py
Mengikuti langkah-langkah pembuatan project berdasarkan course dagster and dbt. Dibuat agar dagster mengenali models dbt

``` py
dbt_project = DbtProject(
  project_dir=Path(__file__).joinpath("../../..", "property_management").resolve(),
)
```
Masalah yang terjadi:
1. Beberapa kesalahan yang terjadi akibat import file directory yang kurang tepat

Solusi:
1. Mencermati peletakan file

### Mendeklarasikan definition
Masalah yang terjadi:
1. Definition masih tidak dapat menerima asset meskipun sudah dibuat seperti ini
``` py
all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
)
```


Solusi:
1. Memakai lazy definition
``` py
@definitions
def defs():
    return load_from_defs_folder(project_root=Path(__file__).parent.parent.parent)
```

### Menyambungkan dependencies asset dari dagster ke asset yang dibuat oleh dbt
Dilakukan dengan membuat class CustomizedDagsterDbtTranslator

Versi pertama:
``` py
class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):
        resource_type = dbt_resource_props["resource_type"]
        name = dbt_resource_props["name"]
        if name == "property_list":
            return dg.AssetKey(f"run_properties_asset")
        elif name == "subscription_list":
            return dg.AssetKey(f"run_subscriptions_asset")
        else:
            return super().get_asset_key(dbt_resource_props)
```

alur kerja:
mencari source di dbt (yang di return disini sebenarnya nama table, bukan nama source)
apabila source yang dicari sudah ditemukan, maka source tersebut dihubungkan dengan asset dlt.

Karena fungsinya masih hard-coded, baiknya setiap menamai table di data warehouse(snowflake), namanya harus terkandung dalam asset dalam dagster. Atau nama asset di dagsternya diubah

Versi kedua:
``` py
class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):
        resource_type = dbt_resource_props["resource_type"]
        name = dbt_resource_props["name"]
        if resource_type == "source":
            return dg.AssetKey(f"run_{name}_asset")
        else:
            return super().get_asset_key(dbt_resource_props)
```

