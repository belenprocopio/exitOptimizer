from requests import get
import pandas as pd
import os

#token api interna.
token = os.environ.get('SUPERVISOR_TOKEN')

#especifiquem Id que volem
id_sensor = "sensor.sunvec_potencia_paneles_master"
             

#preparem la url de la api corresponent a la id i periode que volem descarregar
url = "http://supervisor/core/api/states/sensor.sunvec_potencia_paneles_master"

headers = {
    "Authorization": "Bearer "+token,
    "content-type": "application/json",
}

#Llegim les dades de la url
response = get(url, headers=headers)

if response.status_code == 200:
    try:
        sensor_data_historic = pd.json_normalize(response.json())
    except ValueError as e:
        print("Error parsing JSON: " + str(e))
elif response.status_code == 500:
    print("Server error (500): Internal server error at sensor ", id_sensor)
    sensor_data_historic = pd.DataFrame()
else:
    print("Request failed with status code: ", response.status_code)
    sensor_data_historic = pd.DataFrame()
    
print("Sensor:")
print(sensor_data_historic)
print("State:")
print(sensor_data_historic['state'][0])
