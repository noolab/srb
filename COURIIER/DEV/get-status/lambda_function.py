import requests
import json
import time
import os

def getStatus(event, context):

  start = time.time()
  available = True
  response_time = 0

  # TO ADD TO ENV VARs
  # COURIIER_APIKEY = 8411eecbb657112d7ff930080adb8d73
  # COURIIER_BASE_URI = https://dropit.soixanteseize-lab.com/ecommerce/

  response = requests.get("https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=" + (date.today() + relativedelta(days=+1)).strftime('%Y-%m-%d') + "&dateTo=" + (date.today() + relativedelta(days=+8)).strftime('%Y-%m-%d'), headers=headers)

  try:
    headers = {'apikey': '8411eecbb657112d7ff930080adb8d73'}
    response = requests.get("https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=" + (date.today() + relativedelta(days=+1)).strftime('%Y-%m-%d') + "&dateTo=" + (date.today() + relativedelta(days=+8)).strftime('%Y-%m-%d'), headers=headers)
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