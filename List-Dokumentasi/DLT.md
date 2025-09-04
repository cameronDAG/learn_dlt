# DLT (Data Load Tool) ETL Summary

## 📌 Pengertian

**DLT** adalah library Python yang mempermudah proses **ETL** (Extract, Transform, Load), terutama untuk data berbentuk JSON nested yang ingin dimasukkan ke data warehouse.

---

## 📦 Instalasi

```bash
pip install dlt
```

---

## ⚙️ Cara Kerja DLT

1. **Extract**: Mengambil data mentah dari berbagai sumber.
2. **Normalize**: Memecah struktur JSON nested menjadi tabel-tabel yang terpisah dan saling berelasi.
3. **Load**: Memasukkan hasil normalisasi ke dalam data warehouse (misalnya DuckDB).

---

## 🧱 Struktur Pipeline

```python
@dlt.source
def sumber_data():
    @dlt.resource
    def ambil_data():
        yield {...}

    return ambil_data

@dlt.transformer
def ubah_data(item):
    item["new_column"] = ...
    yield item
```

Struktur umum:
```
[Resource] → [Transformer] → [Transformer/Aggregation] → Hasil akhir
```

---

## 🚀 Menjalankan Pipeline

```python
load_info = pipeline.run(data, table_name="nama_tabel", write_disposition="append")
```

### Opsi `write_disposition`:
- `append`: Menambahkan data baru.
- `replace`: Menghapus data lama dan menggantinya.
- `skip`: Tidak memuat data.
- `merge`: Deduplikasi dan merge data berdasarkan `primary_key`.

---

## 🧩 Komponen Tambahan

### 🔁 Pagination
DLT mendukung data paginasi secara otomatis.

### 🧪 Incremental Loading
Hanya memuat data yang baru atau diubah berdasarkan parameter seperti `created_at`.

---

## 📈 Progress Bar (Opsional)
DLT mendukung beberapa tool untuk menampilkan progress:
- `log`
- `enlighten`
- `alive_progress`
- `tqdm`

---

## 🧮 Skema dan Metadata

- **Skema** bisa dicek via CLI atau Python.
- **Metadata**: Informasi seperti waktu eksekusi pipeline.
- **Load Info**: Info mengenai data terbaru yang dimuat.
- **Trace**: Detail eksekusi pipeline.
- **State**: Status internal pipeline.

---

## 🔀 Transformasi Data

- **Before Extract**: `query_adapter_callback`
- **After Extract, Before Load**:
  - `add_map`
  - `add_yield_map`
  - `add_filter`

Contoh:
```python
@my_resource.add_map
def anonimisasi_author(row):
    row["author"] = hash(row["author"])
    return row
```

---

## 📜 Data Contract

Untuk mengontrol perubahan skema data:

### Table Level:
- `evolve`: Perubahan dan penambahan table diperbolehkan.
- `freeze`: Tidak memperbolehkan perubahan apa pun.

### Column Level:
- `evolve`, `freeze`, `discard_row`, `discard_value`

### Data Type Level:
- `evolve`, `freeze`, `discard_row`, `discard_value`

---

## 🧵 Paralelisme di Python

- **Threading**: Banyak thread dalam 1 proses.
- **Multiprocessing**: Proses dijalankan di core berbeda.
- **AsyncIO**: Bergantian dalam menjalankan proses async.

---

## 💡 Contoh Ambil Data dari Pipeline

```python
df = pipeline.dataset().nama_tabel.df()
```

---

## ⛓️ Pre-built Sources & Destinations

Inisialisasi menggunakan:
```bash
dlt init <verified-source> <destination>
```
