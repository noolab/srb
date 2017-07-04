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
			headersConfig = {'apikey': '8411eecbb657112d7ff930080adb8d73'}
			date = datetime.datetime.now()
			tmr = date + datetime.timedelta(days=1)
			eightDay = date + datetime.timedelta(days=8)
			urlreq="https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=" + (tmr).strftime('%Y-%m-%d') + "&dateTo=" + (eightDay).strftime('%Y-%m-%d')
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

	def slots(self ,paramlist):
		headers = {'apikey': '8411eecbb657112d7ff930080adb8d73'}
		# today = datetime.date.today()
		# url="https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=" + (today + relativedelta(days=+1)).strftime('%Y-%m-%d') + "&dateTo=" + (today + relativedelta(days=+8)).strftime('%Y-%m-%d')
		date = datetime.datetime.now()
		tmr = date + datetime.timedelta(days=1)
		eightDay = date + datetime.timedelta(days=8)
		url="https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=" + (tmr).strftime('%Y-%m-%d') + "&dateTo=" + (eightDay).strftime('%Y-%m-%d')
		response = netw.sendRequestHeaderConfig(url, "", "get", headers)
		return json.loads(response.text)

	def type(self,paramlist):
		true=True
		false=False
		data={"type": "pickup","postal": false,"pickup": true,"dropoff": false,"linehaul": false}

		return data


	def pickup(self,userparamlist):
		print("pickup fucntion")
		url = "https://dropit.soixanteseize-lab.com/ecommerce/orders"
		headers={"apiKey": "8411eecbb657112d7ff930080adb8d73","Content-Type": "application/json"}
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
		