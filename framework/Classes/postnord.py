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

class postnord(Service):
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
				"post":true
			},
			"pickup":{
				"post":false
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
		data={"type": "pickup","postal": false,"label": true,"dropoff": false,"linehaul": false}
		return data

	def status(self,paramlist):
		allresponseTime=[]
		paramlist=""
		start=time.time()
		available=True
		response_time=0
		try:
			myparamlist={
				"destination": {
				    "name": "abprufen GMB",
				    "company": "string",
				    "street_number": "string",
				    "street_name": "string",
				    "line1": "haupstrasse 34",
				    "state": "string",
				    "country": "danmark",
				    "phone": "123 456 789",
				    "email": "string",
					"last_name": "abprufen GMB",
					"first_name": "GMB",
					"line2": "",
					"country_code": "FR",
					"city": "Haderslev",
					"zipcode": "6100"
				},
				"parcel": {
				    "length_in_cm": 10,
				    "width_in_cm": 10,
				    "height_in_cm": 10,
				    "weight_in_grams": 1000,
					"contents":"tshirt",
				    "number_of_pieces": 0
				}
			}

			responese = self.label(myparamlist)
		except:
			available=False
			response_time=-1

		# responese = self.label(myparamlist)

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

	def label(self,userparamlist):
		req_list=["destination/first_name","destination/last_name","destination/line1","destination/zipcode","destination/city","destination/phone","parcel/weight_in_grams","parcel/contents"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			reqEmpty=["destination/last_name"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
			paramlist["destination"]["name"]= paramlist["destination"]["first_name"]+paramlist["destination"]["last_name"]
		else:
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		url="http://booking.parcelfeeder.dk:8888/post?task=&"
		username = "Shoprun"
		password = "123"
		weight = int(paramlist["parcel"]["weight_in_grams"])/1000
		# task=&Uid=Shoprun&Pwd=123&Mnavn=abprufen GMBH&Madr=haupstrasse 34&Mland=danmark&Mzip=6100&Mby=Haderslev&Matt=friderick schultz&Mtlf=123 456 789&Service=PostNord Parcel&weight=1&Sref=order 12345&Mref=rekv.123&content=Shirt"
		fullurl =str(url+"Uid="+username+"&Pwd="+password+"&Mnavn="+paramlist["destination"]["first_name"]+paramlist["destination"]["last_name"]+"&Madr="+paramlist["destination"]["line1"]+"&Mland="+paramlist["destination"]["country"]+"&Mzip="+paramlist["destination"]["zipcode"]+"&Mby="+paramlist["destination"]["city"]+"&Matt="+paramlist["destination"]["name"]+"&Mtlf="+paramlist["destination"]["phone"]+"&Service="+"PostNord Parcel"+"&weight="+str(weight)+"&Sref=default &Mref=default &content=default")

		# urlresp = netw.sendRequest(fullurl, "", "get", "", "")
		try:
			urlresp = requests.get(fullurl)
		except:
			return urlresp
		pdfurl =urlresp.text
		name_file = str(time.time()) + ".pdf"
		c = boto.connect_s3(os.environ["S3_KEY1"], os.environ["S3_KEY2"])
		b = c.get_bucket("srbstickers", validate=False)
		k = Key(b)
		k.key = name_file
		k.contentType="application/pdf"
		k.ContentDisposition="inline"
		r = requests.get(pdfurl)#netw.sendRequest(pdfurl, "", "get", "", "")
		img_data = r.content
		k.set_contents_from_string(img_data)
		link_pdf="https://s3-us-west-2.amazonaws.com/srbstickers/"+name_file
		paramlist["label_url"] = link_pdf
		return paramlist