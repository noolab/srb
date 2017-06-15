import requests
import json
import os

def getSlots(event, context):
  headers = {'apikey': '8411eecbb657112d7ff930080adb8d73'}
  response = requests.get("https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=2017-06-15&dateTo=2017-06-22", headers=headers)

  data = json.dumps(response.text)

  # days = []

  # for slot in data:

  return data