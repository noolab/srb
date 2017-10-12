from Classes.AbstractService import Service
from Modules.data_converter import data_converter as converter
from Modules.network import networking as netw
from Modules.data_validator import Validator 
from BuiltInService import requests
import os
import time
import datetime
import json
import re

import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
paramlist = {}
responese =""

class gophr(Service):
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
			"status": {
				"get": true
			},
			"label":{
				"post":false
			},
			"pickup":{
				"post":true
			},
			"tracking":{
				"get":false
			}

		}
		return data

	def type(self,paramlist):
		print("type")
		true=True
		false=False
		data={"type": "pickup","postal": false,"pickup": true,"dropoff": false,"linehaul": false}
		return data

	def status(self,paramlist):
		date = datetime.datetime.now() + datetime.timedelta(days=1)
		# curdate = re.sub(r'\s.*','',str(date))
		timeformat = re.sub(r'\..*','',str(date))
		timeformat =  re.sub(r'\s','T',str(timeformat))

		allresponseTime=[]
		paramlist=""
		start=time.time()
		available=True
		response_time=0
		paramlist={
		  "shipment_id": "",
		  "origin": {
		    "name": "Mister John",
		    "phone": "+44 20 9999 8964",
		    "street_number": "",
		    "street_name": "",
		    "line1": "1 Grape St, Covent Garden",
		    "city": "London",
		    "zipcode": "WC2H 8ED",
		    "country_code": "GB",
			"email":"mister.john@gmail.com"
		  },
		  "pickup": {
		    "pickup_date": timeformat
		  },
		  "destination": {
		    "name": "David Beckbeck",
		    "first_name": "David",
		    "last_name": "Beckbeck",
		    "company": "",
		    "street_number": "",
		    "street_name": "",
		    "line1": "25 Crescent Way",
		    "zipcode": "SE4 1QL",
		    "city": "London",
		    "country": "",
		    "country_code": "GB",
		    "phone": "+44 20 9999 1111",
		    "email": "",
		    "latitude": 0,
		    "longitude": 0
		  },
		  "parcel": {
		    "length_in_cm": 10,
		    "width_in_cm":10,
		    "height_in_cm": 10,
		    "weight_in_grams": 200,
		    "number_of_pieces": 0
		  }
		}
		try:
			responese = self.pickup(paramlist)	 #errro here
			print("test here")
		except:
			available=False
			response_time=-1
			# return responese

		# responese = self.pickup(paramlist)

		if response_time==0:
			response_time=time.time()-start

		timeout=False

		if response_time>30:
			timeout=True

		#Call Rooot =======
		response_time_1=0
		start_1 = time.time()
		try:
			rootdata= self.root(paramlist)
		except:
			response_time_1=-1
		if response_time_1 == 0:
			response_time_1 = time.time() - start_1
		allresponseTime.append(response_time_1)

		#Cal type
		response_time_2=0
		start_2 = time.time()
		try:
			rootdata= self.type(paramlist)
		except:
			response_time_2=-1
		if response_time_2 == 0:
			response_time_1 = time.time() - start_2
		allresponseTime.append(response_time_2)

		final_responseTime=min(allresponseTime)
		result = {
		    "available": available,
		    "response_time": final_responseTime,
		    "timeout": timeout,
		    "limit": 30000
		}
		return result

	def pickup(self,userparamlist):
		url = os.environ["GOPHR_PICKUP_URL"]

		req_list=["origin/name","origin/line1","origin/zipcode","origin/email","origin/phone","origin/country_code",
		"destination/first_name","destination/last_name","destination/line1","destination/zipcode","destination/name"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			# reqEmpty=["origin/line2","destination/line2"]
			# paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
		else:
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		data = {
			"api_key" : os.environ["GOPHR_API_KEY"],
			"external_id" : "return_id",
			"pickup_person_name" :paramlist["origin"]["name"],
			"pickup_address1" : paramlist["origin"]["line1"],
			"pickup_postcode" : paramlist["origin"]["zipcode"],
			"pickup_city" : paramlist["origin"]["city"],
			"pickup_country_code" : paramlist["origin"]["country_code"],
			"pickup_email" : paramlist["origin"]["email"],#"mister.john@gmail.com"
			"pickup_mobile_number" : paramlist["origin"]["phone"],
			"pickup_tips_how_to_find" : "Tips to find",
			"delivery_person_name" : paramlist["destination"]["name"],
			"delivery_address1" : paramlist["destination"]["line1"],
			"delivery_postcode" : paramlist["destination"]["zipcode"],
			"delivery_city" : paramlist["destination"]["city"],
			"delivery_country_code" : paramlist["destination"]["country_code"],
			"delivery_mobile_number" : paramlist["destination"]["phone"],
			"size_x" : paramlist["parcel"]["length_in_cm"],
			"size_y" : paramlist["parcel"]["width_in_cm"],
			"size_z" : paramlist["parcel"]["height_in_cm"],
			"weight" : paramlist["parcel"]["weight_in_grams"],
			"order_value" : "100",
			"earliest_pickup_time" : paramlist["pickup"]["pickup_date"],
			"pickup_deadline" : paramlist["pickup"]["pickup_date"]
		}


		headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
		resp = requests.post(url=url, data=data, headers=headers)
		result = json.loads(resp.text)
		try:
			paramlist["pickup_id"]= result["data"]["job_id"]
			paramlist["shipment_details"]=paramlist["parcel"]
		except:
			return result
		del paramlist["parcel"]
		return paramlist

	def tracking(self,paramlist):
		print("tracking")
		tracking_id= str(paramlist) #"20161026-102544-af700b752a5dae25"
		url = os.environ["GOPHR_TRACKING_URL"] #''

		data = {
			"api_key" : os.environ["GOPHR_API_KEY"],
			"job_id" : tracking_id,
		}

		headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
		resp = requests.post(url=url, data=data, headers=headers)
		# return resp.text
		resp  = json.loads(resp.text)
		# final_data=[]
		dt =[{
			"status":resp["data"]["status"],
			"steps": [
				{
					"status": resp["data"]["status"],
					"location": ""
				}
			]
		}]
		return dt