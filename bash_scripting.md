# bikin file
touch insert_data.sh
vim insert_data.sh

# kasih permission
chmod 777 insert_data.sh

# list error

```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
./insert_data.sh: line 15: unexpected EOF while looking for matching ``'
cammy@LAPTOP-BTRRPI97:~$ ./insert_data.sh
mysql: [Warning] Using a password on the command line interface can be insecure.
./insert_data.sh: line 16: /home/Cammy/insert_log.txt: No such file or directory
```

1. Error pertama: kebanyakan tanda petik di kodenya
2. Error kedua: ada capslock di pathnya
3. Cron-nya belum jalan. Pas dicek di ```systemctl status cron ``` muncul ```(CRON) info (No MTA installed, discarding output)```

# Mencoba mengatasi masalah cron tidak berjalan
menginstall ```sudo apt-get install postfix```

Masalah yang masih ada:
1. Cron jalan (karena ada di file cron_debug.log yang nyatet tiap kali cronnya jalan), tapi nggak ada data masuk

Cron punya pengetahuan terbatas mengenai perintah di bash. Jadi kode dibawah ini

```sh
NAMES=("Alice" "Bob" "Charlie" "Diana" "Evan" "Fiona")
RANDOM_NAME="${NAMES[$RANDOM % ${#NAMES[@]}]}$((RANDOM % 90 + 10))"
EMAIL="${RANDOM_NAME,,}@example.com"  # lowercase email
```

diganti dengan
```sh
NAME=$(shuf -n 1 -e Alice Bob Charlie Diana Evan Fiona)
NUMBER=$(shuf -i 10-99 -n 1)
RANDOM_NAME="${NAME}${NUMBER}"
EMAIL="$(echo "$RANDOM_NAME" | tr '[:upper:]' '[:lower:]')@example.com"
```

insert_log.txt dapat dilihat di [logging](insert_log.txt)