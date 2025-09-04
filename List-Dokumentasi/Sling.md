# Apa itu Sling?
data integration platform modern berbasis CLI (dengan opsi platform UI) yang dirancang untuk mempermudah proses ETL⁄ELT, transformasi, dan quality checks di berbagai sumber data dan destination seperti file, database, atau object storage. Tools ini dibuat menggunakan bahasa go

# Sling CLI
## Installation (Linux)

```bash
# download latest binary
curl -LO 'https://github.com/slingdata-io/sling-cli/releases/latest/download/sling_linux_amd64.tar.gz' \
  && tar xf sling_linux_amd64.tar.gz \
  && rm -f sling_linux_amd64.tar.gz \
  && chmod +x sling


./sling -h
```

## Koneksi ke source dan target
```bash
pip install sling
```

### Melalui file .yml
Salah satu cara untuk mendeklarasikan source dan destination dari sling adalah dengan membuat file ```replication.yml``` yang berisikan detail koneksi

```yml
source: MY_POSTGRES
target: MY_SNOWFLAKE

# default config options which apply to all streams
defaults:
  mode: full-refresh
  object: new_schema.{stream_schema}_{stream_table}

streams:
  my_schema.*:

env:
  SLING_THREADS: 3
```

Agar sling dapat membaca file tersebut, lakukan
```bash
sling run replication.yaml
```
### Melalui CLI

```bash
export MY_PG='postgresql://user:mypassw@pg.host:5432/db1'

sling run --src-stream file:///path/to/myfile.csv --tgt-conn MY_PG --tgt-object public.my_new_data
```

### Melalui kode Python
```py
from sling import Replication, ReplicationStream

replication = Replication(
  source='MY_PG',
  target='MY_AWS_S3',
  steams={
    "my_table": ReplicationStream(
      sql="select * from my_table",
      object='my_folder/new_file.csv',
    ),
  }
)

replication.run()
```

## Connection management
untuk melihat list connection, jalankan
```bash
sling conns list
+--------------------------+-----------------+-------------------+
| CONN NAME                | CONN TYPE       | SOURCE            |
+--------------------------+-----------------+-------------------+
| AWS_S3                   | FileSys - S3    | sling env yaml    |
| FINANCE_BQ               | DB - BigQuery   | sling env yaml    |
| DO_SPACES                | FileSys - S3    | sling env yaml    |
| LOCALHOST_DEV            | DB - PostgreSQL | dbt profiles yaml |
| MSSQL                    | DB - SQLServer  | sling env yaml    |
| MYSQL                    | DB - MySQL      | sling env yaml    |
| ORACLE_DB                | DB - Oracle     | env variable      |
| MY_PG                    | DB - PostgreSQL | sling env yaml    |
+--------------------------+-----------------+-------------------+
```

Untuk mengetes connection, jalankan
``` bash
sling conns test LOCALHOST_DEV
9:04AM INF success!
```

## Sling run
Sling memiliki berbagai macam flag yang dapat digunakan sesuai kebutuhan. Listnya tedapat pada https://docs.slingdata.io/sling-cli/run

# Sling platform
dapat diakses di https://platform.slingdata.io/

## Agent
Merupakan alat yang menampung seluruh data pipeline. Agent akan menghubungkan dirinya dengan pipeline menggunakan API Key

## Connection
Untuk menyambungkan source dan target, prinsipnya mirip dengan yang di CLI

# Hooks/Steps
Mekanisme untuk menjalankan perintah sebelum maupun sesudah replikasi data

Sebelum:
- Validasi requirements
- Download file yang dibutuhkan terlebih dahulu
- Configuration setting
- Cleanup operation

Sesudah:
- Validasi hasil
- Mengirim notifikasi
- Mengupload hasil
- Cleanup operation
- Logging

Ditulis dalam file ```replication.yml``` seperti ini

```yml
defaults:
  ...

streams:
  my_stream:
    hooks:
      pre:
        - type: query
          # hook configuration...

      post:
        - type: http
          # hook configuration...
```

# Pipeline
Pipeline juga dikonfigurasikan di dalam file ```replication.yml``` dengan ```steps``` sebagai kuncinya

```yml
steps:
  - type: log
    message: "Starting pipeline execution"

  - type: replication
    path: path/to/replication.yaml
    id: my_replication

  - type: query
    if: state.my_replication.status == "success"
    connection: my_database
    query: "UPDATE status SET completed = true"

env:
  MY_KEY: VALUE
```

# Constraint
Digunakan untuk mengevaluasi value dari suatu kolom. Dideklarasikan menggunakan syntax SQL. Setiap conditionnya dipisahkan oleh simbol ```|```

```yml
source: source_name
target: target_name

streams:
  my_stream:
    columns:
      # id values cannot be null
      id: bigint | value is not null

      # status values can only be active or inactive
      status: string | value in ('active', 'inactive')

      # col_1 value length can only be 6, 7 or 8
      col_1: string(8) | value_len > 5 and value_len <= 8
```