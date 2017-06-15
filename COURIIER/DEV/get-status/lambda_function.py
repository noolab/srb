import requests
import json
import time
import os

def getStatus(event, context):

  start = time.time()
  available = True
  response_time = 0

  try:
    headers = {'apikey': '8411eecbb657112d7ff930080adb8d73'}
    response = requests.get("https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=2017-06-15&dateTo=2017-06-22", headers=headers)
  except:
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