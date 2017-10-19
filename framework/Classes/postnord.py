# from Classes.generalclass import ServiceGeneral
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
		objfunction=["root","type","label"]
		paramlabel={
		  "origin": {
		    "first_name": "Ithyvan",
		    "last_name": "Schreys",
		    "phone": "0622889977",
		    "company": "Company Origin",
		    "line1": "11 avenue de la habette",
		    "zipcode": "94000",
		    "country_code": "DK",
		    "city": "CRETEIL"
		  },
		  "destination": {
		    "first_name": "Leo",
		    "last_name": "Martin",
		    "company": "Company Destination",
		    "line1": "59 rue des petits champs",
		    "zipcode": "75001",
		    "country_code": "DK",
		    "phone": "0688997788",
		    "city": "Paris"
		  },
		  "parcel": {
		    "length_in_cm": 10,
		    "width_in_cm": 10,
		    "height_in_cm": 10,
		    "weight_in_grams": 1950,
		    "contents": "It contains 2 T-shirts"
		  },
		  "shipment_id": "9999"
		}
		# instance = Validator()
		# result = instance.check_status("postnord",objfunction,paramlabel,"","")
		# return result
		

	def label(self,userparamlist):
		req_list=["destination/first_name","destination/last_name","destination/phone","destination/line1","destination/zipcode","destination/city","destination/country_code","destination/phone","parcel/weight_in_grams","parcel/contents"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			reqEmpty=["destination/last_name"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
			paramlist["destination"]["name"]= str(paramlist["destination"]["first_name"])+" "+str(paramlist["destination"]["last_name"])
		else:
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		url=os.environ["POSTNORD_LABEL_URL"] 
		username = os.environ["POSTNORD_USERNAME"]
		password = os.environ["POSTNORD_PASSWORD"]
		weight = int(paramlist["parcel"]["weight_in_grams"])/1000
		# task=&Uid=Shoprun&Pwd=123&Mnavn=abprufen GMBH&Madr=haupstrasse 34&Mland=danmark&Mzip=6100&Mby=Haderslev&Matt=friderick schultz&Mtlf=123 456 789&Service=PostNord Parcel&weight=1&Sref=order 12345&Mref=rekv.123&content=Shirt"
		fullurl =str(url+"Uid="+username+"&Pwd="+password+"&Mnavn="+paramlist["destination"]["first_name"]+paramlist["destination"]["last_name"]+"&Madr="+paramlist["destination"]["line1"]+"&Mland="+paramlist["destination"]["country_code"]+"&Mzip="+paramlist["destination"]["zipcode"]+"&Mby="+paramlist["destination"]["city"]+"&Matt="+paramlist["destination"]["name"]+"&Mtlf="+paramlist["destination"]["phone"]+"&Service="+"PostNord Parcel"+"&weight="+str(weight)+"&Sref=default &Mref=default &content=default")

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