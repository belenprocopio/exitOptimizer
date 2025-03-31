from requests import post

def post_state(id_sensor,state,unit_of_measurement):
  #token api interna.
  token = os.environ.get('SUPERVISOR_TOKEN')
  
  #preparem la url de la api corresponent a la id que volem canviar
  url = "http://localhost:8123/api/states/"+id_sensor
  headers = {
    "Authorization": "Bearer " +token, 
    "content-type": "application/json",
  }
  
  data = {"state": state, "attributes": {"unit_of_measurement": unit_of_measurement}}

  response = post(url, headers=headers, json=data)
  print(response.text)
