from Classes.AbstractService import Service
from Modules.data_converter import data_converter as converter
from Modules.network import networking as netw
from Modules.data_validator import Validator 
import os
import xml.etree.ElementTree as ET
import time
import datetime
import json
import re

COURIIER_PICKUP_URL=os.environ["COURIIER_PICKUP_URL"]
COURIIER_HEADERS_APIKEY =  os.environ["COURIIER_HEADERS_APIKEY"]
COURIIER_URL_REQ = os.environ["COURIIER_URL_REQ"]
class couriier(Service):

	def root(self,paramlist):
		true=True
		false = False
		data={
			"/": {
				"get": true
			},
			"type": {
				"get": true
			},
			"pickup/slots": {
				"get": true
			},
			"pickup": {
				"post": true
			},
			"status": {
				"get": true
			},
			"tracking":{
				"get":false
			}

		}
		return data

	def status(self,paramlist):
		
		paramlabel ={}
		parampickup={
			"origin": {
			    "first_name": "Test ",
			    "last_name":"Mission",
			    "phone": "0671844487", 
			    "company": "string",
			    "street_number": "string",
			    "line1": "21 rue des filles du calvaire",
			    "line2": "Digicode test", 
			    "city": "Paris", 
			    "zipcode": "75003", 
			    "latitude": 55.685800, 
			    "longitude": 12.584826
			},
			"destination": {
			    "first_name": "Test",
			    "last_name":"Campaign",
			    "line1": "9 rue du faubourg saint Denis",
			    "line2": "Digicode test",
			    "zipcode": "75010",
			    "city": "Paris", 
			    "phone": "0671844487", 
			    "latitude": 48.86302, 
			    "longitude": 2.366132
			},
			"pickup": {
			    "date": "2017-07-05 15:00:00",
			},
			"parcel":{}
		}
		paramtraking={}
		objfunction=["root","type","pickup","pickup/slots"]
		instance = Validator()
		api_url_request = os.environ["API_DEVEVELOPER_URL"]
		result = instance.get_all_status("couriier",api_url_request,objfunction,paramlabel,parampickup,"",paramtraking,"")
		return result

	def pickupslots(self ,paramlist):
		headers = {'apikey': COURIIER_HEADERS_APIKEY}
		# today = datetime.date.today()
		# url="https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=" + (today + relativedelta(days=+1)).strftime('%Y-%m-%d') + "&dateTo=" + (today + relativedelta(days=+8)).strftime('%Y-%m-%d')
		date = datetime.datetime.now()
		tmr = date + datetime.timedelta(days=1)
		eightDay = date + datetime.timedelta(days=8)
		url=COURIIER_URL_REQ + (tmr).strftime('%Y-%m-%d') + "&dateTo=" + (eightDay).strftime('%Y-%m-%d')
		response = netw.sendRequestHeaderConfig(url, "", "get", headers)
		data_json = json.loads(response.text)
		FMT = '%H:%M:%S'
		data =[]
		for l in data_json:
			# start_time =l["formatted_date"]+" "+l["slot"]["formatted_slot_from"]
			s2 = l["slot"]["formatted_slot_to"]
			s1 = l["slot"]["formatted_slot_from"]
			minusone_hour='01:00:00'
			bigone_hour='04:00:00'
			start_time =l["slot"]["formatted_slot_from"]
			duration = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)
			duration=int(duration.seconds/60 )
			timezone=True
			newstart_time =  datetime.datetime.strptime(start_time, FMT) - datetime.datetime.strptime(minusone_hour, FMT)
			dt={
				"formatted_date":l["formatted_date"],
				"slot":{
					"id":l["id"],
					"start_time":str(newstart_time),
					"duration":duration,
					"availability":-1
				}
			}

			data.append(dt)

		count =1
		result = []
		for l in data:
			if count ==1:
				dt={
					"date":l["formatted_date"],
					"timezone":True,
					"slots":[l["slot"]]
				}
				result.append(dt)
				count =count+1
			for res in result:
				if l["formatted_date"] == res["date"]:
					print ("same date sir--------->")
					newslot = l["slot"]
					res["slots"].append(newslot)
				else:
					if not any(res['date'] == l["formatted_date"] for res in result):
						print("diff sir")
						dt={
							"date":l["formatted_date"],
							"timezone":True,
							"slots":[l["slot"]]
						}
						result.append(dt)

		final_data_reuslt =sorted(result, key=lambda x: x['date'], reverse=False)
		return final_data_reuslt

	def type(self,paramlist):
		true=True
		false=False
		data={"type": "pickup","postal": false,"pickup": true,"dropoff": false,"linehaul": false}

		return data


	def pickup(self,userparamlist):
		print("pickup fucntion")
		url = COURIIER_PICKUP_URL
		headers={"apiKey": COURIIER_HEADERS_APIKEY,"Content-Type": "application/json"}
		req_list=["origin/first_name","origin/last_name","origin/line1","origin/zipcode","origin/city","origin/phone","destination/first_name","destination/last_name","destination/line1","destination/zipcode","destination/city","destination/phone","pickup/date"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			# paramlist=userparamlist
			reqEmpty=["origin/line2","destination/line2","parcel/number_of_pieces"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
			paramlist["origin"]["name"]= str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
			paramlist["destination"]["name"]=str(paramlist["destination"]["first_name"])+" "+str(paramlist["destination"]["last_name"])

			address1 = str(paramlist["origin"]["line1"])+" "+str(paramlist["origin"]["city"])+" "+str(paramlist["origin"]["zipcode"])
			datalatlng = instance.getLatLng(address1)
			paramlist["origin"]["longitude"] = str(datalatlng["lng"])	#paramlist["longitude"]
			paramlist["origin"]["latitude"] = str(datalatlng["lat"])		#paramlist["latitude"]

			address2 = str(paramlist["destination"]["line1"])+" "+str(paramlist["destination"]["city"])+" "+str(paramlist["destination"]["zipcode"])
			datalatlng2 = instance.getLatLng(address2)
			paramlist["destination"]["longitude"] = str(datalatlng2["lng"])	#paramlist["longitude"]
			paramlist["destination"]["latitude"] = str(datalatlng2["lat"])		#paramlist["latitude"]

		else:
			# return checkparamlist["message"]
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		data_sender=json.dumps({
            "datas": "[{\"offerIdTarifs\": \"RPP-CLASSIC\",\"pickupName\": \""+paramlist["origin"]["name"]+"\",\"pickupLatitude\": \""+str(paramlist["origin"]["latitude"])+"\",\"pickupLongitude\": \""+str(paramlist["origin"]["longitude"])+"\",\"pickupAddress\": \""+paramlist["origin"]["line1"]+"\",\"pickupAddress2\": \""+paramlist["origin"]["line2"]+"\",\"pickupZip\": \""+paramlist["origin"]["zipcode"]+"\",\"pickupCity\": \""+paramlist["origin"]["city"]+"\",\"pickupTel\": \""+paramlist["origin"]["phone"]+"\",\"recipientName\": \""+paramlist["destination"]["name"]+"\",\"recipientLatitude\": \""+str(paramlist["destination"]["latitude"])+"\",\"recipientLongitude\": \""+str(paramlist["destination"]["longitude"])+"\",\"recipientAddress\": \""+paramlist["destination"]["line1"]+"\",\"recipientAddress2\": \""+paramlist["destination"]["line2"]+"\",\"recipientZip\": \""+paramlist["destination"]["zipcode"]+"\",\"recipientCity\": \""+paramlist["destination"]["city"]+"\",\"recipientTel\": \""+paramlist["destination"]["phone"]+"\",\"deliveryType\": \"BAL\", \"pickupTimeManagement\": \""+paramlist["pickup"]["date"]+"\"}]"
        })
        # data_sender = json.dumps(data)
		response = netw.sendRequestHeaderConfig(url, data_sender, "post", headers)
		# newresp= re.sub(r'\"\\\"\\\\n','',str(response))
		# final_data=re.sub(r'\\','',newresp)
		final_data  =  json.loads(response)
		try:
			paramlist["pickup_id"] = final_data[0]["id"]
		except:
			paramlist["pickup_id"]=""
		paramlist["shipment_details"] = paramlist["parcel"]
		del paramlist["parcel"]
		return paramlist