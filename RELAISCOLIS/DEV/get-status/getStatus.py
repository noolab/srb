import requests
import time
import datetime
import re

def lambda_handler(event,context):
  date = datetime.datetime.now()
  datenow=re.sub(r'\s.*','',str(date))

  lat = '48.8640556'
  lng = '2.3478669'

  uri = "http://apir.viamichelin.com/apir/1/FindPOI.xml?db=169676&center=" + lng + ":" + lat + "&dist=30000&nb=5&ie=UTF-8&charset=UTF-8&authKey=JSBS20140827164219887761188235&lg=eng"

  start = time.time()
  available = True
  response_time = 0

  try:
    response = requests.get(uri)
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