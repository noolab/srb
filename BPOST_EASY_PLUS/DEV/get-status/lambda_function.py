import json
import requests
import time
import os

def getStatus(event, context):
  start = time.time()
  available = True
  response_time = 0

  try:
      response = requests.post(
          url = "https://rraw4ebe2c.execute-api.eu-central-1.amazonaws.com/sandbox/label",
          headers = {
              "Content-Type": "application/json; charset=utf-8",
          },
          data = json.dumps({
              "destination": {
                  "state": "IDF",
                  "country_code": "FR",
                  "email": "",
                  "phone": "0688997788",
                  "company": "Company Destination",
                  "zipcode": "75001",
                  "line1": "59 rue des petits champs",
                  "street_number": "",
                  "first_name": "Leo",
                  "city": "Paris",
                  "shipment_id": "return_id_at_srb",
                  "last_name": "Martin",
                  "country": "France",
                  "name": "Leo Martin",
                  "line2": ""
              },
              "return_id": "9999",
              "parcel": {
                  "height_in_cm": 10,
                  "weight_in_grams": 1950,
                  "width_in_cm": 10,
                  "length_in_cm": 10
              },
              "contents": "TESTS",
              "origin": {
                  "state": "",
                  "country": "France",
                  "country_code": "FR",
                  "phone": "0622889977",
                  "place_description": "At home",
                  "company": "Company Origin",
                  "zipcode": "94000",
                  "line1": "11 avenue de la habette",
                  "street_number": "",
                  "first_name": "Ithyvan",
                  "city": "CRETEIL",
                  "last_name": "Schreys",
                  "email": "eddy@shoprunback.com",
                  "name": "Ithyvan Schreys",
                  "line2": ""
              },
              "shipment_date": "2017-06-10"
          })
      )
  except requests.exceptions.RequestException:
      available = False
      response_time = -1

  if response_time == 0:
    response_time = time.time() - start

  timeout = False

  if response_time > 30:
    timeout = True

  result = {
      "available": available,
      "response_time": response_time,
      "timeout": timeout,
      "limit": 30000
  }
  return result
