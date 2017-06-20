import requests
import json
import os


# TO ADD TO ENV VARs
# COURIIER_APIKEY = 8411eecbb657112d7ff930080adb8d73
# COURIIER_BASE_URI = https://dropit.soixanteseize-lab.com/ecommerce/

def getSlots(event, context):
  headers = {'apikey': '8411eecbb657112d7ff930080adb8d73'}
  response = requests.get("https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=" + (date.today() + relativedelta(days=+1)).strftime('%Y-%m-%d') + "&dateTo=" + (date.today() + relativedelta(days=+8)).strftime('%Y-%m-%d'), headers=headers)

  data = json.dumps(response.text)

  # days = []

  # for slot in data:

  return data