from requests import get
import pandas as pd
import os

#token api interna.
token = os.environ.get('SUPERVISOR_TOKEN')

#periode que necesitem.
t_ini="2023-10-01T00:00:00"
t_fi="2023-10-25T00:00:00"

#especifiquem Id que volem
id_sensor = "sensor.esp32_gtmeas_sistema_termic_temperatura_diposit"
             

#preparem la url de la api corresponent a la id i periode que volem descarregar
url = "http://supervisor/core/api/history/period/"+t_ini+"?end_time="+t_fi+"&filter_entity_id="+id_sensor + "&minimal_response&no_attributes"

headers = {
    "Authorization": "Bearer "+token,
    "content-type": "application/json",
}

#Llegim les dades de la url
response = get(url, headers=headers).json()

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
    
print("Hem llegit:")
print(sensor_data_historic)