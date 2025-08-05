# Cron
## Cara memanggil
crontab -e

## Cara menyetel
strukturnya akan seperti ini

```
minute hour day month weekday <command-to-execute>
```

### Contoh
1. jalan setiap hari, setiap bulan, setiap jam 3
```
15 * * * * command
```

2. jalan setiap jam 5.30pm di hari jumat
```
30 17 * * 5 command
```

3. jalan setiap waktu kerja(jam 9-5, senin-jumat)
```
0 9-17 * * 1-5 command
```

4. jalan setiap interval 2 jam
```
0 */2 * * * command
```
