# Data Orchestration and Data Scheduler
Data orchestration merupakan proses pembuatan sebuah flow data dalam data environment secara otomatis.

Data orchestration tools biasanya memiliki fungsi sebagai berikut:
1. Scheduling: Menjadwalkan kapan sebuah proses akan dijalankan
2. Dependency management: Menentukan urutan eksekusi
3. Monitoring and retry: Memantau workflow, memberikan notifikasi error, dan otomatis retry
4. Logging and debugging: Menyediakan log untuk analisis kesalahan

Workflow data biasanya divisualisasikan sebagai DAG (Directed Acyclic Graph), dimana setiap task merupakan node yang akan menunjuk ke node lainnya sebagai task yang akan dilakukan selanjutnya.

## Tipe Workflow
```
# 🔑 Perbedaan Task-Centric vs Asset-Centric

| Aspek              | Task-Centric ("Jalankan tugas ini")            | Asset-Centric ("Perbarui aset ini")                   |
|--------------------|-----------------------------------------------|------------------------------------------------------|
| Fokus utama        | Menyelesaikan **tugas/pekerjaan** tertentu    | Memastikan **aset data** selalu mutakhir & konsisten |
| Titik awal         | Dari *job*, script, atau pipeline             | Dari *aset* (tabel, model, laporan) yang ingin dijaga|
| Orientasi proses   | **Proses-driven** (menjalankan langkah-langkah)| **Data-driven** (menjaga hasil akhir tetap valid)    |
| Dependency         | Bergantung pada urutan eksekusi task          | Bergantung pada keterkaitan antar aset                |
| Monitoring         | Apakah tugas selesai atau gagal               | Apakah aset sudah fresh, lengkap, dan konsisten       |
| Contoh             | "Jalankan job ETL harian"                     | "Pastikan tabel `fact_sales` sudah diperbarui hari ini" |
```

## Tools
### Airflow
Apache airflow merupakan sebuah tools open-sources untuk mejadwalkan and memonitor kegiatan workflow.

#### Konsep dasar Airflow
1. Task: Proses yang akan dijalankan
2. Task Instances: Status dari task (running,success,failed)
3. DAG (Directed Acyclic Graph)
4. DAG run: Eksekusi individual masing-masing node DAG

### Dagster
Dagster merupakan sebuah asset-centric data orchestration tools.

# Dagster Essential
## Asset
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

Jenis-jenis asset:
1. Asset
2. Multi-asset
3. Graph-asset
4. Graph-multi-asset

## Asset check
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

## Definitions
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

## Dependency
Hubungan antar assets, di declare di dalam asset

1. Downstream = asset membutuhkan asset yang lain untuk dijalankan
2. Upstream = asset dibutuhkan oleh asset yang lain

## Resources
Merupakan sebuah external dependency untuk pipeline dan asset. Seperti API tempat data diambil, database dimana data disimpian, dll.

## Jobs
Kumpulan tugas yang dijalankan bersama-sama untuk mencapai tujuan.

## Schedule
Kapan sebuah tugas akan dilakukan, biasanya disetel menggunakan cron.

## Partitions
Membagi-bagi data menjadi beberapa pecahan untuk memudahkan re-run, debugging, dan optimisasi performa. Terdapat 3 jenis partition, regular, dynamic, dan triggering.

1. Regular: digunakan untuk dataset yang strukturnya tidak berubah
2. Dynamic Partition: digunakan untuk dataset yang strukturnya dapat berubah-ubah
3. Triggering Partition: membagi data berdasarkan suatu kejadian yang menyalakan sensor

## Backfills
memproses ulang data historis untuk satu atau banyak partisi sekaligus.

## Sensor
komponen yang secara terus-menerus memantau kondisi eksternal dan menjalankan job secara otomatis jika kondisi tertentu terpenuhi.

# Dagster and ETL
## API
1. Langkah pertama: Membuat resources
2. Langkah kedua: Jangan lupa masukkan ke definition

### Time bounding
Dilakukan dengan cara mengambil data yang sebelumnya. Pada contoh kasus, apabila kita mengambil data terbaru, kita tidak dapat yakin bahwa data tersebut telah selesai diupdate, oleh karena itu kita mengambil data versi sebelumnya.

## DLT
Biasanya menggunakan dagster-dlt-translator seperti ini
```python
class CustomDagsterDltTranslator(DagsterDltTranslator):
    def get_asset_spec(self, data: DltResourceTranslatorData) -> dg.AssetSpec:
        default_spec = super().get_asset_spec(data)
        return default_spec.replace_attributes(
            deps=[dg.AssetKey("import_file")],
        )

@dlt_assets(
    ...
    dagster_dlt_translator=CustomDagsterDltTranslator(),
)

```

namun cara yang lebih simplenya adalah dengan membuat dagster asset yang memanggilkan function run pipeline dlt
```py
@dg.asset()
def run_metadata_asset(context: dg.AssetExecutionContext):

    run_metadata_pipeline()
```
## Sling (untuk database)
Sling merupakan alat replikasi yang menyalin data dari database sumber dan menjadikannya sebuah asset di dagster.

Cara kerja:
1. Dagster akan membaca file YAML untuk mengetahui credential dan tabel mana yang ingin dibaca dalam database
2. Dengan menggunakan sling, data yang dibaca akan direplikasi ke dalam bentuk asset menggunakan decorator @sling_assets

# Dagster and DBT
Models di dbt bisa dijadikan asset dalam Dagster menggunakan fungsi dekorasi @dbt_asset.
Ketika proses materialize dalam dagster dijalankan, asset-asset yang berasal dari dbt dianggap menjadi satu proses. Hal ini dikarenakan dalam dbt, kita biasa menjalankan dbt run atau dbt build untuk semua modelnya sekaligus.

