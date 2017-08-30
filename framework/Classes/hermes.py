from Classes.AbstractService import Service
from BuiltInService import requests 
from Modules.data_converter import data_converter as converter
from Modules.data_validator import Validator 
from Modules.network import networking as netw

import os
from random import randrange
import re
import time
import datetime
import xml.etree.ElementTree as ET
import json
import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import hashlib


date = datetime.datetime.now()
curdate = re.sub(r'\s.*','',str(date))

HERMES_URL_LABEL = os.environ["HERMES_URL_LABEL"]
HERMES_URL_STATUS = os.environ["HERMES_URL_STATUS"]


class hermes(Service):
	"""docstring for hermes"""
	def root(self,userparamlist):
		true=True
		false= False
		data={
			"/":{
				"get":true
			},
			"type":{
				"get":true
			},
			"label":{
				"post":true
			},
			"status":{
				"get":true
			},
			"tracking":{
				"get":false
			}
		}
		return data

	def type(self,paramlist):
		true=True
		false=False
		data={
			"type": "postal",
			"postal": true,
			"pickup": false,
			"dropoff": false,
			"linehaul": false
		}
		return data

	def status(self,paramlist):
		allresponseTime=[]
		paramlist=""
		
		start=time.time()
		available=True
		response_time=0
		# xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		try:
			# xmlresponse = netw.sendRequest(HERMES_URL_STATUS, "", "get", "", "")
			xmlresponse=requests.get(HERMES_URL_STATUS)
			if xmlresponse.status_code !=200:
				available=False
				response_time=-1
		except:
			available=False
			response_time=-1

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
		#Cal label
		response_time_3=0
		start_3 = time.time()
		labelparamlist ={
			"origin": {
		    "name": "Ithyvan Schreys",
		    "first_name": "",
		    "last_name": "",
		    "phone": "d arnouville",
		    "email": "",
		    "company": "Company Origin",
		    "line1": "32 rue de paradis",
		    "state": "Ile de france",
		    "zipcode": "75010",
		    "country": "France",
		    "country_code": "FR",
		    "city": "Paris",
		    "place_description": "At office"
		  },
		  "destination": {
		    "name": "Maison",
		    "shipment_id": "return_id_at_srb",
		    "first_name": "Leo",
		    "last_name": "Martin",
		    "company": "Company Destination",
		    "line1": "Wilsnacker Str. 52",
		    "line2": "line2",
		    "state": "Helsinki",
		    "zipcode": "00101",
		    "country": "Finland",
		    "country_code": "FI",
		    "phone": "3589635732",
		    "email": "eddy@gmail.com",
		    "city": "Helsinki"
		  },
		  "parcel": {
		    "length_in_cm": 10,
		    "width_in_cm": 10,
		    "height_in_cm": 10,
		    "weight_in_grams": 1700,
		    "content": "This is a contents write by "
		  },
		  "shipment_date": curdate
		  
		}
		try:
			rootdata= self.label(labelparamlist)
		except:
			response_time_3=-1
		if response_time_3 == 0:
			response_time_3 = time.time() - start_3
		allresponseTime.append(response_time_3)
		
		final_responseTime=min(allresponseTime)
		result = {
		    "available": available,
		    "response_time": response_time,
		    "timeout": timeout,
		    "limit": 30000
		}
		return result

	def label(self,userparamlist):
		paramlist = {}
		paramlist["shipment_id"] = ""
		paramlist["partnerid"] = os.environ["HERMES_PATHNERID"]
		paramlist["password"] = os.environ["HERMES_PASSWORD"]

		#default value
		paramlist["destination"]={}
		paramlist["destination"]["name"]=""
		paramlist["destination"]["first_name"]=""
		paramlist["destination"]["last_name"]=""
		paramlist["destination"]["phone"] = ""
		paramlist["destination"]["email"]=""
		paramlist["destination"]["company"] =""
		paramlist["destination"]["street_number"] =""
		paramlist["destination"]["street_name"] =""
		paramlist["destination"]["line1"] =""
		paramlist["destination"]["line2"] =""
		paramlist["destination"]["state"] =""
		paramlist["destination"]["zipcode"]=""
		paramlist["destination"]["country"] =""
		paramlist["destination"]["country_code"] = ""
		paramlist["destination"]["city"] =""
		paramlist["origin"]={}
		paramlist["origin"]["name"] =""
		paramlist["origin"]["phone"] =""
		paramlist["origin"]["email"] =""
		paramlist["origin"]["company"] =""
		paramlist["origin"]["line1"] =""
		paramlist["origin"]["line2"] =""
		paramlist["origin"]["street_name"] =""
		paramlist["origin"]["state"] =""
		paramlist["origin"]["country_code"] =""
		paramlist["origin"]["place_description"] =""
		paramlist["parcel"]={}
		paramlist["parcel"]["length_in_cm"] =""
		paramlist["parcel"]["width_in_cm"] =""
		paramlist["parcel"]["height_in_cm"] =""
		paramlist["parcel"]["weight_in_grams"] =""
		paramlist["shipment_id"]= ""

		req_list=["origin/country","origin/first_name","origin/last_name","origin/street_number","origin/line1","origin/zipcode","origin/city"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			if "street_name" not in paramlist["origin"]:
				paramlist["origin"]["street_name"] =""
			if "street_number" not in paramlist["origin"]:
				paramlist["origin"]["street_number"] = ""
			streetInfo = str(paramlist["origin"]["street_number"])+str(paramlist["origin"]["street_name"])#+str(paramlist["origin"]["line1"])
			data_param ={
				"partnerid":os.environ["HERMES_PATHNERID"],
				"password":os.environ["HERMES_PASSWORD"],
				"country":paramlist["origin"]["country_code"],
				"firstname":paramlist["origin"]["first_name"],
				"lastname":paramlist["origin"]["last_name"],
				"additionalinfo":"",
				"street":streetInfo,
				"housenumber":paramlist["origin"]["street_number"],
				"zipcode":paramlist["origin"]["zipcode"],
				"city":paramlist["origin"]["city"],
				"kdrefno":paramlist["shipment_id"]
			}
		else:
			# return checkparamlist["message"]
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)
		
		
		# responsePrint = netw.sendRequest(HERMES_URL_LABEL, data_param, "postgetcontent", "json", "")
		headers={"Content-Type": "application/json"}
		try:
			responsePrint=requests.post('https://api-return.hermesworld.com/LabelService/V1/getReturnLabel', data=data_param)
		except:
			responseErr = {
	        	"status": 500,
	        	"errors": [
	            	{
	              		"detail": str(responsePrint)
	            	}
	        	]
	        }
			raise Exception(responseErr)
		try:
			d = responsePrint.headers['content-disposition']
			shipmentId = re.sub(r'\s+|\.pdf|.*?\=','',str(d))
		except:
			# return responsePrint.content
			responseErr = {
	        	"status": 500,
	        	"errors": [
	            	{
	              		"detail": str(responsePrint)
	            	}
	        	]
	        }
			raise Exception(responseErr)

		c = boto.connect_s3(os.environ["AWS_S3_KEY1"], os.environ["AWS_S3_KEY2"])
		bucket = c.get_bucket("srbstickers", validate=False)
		name_file = str(time.time()) + ".pdf"
		k = Key(bucket)
		k.key = name_file
		k.contentType="application/pdf"
		k.ContentDisposition="inline"

		with open('/tmp/'+name_file, 'wb') as f:
	 		f.write(responsePrint.content)
	 	
		pathtofile= '/tmp/'+name_file
		k.set_contents_from_filename(pathtofile)

		
		link_pdf = "https://s3-us-west-2.amazonaws.com/srbstickers/" + name_file
		if "destination" and "parcel" in paramlist:
			print("destination and parcel found")
			final_response = {
				"origin": paramlist["origin"],
				"destination": paramlist["destination"],
				"parcel": paramlist["parcel"],
				"carrier_shipment_id": shipmentId,
				"label_url": link_pdf
			}
		elif "destination" in paramlist:
			print('destination found')
			final_response = {
				"origin": paramlist["origin"],
				"destination": paramlist["destination"],
				"carrier_shipment_id": shipmentId,
				"label_url": link_pdf
			}
		elif "parcel" in paramlist:
			print("parcel found")
			final_response = {
				"origin": paramlist["origin"],
				"parcel": paramlist["parcel"],
				"carrier_shipment_id": shipmentId,
				"label_url": link_pdf
			}
		else:
			print("destination and parcel not found")
			final_response = {
				"origin": paramlist["origin"],
				"carrier_shipment_id": shipmentId,
				"label_url": link_pdf
			}
		# final_response = {
		# 	"origin": paramlist["origin"],
		# 	"destination": paramlist["destination"],
		# 	"parcel": paramlist["parcel"],
		# 	"carrier_shipment_id": shipmentId,
		# 	"label_url": link_pdf
		# }

		return final_response