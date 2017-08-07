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
# import cloudinary
# import cloudinary.uploader
# import cloudinary.api
# cloudinary.config( 
#   cloud_name = "dozjp3am8", 
#   api_key = "714151172147688", 
#   api_secret = "fJBHf8VSu3q2-rkgcE7M9K92too" 
# )
HERMES_URL_LABEL = os.environ["HERMES_URL_LABEL"]
HERMES_URL_STATUS = os.environ["HERMES_URL_STATUS"]


class hermes(Service):
	"""docstring for hermes"""
	def root(self,userparamlist):
		true=True
		data={
			"/":{
				"get":true
			},
			"type":{
				"get":true
			},
			"label":{
				"get":true
			},
			"status":{
				"get":true
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
		# date = datetime.datetime.now()
		# datenow=re.sub(r'\s.*','',str(date))
		# tree = ET.parse('Assets/royalmail/requests/createshipment.txt')
		# root = tree.getroot()
		
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

		result = {
		    "available": available,
		    "response_time": response_time,
		    "timeout": timeout,
		    "limit": 30000
		}
		return result

	def label(self,userparamlist):
		paramlist = {}
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
		paramlist["origin"]["state"] =""
		paramlist["origin"]["country_code"] =""
		paramlist["origin"]["place_description"] =""
		paramlist["parcel"]={}
		paramlist["parcel"]["length_in_cm"] =""
		paramlist["parcel"]["width_in_cm"] =""
		paramlist["parcel"]["height_in_cm"] =""
		paramlist["parcel"]["weight_in_grams"] =""


		req_list=["origin/country","origin/first_name","origin/last_name","origin/street_number","origin/zipcode","origin/city"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			data_param ={
				"partnerid":os.environ["HERMES_PATHNERID"],
				"password":os.environ["HERMES_PASSWORD"],
				"country":paramlist["origin"]["country"],
				"firstname":paramlist["origin"]["first_name"],
				"lastname":paramlist["origin"]["last_name"],
				"additionalinfo":"",
				"street":paramlist["origin"]["street_number"],
				"housenumber":"empty",
				"zipcode":paramlist["origin"]["zipcode"],
				"city":paramlist["origin"]["city"],
				"kdrefno":""
			}
		else:
			return checkparamlist["message"]
		
		
		responsePrint = netw.sendRequest(HERMES_URL_LABEL, data_param, "postgetcontent", "json", "")
		# data =cloudinary.uploader.upload(responsePrint.content)
		# link_pdf = data["url"]
		c = boto.connect_s3(os.environ["AWS_S3_KEY1"], os.environ["AWS_S3_KEY2"])#boto.connect_s3('AKIAJKZ7KCBQFGFGD2ZA', '2HM3b8GPRMQFb4B86pokgXpk6A6bESo7R3NRRw61')
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
		final_response = {
			"origin": paramlist["origin"],
			"destination": paramlist["destination"],
			"parcel": paramlist["parcel"],
			"shipment_id": "shipment_id",
			"label_url": link_pdf
		}

		return final_response