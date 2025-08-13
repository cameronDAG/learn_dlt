# Tahap Extract dan Load
Tools: DLT, Sentry, Dagster

### Schema dan Data Contract
Schema dapat dibuat dalam fungsi Python maupun file .yaml terpisah, digunakan sebagai acuan validasi struktur dan tipe data yang dimuat oleh pipeline. Sementara itu, data contract adalah aturan yang ditetapkan untuk mengatasi apabila terjadi sebuah perubahan schema.

Terdapat 3 level dalam data contract:
1. Table:
    - evolve: Allows the creation of new tables within the schema.
    - freeze: Prevents any changes to the schema, ensuring no new tables can be added.
2. Column:
    - evolve: Allows for the addition of new columns or changes in the existing ones.
    - freeze: Prevents any changes to the existing columns.
    - discard_row: Skips rows that have new columns but loads those that follow the existing schema.
    - discard_value: Doesn't skip entire rows. Instead, it only skips the values of new columns loading the rest of the row data.
3. Data type:
    - evolve: Allows any data type. This may result with variant columns upstream.
    - freeze: Prevents any changes to the existing data types.
    - discard_row: Omits rows with unverifiable data types.
    - discard_value: Replaces unverifiable values with None, but retains the rest of the row data.

apabila terdapat pelanggaran terhadap schema, akan ditampilkan dalam SchemaValidationError yang bisa diimport dari library dlt.common.schema.exceptions

### Sentry
Berdasarkan tutorial Advanced DLT bagian 8: Logging & Tracing(https://colab.research.google.com/drive/1YCjHWMyOO9QGC66t1a5bIxL-ZUeVKViR#forceEdit=true&sandboxMode=true), DLT dapat terhubung dengan Sentry.

Sentry merupakan sebuah tools yang menangani error logging & tracking. Sentry akan menampilkan hasil exception dalam python ke dalam dashboardnya melalui fungsi ```sentry_sdk.capture_exception(e)```

## Alur kerja
1. Tetapkan schema untuk masing-masing data
2. Setting data contract untuk setiap level sebagai freeze, agar schema tidak berubah. Write disposition = merge
3. Buat sentry menangkap exception yang menyebabkan pipeline gagal dijalankan
4. Buat sentry mengirim alert melalui e-mail/teams/slack

Alternatif yang lebih susah tapi kayaknya lebih efektif
1. Tetapkan schema untuk masing-masing data
2. Setting data contract column sebagai discard_row, agar data yang bener tetep bisa masuk supaya nggak ganggu proses bisnis. Write disposition = merge
3. Pastiin sentry bisa deteksi mana aja data yang rusak buat dia jadiin alert (pake sentry_sdk.capture_message tapi log levelnya setting jadi ERROR karena defaultnya INFO)
4. Masukin data yang rusak ke dalam tabel khusus buat diolah dulu
5. Setelah data yang bermasalah diperbaiki, load lagi ke pipeline

# Tahap transform
Tools: DBT, Dagster, Great Expectation

### DBT Unit testing
DBT dapat melakukan generic dan singular testing, tapi tidak dapat membuat alert untuk developer.

### Great Expectation
Merupakan library python yang digunakan untuk melakukan testing terhadap data. Tools ini juga dapat mengirimkan alert lewat e-mail/slack/teams

## Alur kerja
1. Cek lagi di Great Expectation dan dbt dijadikan alat transform aja
2. Transformasi di dbt
3. Lanjut ke nodes selanjutnya
4. Ulangi step 1-3 sampai data sampai ke user

Kenapa nggak ngirim alert dari dagster aja?
- Dagster cuma bakal ngasih alert "job A is failed" tapi buat detailnya kita tetep harus nyari sendiri di log

# Extra step
## Dashboard
Kalau berdasarkan buku Data Quality Fundamental, sebaiknya buat 2 buah dashboard ini

1. Monitoring for freshness
    Buat graph bar chart yang terbentuk dari jumlah data yang masuk per-harinya
    ```sql
     SELECT
        DATE_ADDED,
        COUNT(*) AS ROWS_ADDED
    FROM
        EXOPLANETS
    GROUP BY
        DATE_ADDED;
  ```
  
2. Understanding distribution
    bikin dashboard buat liat kalau distribusi data tiba-tiba jadi tidak normal

## Data catalog
- Simpan metadata pipeline dlt
- Simpan hasil testing Great Expectation buat tau kualitas data
- Metadata bisnis (owner dari data)
- Last updated timestamp

Saran tools: Datahub
