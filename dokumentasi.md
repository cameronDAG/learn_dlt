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

