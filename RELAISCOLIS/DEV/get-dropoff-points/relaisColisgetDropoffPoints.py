import datetime
import requests
import re
import xml.etree.ElementTree as ET
import time
import os
import xmltodict

def getDropoffPoints(event,context):

  # lat = '48.8640556'
  # lng = '2.3478669'

  # GET LAT + LNG
  lng = event["longitude"]
  lat = event["latitude"]

  # CREATE URI
  uri = "http://apir.viamichelin.com/apir/1/FindPOI.xml?db=169676&center=" + lng + ":" + lat + "&dist=30000&nb=5&ie=UTF-8&charset=UTF-8&authKey=JSBS20140827164219887761188235&lg=eng"

  # CALL
  response = requests.get(uri)
  data = xmltodict.parse(response.text)

  relay_list = []

  for relay in data["response"]["poiList"]["item"]:
    sub_tab = []
    for x in relay["poi"]["datasheet"]["descList"]["desc"]:
      if int(x["idx"]) >= 6 and int(x["idx"]) <= 19:
        sub_tab.append(x)
    relay_list.append({
      'dist': relay["dist"],
      'name': relay["poi"]["name"],
      'relay_code': relay["poi"]["id"],
      'lon': relay["poi"]["location"]["coords"]["lon"],
      'lat': relay["poi"]["location"]["coords"]["lat"],
      'city': relay["poi"]["location"]["city"],
      'address': relay["poi"]["location"]["formattedAddressLine"],
      'zip_code': relay["poi"]["location"]["postalCode"],
      'country': relay["poi"]["location"]["countryLabel"],
      'schedules': {
        'monday': { 'am': sub_tab[0]["value"], 'pm': sub_tab[1]["value"]},
        'tuesday': { 'am': sub_tab[2]["value"], 'pm': sub_tab[3]["value"]},
        'wednesday': { 'am': sub_tab[4]["value"], 'pm': sub_tab[5]["value"]},
        'thursday': { 'am': sub_tab[6]["value"], 'pm': sub_tab[7]["value"]},
        'friday': { 'am': sub_tab[8]["value"], 'pm': sub_tab[9]["value"]},
        'saturday': { 'am': sub_tab[10]["value"], 'pm': sub_tab[11]["value"]},
        'sunday': { 'am': sub_tab[12]["value"], 'pm': sub_tab[13]["value"]}}})
  return relay_list