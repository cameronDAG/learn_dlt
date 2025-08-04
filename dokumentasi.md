# Version 1
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

### Mengganti destination dlt dari duckdb ke snowflake
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
4. Mengganti destination dalam pipeline menjadi snowflake
``` py
def run_properties_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="properties",
        destination="snowflake",
        dataset_name="raw_properties"
        
    )
    load_info = pipeline.run(properties_source())
    print(load_info)
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
Membuat asset yang ketika di-materialize akan menjalankan fungsi yang sudah dibuat menggunakan dlt

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

# Version 2 - menambahkan asset baru dari google drive sheets
## Install library yang belum ada
1. uv pip install google
2. uv pip install google-api-python-client
3. uv pip install pandas
4. uv pip install dlt[parquet]

## Melakukan setting credential menggunakan service_account.json
Cara mendapatkan file tersebut:
1. Akses link https://console.cloud.google.com/
2. Buat project baru
3. Aktifkan API yang dibutuhkan
4. Buat service account baru
5. Pencet tab Key, create new key, json

file service_account.json kemudian ditaruh ke dalam directory project
``` py
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

creds = service_account.Credentials.from_service_account_file(
    r"service_account.json",  # Replace with your actual key path
    scopes=SCOPES
)
sheets_service = build("sheets", "v4", credentials=creds)
```
## Melakukan define resources dan pipeline dlt
Membuat resource baru untuk mengambil data dari spreadsheet
``` py
@dlt.resource(table_name='investor_list')
def get_investors():
    spreadsheet_id = "1lLf0mLzWC_tcbPc3aXsgRLpQtr_P5Yb6DKn-1j152P8"
    range_name = "Sheet1"  # change this to match your actual sheet/tab name

    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])
    if not values:
        print("No data found.")
        return

    # Assume first row is header
    df = pd.DataFrame(values[1:], columns=values[0])
    yield df
```
## Membuat asset dagster untuk menjalankan pipeline berisi resource tersebut
1. Mendefinisikan asset
``` py
@asset
def run_investor_list_asset():
    print("Running DLT pipeline for investors")
    run_investors_pipeline()
```

2. Mencoba menjalankan asset di dagster UI

Masalah yang dialami:
1. https://sheets.googleapis.com/v4/spreadsheets/1lLf0mLzWC_tcbPc3aXsgRLpQtr_P5Yb6DKn-1j152P8/values/Sheet1?alt=json returned "The caller does not have permission".

Solusi:
1. add email service_accountnya ke dalam akses google sheet oleh host/pemiliknya

## Setting sourcenya di dalam dbt
dilakukan agar dbt mengenali data yang mau diambil dari table snowflake 
```
  - name: investors
    database: MANAJEMEN_KOS
    schema: RAW_INVESTORS
    description: data investor
    tables:
      - name: investor_list
        description: investor
```

## Membuat model dim_investors
1. Membuat file .sql yang akan mengambil data dari source investors
2. Mendeklarasikan model di dalam schema.yml

```sql
with

source as (

    select * from {{ source('investors', 'investor_list') }}

)

select * from source
```

## Menjalankan dbt build
untuk memuat models dalam dbt dan melakukan pengecekan pada dagster UI

Masalah:
1. Salah satu test unique error karena terdapat data double. 

Solusi:
1. mengubah write disposition dalam dlt untuk pipeline investors menjadi replace

hasil kode:
``` py
@dlt.resource(table_name='investor_list',write_disposition="replace")
def get_investors():
    spreadsheet_id = "1lLf0mLzWC_tcbPc3aXsgRLpQtr_P5Yb6DKn-1j152P8"
    range_name = "Sheet1"  # change this to match your actual sheet/tab name

    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])
    if not values:
        print("No data found.")
        return

    # Assume first row is header
    df = pd.DataFrame(values[1:], columns=values[0])
    yield df

