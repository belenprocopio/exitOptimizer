from requests import get
import pandas as pd
import os

#token api interna.
token = os.environ.get('SUPERVISOR_TOKEN')

#periode que necesitem.
t_ini="2025-03-26T00:00:00"
t_fi="2025-03-27T00:00:00"

#especifiquem Id que volem
id_sensor = "sensor.sunvec_potencia_paneles_master"
             

#preparem la url de la api corresponent a la id i periode que volem descarregar
url = "http://supervisor/core/api/history/period/"+t_ini+"?end_time="+t_fi+"&filter_entity_id="+id_sensor + "&minimal_response&no_attributes"

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
    
print("Hem llegit:")
print(sensor_data_historic)
df_sensor = pd.DataFrame([[sensor_data_historic[col][0]['state'],sensor_data_historic[col][0]['last_changed']] for col in sensor_data_historic.columns if col != 0], columns=["state","last_changed"])
print(df_sensor)

df_sensor["last_changed"] = pd.to_datetime(df_sensor["last_changed"])
df_resampled = df_sensor.set_index("last_changed").resample("1h").first().reset_index().fillna(0)
df_resampled["state"] = pd.to_numeric(df_resampled["state"],errors='coerce')
print('Resampled:')
print(df_resampled)
