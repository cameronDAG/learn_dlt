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