```
Setelah dijalankan 2x di dagster, tidak ada lagi data yang masuknya double

## Menjalankan materialize di dagster untuk semua asset
Karena dagster-dbt translator telah dibuat pada versi sebelumnya, asset run_investor_list_asset dan dim_investors sudah otomatis terhubung.

Hasil:
Semua asset berhasil dimaterialisasi

Masalah:
1. Tabel investor_list tidak memiliki metadata karena pada saat pembuatan fungsi resources, data diubah menjadi dataframe terlebih dahulu baru di yield. Sehingga slt tidak langsung mengenali kolom yang ada.

Solusi:
1. Ubah cara yielding data menjadi looping
``` py
@dlt.resource(table_name='investor_list', write_disposition="append")
def get_investors():
    spreadsheet_id = "1lLf0mLzWC_tcbPc3aXsgRLpQtr_P5Yb6DKn-1j152P8"
    range_name = "Sheet1"

    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])
    if not values:
        print("No data found.")
        return

    header = values[0]        # ambil nama kolom dari baris pertama
    rows = values[1:]         # data di bawahnya

    # Buat list of dict dari header dan rows
    for row in rows:
        yield {col: row[i] if i < len(row) else None for i, col in enumerate(header)}

```

Penjelasan kode:

```py
values = result.get("values", [])
```

Buat list of dict dari header dan rows
```py
[['ID_apartment', 'Investor', 'Nominal'], 
['1', 'Budi', '1000'], ['2', 'Candra', '2000'], 
['3', 'Adul', '3000'], ['4', 'Komeng', '4000'], ['5'],
['7', 'dudul', '57777'], [], ['8', 'bbdbd', '565']] 
```
masih list kan bentuknya, jadi harus diubah ke dict untuk menentukan kolomnya.
Karena kalau list aja, dlt nggak bisa tahu kolomnya apa aja dan bisa jadi langsung 
memasukkan literal list ke dalam tabel.

```py
for row in rows:
```
iterasi 1
row = ['1', 'Budi', '1000']

```py
    yield {col: row[i] if i < len(row) else None for i, col in enumerate(header)}
```
iterasi 1
i = 0, col = 'ID_apartment', row[0] = '1' -> 'ID_apartment': '1'

iterasi 2
i = 1, col = 'Investor', row[1] = 'Budi' -> 'Investor': 'Budi'

iterasi 3
i = 2, col = 'Nominal', row[2] = '1000' -> 'Nominal': '1000'


2. hapus kolom metadata di model dbt dengan cara mengubah fungsi select ke kolom yang dibutuhkan saja

# Version 3 - mencoba memasukkan Sling
## Melakukan setup
### Instalasi
```bash
uv add dagster-sling
```

untuk membuat folder ```.sling/```, kita akan melakukan

```bash
sling init
```

Hal tersebut membuat directory file **tidak berubah**, maka menurut dokumentasi sling, kita harus menambahkan ```.sling/env.yml``` dan ```replication.yml``` sehingga bentuk directory file menjadi seperti berikut

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
   ├── .sling                             <-- ditambahkan secara manual
   │   └── env.yml                        <-- ditambahkan secara manual
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
   ├── replication.yml        <-- ditambahkan secara manual
```

## Konfigurasi file env.yml dan replication.yml
### env.yml
Berikut hal yang perlu disetting dalam file ```env.yml```

```yml
rest_api_source:
  type: rest_api
  config:
    url: "https://api.example.com/data"
    method: GET
    headers:
      Authorization: "Bearer your_api_token"
    pagination:
      type: cursor
      cursor_param: "page"
      start_value: 1
      page_size: 100
      max_pages: 10


snowflake_target:
    type: snowflake
    account: myaccount.region
    user: myuser
    password: mypassword
    database: MANAJEMEN_KOS
    schema: analytics
    warehouse: compute_wh
    role: myrole
```
notes = nantinya disesuaikan dengan kebutuhan

### replication.yml
Selanjutnya kita harus membuat ```replication.yml``` untuk setting connection sling.

```yml
replications:
  - name: load_api_properties
    source: ${rest_api_source_properties}
    destination: ${snowflake_target}
    load:
      mode: replace
      table: property_list_sling

  - name: load_api_subscriptions
    source: ${rest_api_source_subscriptions}
    destination: ${snowflake_target}
    load:
      mode: replace
      table: subscription_list_sling
```

## Melakukan replikasi
```bash
sling replicate --config replication.yml --env .sling/env.yml
```

