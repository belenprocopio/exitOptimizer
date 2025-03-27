#!/usr/bin/with-contenv bashio

# echo "Creem la carpeta (/share/exitos/) si no existeix, aqui guardarem fitxers persistents."
# mkdir -p /share/exitos/

echo "Starting OS_lab.py..."
python3 OS_lab.py
python3 -m http.server 55023
