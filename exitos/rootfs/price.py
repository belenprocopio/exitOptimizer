from datetime import datetime 
from datetime import timedelta
import requests

 # Calculate the date for tomorrow
tomorrow = datetime.today() + timedelta(1)
tomorrow_str = tomorrow.strftime('%Y%m%d')

# Fetch electricity price data from OMIE
url = f"https://www.omie.es/es/file-download?parents%5B0%5D=marginalpdbc&filename=marginalpdbc_{tomorrow_str}.1"
response = requests.get(url)

# If tomorrow's prices are unavailable, fallback to today's data
if response.status_code != 200:
    today = datetime.today().strftime('%Y%m%d')
    url = f"https://www.omie.es/es/file-download?parents%5B0%5D=marginalpdbc&filename=marginalpdbc_{today}.1"
    response = requests.get(url)
    


if response.status_code == 200:
    lines = response.text.split("\r\n")
    elec_prices = []
    for line in lines:
        parts = line.split(";")  # Separar columnas  
        if len(parts) > 5 and int(parts[0]) == tomorrow.year:
            try:
                price = float(parts[-2])
                elec_prices.append(price)
            except ValueError:
                pass
    print(elec_prices)  # Lista final de precios
else:
    print("Error al obtener los datos de OMIE.")