Masalah yang dialami:
1. Setelah melakukan perintah tersebut, proses berhasil tapi di snowflake tidak muncul apa-apa. Setelah dicari di dokumentasi resmi sling, sepertinya perintah yang benar adalah ```sling run -r /path/to/replication.yaml```
2. Setelah dicek melalui ```sling conns list```, connestion yang sudah ditulis dalam ```env.yml``` tidak ada dan hanya menampilkan ini
```
+-----------+-----------------+----------+
| CONN NAME | CONN TYPE       | SOURCE   |
+-----------+-----------------+----------+
| LOCAL     | FileSys - Local | built-in |
+-----------+-----------------+----------+
```

Solusi:
1. Connection didaftarkan melalui CLI saja agar saat dilakukan replikasi, sling tidak bingung lagi dengan source dan destinationnya

## Mendaftarkan connection secara manual melalui CLI
### Percobaan pertama - snowflake dan REST API
untuk snowflake:
```bash
export snowflake_target='snowflake://sling_user:MyP@ssw0rd@snowflake_account.region_id/MY_DB/MY_SCHEMA?warehouse=MY_WAREHOUSE&role=MY_ROLE'

```

untuk REST API:
```bash
export REST_API_PROPERTIES='restapi://api.example.com/v1/properties?page=1?method=GET&headers={"x-api-key":"abc123"}&json_path=data.data'
```

yang muncul ketika melakukan ```sling conns list```:
```
+------------------+-----------------+--------------+
| CONN NAME        | CONN TYPE       | SOURCE       |
+------------------+-----------------+--------------+
| LOCAL            | FileSys - Local | built-in     |
| SNOWFLAKE_TARGET | DB - Snowflake  | env variable |
+------------------+-----------------+--------------+
```

Masalah yang terjadi:
1. Kenapa connection REST API-nya tidak terdaftar, padahal ketika dilakukan '''echo $rest_api_source_subscriptions''' variabel connection tersebur jelas ada?

Solusi:
1. Tes replicationnya langsung saja supaya memastikan apakah hal tersebut bermasalah atau tidak
```bash
sling run --src-conn rest_api_source_properties --tgt-conn snowflake_target --tgt-object analytics.property_list_sling --mode replace
```

dan muncul error
```
fatal:
~ could not set task configuration
could not find connection rest_api_source_properties
```
berarti memang koneksi REST API-nya tidak terdaftar

2. Karena solusi diatas tidak berhasil, untuk sementara kita gunakan DuckDB dulu sebagai pengganti REST API sebagai source

### Percobaan kedua - DuckDB
#### Setting Variabel
```bash
export MY_DUCKDB='duckdb:///absolute/path/to/your_file.duckdb'
```

setelah melakukan export untuk koneksi ke ```properties.duckdb``` dan ```subscriptions.duckdb```, maka connection list akan berubah seperti ini

```
+-------------------------+-----------------+--------------+
| CONN NAME               | CONN TYPE       | SOURCE       |
+-------------------------+-----------------+--------------+
| LOCAL                   | FileSys - Local | built-in     |
| MY_DUCKDB_PROPERTIES    | DB - DuckDB     | env variable |
| MY_DUCKDB_SUBSCRIPTIONS | DB - DuckDB     | env variable |
| SNOWFLAKE_TARGET        | DB - Snowflake  | env variable |
+-------------------------+-----------------+--------------+
```

#### Mencoba replikasi
```bash
sling run --src-conn MY_DUCKDB_PROPERTIES --tgt-conn snowflake_target --tgt-object analytics.property_list_sling --mode replace
```

Masalah yang terjadi:
1. error (karena belum setting source streamnya dan tidak ada mode replace, hanya full-refresh, incremental, backfill, snapshot or truncate)
```
fatal:
~ could not parse stream table name
invalid table name:
```

Solusi:
1. Jangan lupa taruh source stream dan ubah modenya ke mode yang tersedia
``` bash
sling run   --src-conn MY_DUCKDB_PROPERTIES   --src-stream "property_list"   --tgt-conn SNOWFLAKE_TARGET   --tgt-object analytics.property_list_sling   --mode full-refresh
```

