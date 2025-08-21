Dokumentasi mengenai eksplorasi full dapat diakses di [data_quality_solutions.md](data_quality_solutions.md)

# Perbandingan
## Dagster Asset Checks
Pro:
- Karena dagster merupakan tools yang kita gunakan, integrasi asset checks ke dalam orchestration lebih mudah
- Dapat menampilkan detail rows yang ditolak
![invalid_record](invalid_record.png)

Kontra:
- Data yang telah dimasukkan ke dalam database perlu dipanggil lagi untuk melakukan asset checks. Sehingga cukup boros resource dan waktu.
```py
@asset
def run_manusia_list_asset() -> DataFrame:
    load_manusia_table()
    df = fetch_data_from_snowflake()  #Dibuat fungsi tambahan untuk mengambil kembali data yang sudah dimasukkan ke dalam snowflake. Ditakutkan akan mengganggu skalabilitas apabila volume data sudah besar
    return df
```

## Soda
Pro:
- Check disetting dalam file .yml dengan banyak built-in command yang mempermudah logika pengecekan kualitas data
```yml
# checks.yml
checks for MANUSIA:
  # 1. Tinggi antara 110 dan 200
  - invalid_count(TINGGI) = 0:
      valid min: 110
      valid max: 200

  # 2. Berat antara 40 dan 150
  - invalid_count(BERAT) = 0:
      valid min: 40
      valid max: 150

  # 3. Kolom ID harus unik
  - duplicate_count(ID) = 0

  # 4. Kolom NAME tidak boleh null
  - missing_count(NAME) = 0:
      missing values: [N/A, '0000', none,'',' ']

  # 5. Kolom EMAIL harus format email valid
  - invalid_count(EMAIL) = 0:
      valid format: email

```

Kontra:
- Hanya dapat menampilkan berapa banyak cek yang lolos dan gagal, bukan detailnya. Hasil testing:
```
[10:33:05] Scan summary:
[10:33:05] 1/5 checks PASSED: 
[10:33:05]     MANUSIA in my_datasource_name
[10:33:05]       duplicate_count(ID) = 0 [PASSED]
[10:33:05] 4/5 checks FAILED: 
[10:33:05]     MANUSIA in my_datasource_name
[10:33:05]       invalid_count(TINGGI) = 0 [FAILED]
[10:33:05]         check_value: 2
[10:33:05]       invalid_count(BERAT) = 0 [FAILED]
[10:33:05]         check_value: 2
[10:33:05]       missing_count(NAME) = 0 [FAILED]
[10:33:05]         check_value: 1
[10:33:05]       invalid_count(EMAIL) = 0 [FAILED]
[10:33:05]         check_value: 2
[10:33:05] Oops! 4 failures. 0 warnings. 0 errors. 1 pass.
```

# Kesimpulan:
1. Volume data kecil dan ingin hasil mendetail -> Dagster Asset Checks
2. Volume data besar dan tidak butuh detail -> Soda
