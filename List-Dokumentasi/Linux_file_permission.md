# Linux File Permission

## 1. Cara Mengecek Permission File

Gunakan perintah berikut di terminal:
```bash
ls -l
```
## 2. Struktur
```
rwxrw-r–
```

3 huruf pertama: permission buat user (yang buat file)
3 huruf tengah: permission buat grup
3 huruf terakhir: permission buat other member

r = baca
w = nulis/ubah
x = menjalankan

## 3. Cara mengubah akses
### Cara pertama
```
chmod [kode] [nama-file]
```
### Cara Kedua
```
chmod [user][+/-/=][tipe akses]
```
