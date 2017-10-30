from ServiceManager import ServiceManager
import xml.etree.ElementTree as ET
import requests
import datetime
import re
import sys
#from flask import Flask
#from flask import request

#app = Flask(__name__)

myservice = ServiceManager()


paramdhl={
  "shipment_id": "132456",
  "origin": {
    "first_name": "ithyvan",
    "last_name": "schreys",
    "name": "",
    "phone": "0769090961",
    "company": "ShopRunBack",
    "street_number": "",
    "street_name": "",
    "line1": "Na Košince",
    "line2": "",
    "city": "Praha",
    "zipcode": "180 00",
    "country_code": "CZ"
  },
  "destination": {
    "first_name": "Ithyvan",
    "last_name": "SCHREYS",
    "name": "",
    "phone": "",
    "company": "",
    "street_number": "",
    "street_name": "",
    "line1": "59 rue des petits champs",
    "line2": "",
    "city": "Paris",
    "zipcode": "75001",
    "country_code": "FR"
  },
  "parcel": {
    "length_in_cm": "10",
    "width_in_cm": "10",
    "height_in_cm": "10",
    "weight_in_grams": "1000",
    "number_of_pieces": "1"
  },
  "dropoff": {
    "point_id": ""
  },
  "pickup": {
    "slot_id": "",
    "date": "",
    "slot_start_at": "",
    "slot_end_at": "",
    "special_instructions": ""
  }
}
myservice.call_service("shoprunback","pickup", paramdhl)

print ("\n")
# test parcel pickup service
# paramparcel = {}
# paramparcel['from'] = "France"
# paramparcel['to'] = "Cambodia"
# myservice.call_service("parcel", "pickup", paramparcel)


#========================= API GETWAY ================================
#@app.route("/<company>/<service>")
#def pickup(company, service):
#	return mys.0ervice.call_service(company, service, paramdhl)
#if __name0__=="__main__":
#	app.run()