tebak apa yang terjadi? yak, error
```
tls: failed to verify certificate: x509: certificate is valid for *.prod3.us-west-2.snowflakecomputing.com, *.us-west-2.snowflakecomputing.com, *.global.snowflakecomputing.com, *.snowflakecomputing.com, *.prod3.us-west-2.aws.snowflakecomputing.com, not LPURCVA-BI18025.us-east-4.snowflakecomputing.com
```
karena certificatenya tidak valid untuk region snowflake akun yang digunakan

2. Karena solusi diatas belum berjalan, kita deklarasikan ulang variabel connection ke snowflakenya untuk bisa bypass hal tersebut dari region ```us-east-4``` ke ```snowflakecomputing.com``` dan jalankan kembali perintah replikasi
hasil: masih error
```
fatal:
~ Could not get source columns
did not find any columns for "main"."property_list". Perhaps it does not exists, or user does not have read permission.
```
kali ini error cukup jelas karena tabel property_list dalam duckdb ada di raw_properties.property_list
3. ubah source stream menjadi ```raw_properties.property_list```
hasil: berhasil
```bash
sling run   --src-conn MY_DUCKDB_PROPERTIES   --src-stream "raw_properties.property_list"   --tgt-conn SNOWFLAKE_TARGET   --tgt-object analytics.property_list_sling   --mode full-refresh
3:22PM INF Sling CLI | https://slingdata.io
3:22PM INF connecting to source database (duckdb)
3:22PM INF connecting to target database (snowflake)
3:22PM INF reading from source database
3:22PM INF writing to target database [mode: full-refresh]
3:22PM INF created table "ANALYTICS"."PROPERTY_LIST_SLING_TMP"
3:22PM INF streaming data
3:22PM INF created table "ANALYTICS"."PROPERTY_LIST_SLING"
3:22PM INF inserted 6 rows into "ANALYTICS"."PROPERTY_LIST_SLING" in 24 secs [0 r/s] [1.5 kB]
3:22PM INF execution succeeded
```

## Membuat asset di dagster
Dibuat berdasarkan guide yang ditemukan di https://docs.dagster.io/integrations/libraries/sling#:~:text=Sling%20provides%20an%20easy-to-use%20YAML%20configuration%20layer%20for,derive%20Dagster%20assets%20from%20a%20replication%20configuration%20file.

### Perbaiki replication.yml
```yml
replications:
  - name: load_duckdb_properties
    source: MY_DUCKDB_PROPERTIES
    destination: SNOWFLAKE_TARGET
    defaults:
      mode: full-refresh
      object: 'analytics.property_list_sling'
    streams:
      raw_properties.property_list:
        object: 'analytics.property_list_sling'

  - name: load_api_subscriptions
    source: MY_DUCKDB_SUBSCRIPTIONS
    destination: SNOWFLAKE_TARGET
    defaults:
      mode: full-refresh
      object: 'analytics.subscription_list_sling'
    streams:
      raw_subscriptions.subscription_list:
        object: 'analytics.subscription_list_sling'
```

selanjutnya kita coba run untuk memastikan konfigurasinya sudah benar

Masalah yang ditemukan:
1. Sling bingung mau jalanin replication yang mana
2. di versi Sling yang sekarang (1.4.16) destination itu ga valid, pakeknya target

Solusi:
1. Masing-masing replication dipisah file ke ```replication_properties.yml``` dan ```replication_subscriptions.yml``` sehingga directory file sekarang menjadi

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
   ├── .sling                             <-- ditambahkan secara manual
   │   └── env.yml                        <-- ditambahkan secara manual
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
   ├── replication_properties.yml        <-- ditambahkan secara manual
   ├── replication_subscriptions.yml     <-- ditambahkan secara manual
   
```

2. Destination di file .yml diganti jd target sehingga file ```replication_properties.yml``` menjadi

```yml
source: MY_DUCKDB_PROPERTIES
target: SNOWFLAKE_TARGET
defaults:
  mode: full-refresh
  object: 'analytics.property_list_sling'
streams:
  raw_properties.property_list:
    object: 'analytics.property_list_sling'
```

Hasil: ketika dilakukan ```sling run -r replication_properties.yml``` data duckdb berhasil tersalin ke snowflake

### Jadikan resources di dagster
Karena dagster tidak dapat membaca replication.yml, seluruh koneksi harus didefinisikan ulang dalam resources di dagster.