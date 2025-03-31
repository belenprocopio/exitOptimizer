from requests import post

url = "http://localhost:8123/api/states/sensor.kitchen_temperature"
headers = {"Authorization": "Bearer TOKEN", "content-type": "application/json"}
data = {"state": "25", "attributes": {"unit_of_measurement": "°C"}}

response = post(url, headers=headers, json=data)
print(response.text)
