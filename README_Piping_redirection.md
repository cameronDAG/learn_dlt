# Piping dan Redirection
## Piping
Piping biasa ditandai dengan simbol | dan digunakan untuk mengalirkan output dari 1 perintah sebagai input untuk perintah lainnya.

contoh:
```bash
ls | sort
```

maka program akan mengambil semua directory yang ada terlebih dahulu sebelum melakukan sorting.

## Redirection
Digunakan untuk mengarahkan input dan output dari suatu perintah.

```bash
ls -a > contents.txt
```

- '>' mengarahkan output ke suatu file/perintah
- '<' mengarahkan input ke suatu perintah
- '>>' mengarahkan output ke suatu file/perintah dan memasukkan output ke baris baru apabila filenya sudah memiliki isi
- '2>' mengarahkan hasil error ke suatu file/perintah
- '2>>' mengarahkan hasil error ke suatu file/perintah dan memasukkan error message ke baris baru apabila filenya sudah memiliki isi
- '&>' mengarahkan output dan error ke suatu file/perintah
- '&>>' mengarahkan output dan error dan menambahkan baris baru apabila file sudah memiliki isi
