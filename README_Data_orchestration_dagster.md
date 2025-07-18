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

#### Asset
Merepresentasikan sumber data yang terdapat di dalam pipeline.
Snippet:
```
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

#### Asset check
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

#### Definitions
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

#### Dependency
Hubungan antar assets

1. Downstream = asset membutuhkan asset yang lain untuk dijalankan
2. Upstream = asset dibutuhkan oleh asset yang lain

#### Resources
Merupakan sebuah external dependency untuk pipeline dan asset. Seperti API tempat data diambil, database dimana data disimpian, dll.

#### Jobs
Kumpulan tugas yang dijalankan bersama-sama untuk mencapai tujuan.

#### Schedule
Kapan sebuah tugas akan dilakukan, biasanya disetel menggunakan cron.

#### Partitions
Membagi-bagi data menjadi beberapa pecahan untuk memudahkan re-run, debugging, dan optimisasi performa.

#### Backfills
memproses ulang data historis untuk satu atau banyak partisi sekaligus.

#### Sensor
komponen yang secara terus-menerus memantau kondisi eksternal dan menjalankan job secara otomatis jika kondisi tertentu terpenuhi.