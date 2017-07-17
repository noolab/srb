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

# test dhl dropoff service
# paramdhl = {}
# paramdhl["pickup_date"] = "2017-05-26"
# paramdhl["ready_by_time"] = "10:20"
# paramdhl["close_time"] = "14:20"
paramdhl={
  "requestor": {
    "name": "Rikhil",
    "phone": "23162",
    "company": "Saurabh"
  },
  "place": {
    "line1": "123 Test Ave",
    "line2": "Test Bus Park",
    "package_location": "Reception",
    "city": "PARIS",
    "post_code": "75018",
    "country_code": "FR"
  },
  "pick_up": {
    "pickup_date": "2017-06-14",
    "slot_id": "string",
    "ready_by_time": "10:20",
    "close_time": "23:20",
    "number_of_pieces": 0,
    "special_instructions": "1 palett of 200 kgs - Vehicule avec hayon"
  },
  "shipment_details": {
    "number_of_pieces": 1,
    "weight": 200
  }
}
myservice.call_service("dhl","pickup", paramdhl)

print ("\n")
# test parcel pickup service
paramparcel = {}
paramparcel['from'] = "France"
paramparcel['to'] = "Cambodia"
myservice.call_service("parcel", "pickup", paramparcel)


#========================= API GETWAY ================================
#@app.route("/<company>/<service>")
#def pickup(company, service):
#	return mys.0ervice.call_service(company, service, paramdhl)
#if __name0__=="__main__":
#	app.run()

