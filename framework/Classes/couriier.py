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
				"get": true
			},
			"status": {
				"get": true
			}
		}
		return data

	def status(self,paramlist):
		start = time.time()
		available = True
		response_time = 0

		try:
			headersConfig = {'apikey': COURIIER_HEADERS_APIKEY}
			date = datetime.datetime.now()
			tmr = date + datetime.timedelta(days=1)
			eightDay = date + datetime.timedelta(days=8)
			urlreq=COURIIER_URL_REQ + (tmr).strftime('%Y-%m-%d') + "&dateTo=" + (eightDay).strftime('%Y-%m-%d')
			response = netw.sendRequestHeaderConfig(urlreq, "", "get", headersConfig)
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
			start_time =l["formatted_date"]+" "+l["slot"]["formatted_slot_from"]
			s2 = l["slot"]["formatted_slot_to"]
			s1 = l["slot"]["formatted_slot_from"]
			duration = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)
			duration=int(duration.seconds/60 )
			dt={
				"formatted_date":l["formatted_date"],
				"slot":{
					"start_time":start_time,
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
							"slots":[l["slot"]]
						}
						result.append(dt)
		return result

	def type(self,paramlist):
		true=True
		false=False
		data={"type": "pickup","postal": false,"pickup": true,"dropoff": false,"linehaul": false}

		return data


	def pickup(self,userparamlist):
		print("pickup fucntion")
		url = COURIIER_PICKUP_URL
		headers={"apiKey": COURIIER_HEADERS_APIKEY,"Content-Type": "application/json"}
		paramlist = {}
		paramlist["requestor"] = {}
		paramlist["plcae"] = {}
		paramlist["plcae"]["line2"] = ""
		paramlist["destination"] = {}
		paramlist["destination"]["line2"] = ""
		req_list=["requestor/name","place/latitude","place/longitude","place/line1","place/post_code","place/city","requestor/phone","destination/name","destination/longitude","destination/latitude","destination/line1","destination/zipcode","destination/city","destination/phone","pickup/pickup_date"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
		else:
			return checkparamlist["message"]
		data_sender=json.dumps({
            "datas": "[{\"offerIdTarifs\": \"NPP-CLASSIC\",\"pickupName\": \""+paramlist["requestor"]["name"]+"\",\"pickupLatitude\": \""+str(paramlist["place"]["latitude"])+"\",\"pickupLongitude\": \""+str(paramlist["place"]["longitude"])+"\",\"pickupAddress\": \""+paramlist["place"]["line1"]+"\",\"pickupAddress2\": \""+paramlist["place"]["line2"]+"\",\"pickupZip\": \""+paramlist["place"]["post_code"]+"\",\"pickupCity\": \""+paramlist["place"]["city"]+"\",\"pickupTel\": \""+paramlist["requestor"]["phone"]+"\",\"recipientName\": \""+paramlist["destination"]["name"]+"\",\"recipientLatitude\": \""+str(paramlist["destination"]["latitude"])+"\",\"recipientLongitude\": \""+str(paramlist["destination"]["longitude"])+"\",\"recipientAddress\": \""+paramlist["destination"]["line1"]+"\",\"recipientAddress2\": \""+paramlist["destination"]["line2"]+"\",\"recipientZip\": \""+paramlist["destination"]["zipcode"]+"\",\"recipientCity\": \""+paramlist["destination"]["city"]+"\",\"recipientTel\": \""+paramlist["destination"]["phone"]+"\",\"deliveryType\": \"BAL\", \"pickupTimeManagement\": \""+paramlist["pickup"]["pickup_date"]+"\"}]"
        })
        # data_sender = json.dumps(data)
		response = netw.sendRequestHeaderConfig(url, data_sender, "post", headers)
		newresp= re.sub(r'\"\\\"\\\\n','',str(response))
		final_data=re.sub(r'\\','',newresp)
		return json.loads(final_data)
		