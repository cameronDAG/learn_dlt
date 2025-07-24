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

# dbt test vs run vs build
1. test: validasi apakah isi kolom sudah sesuai
2. run: materialisasi model
3. build: materialisasi model, kemudian menjalankan test