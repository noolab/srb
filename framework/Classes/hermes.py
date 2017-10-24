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
		paramtraking={}
		parampickup={}
		paramlabel ={
			"origin": {
		    "name": "Ithyvan Schreys",
		    "first_name": "Ithyvan",
		    "last_name": "Schreys",
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
		    "contents": "This is a contents write by "
		  },
		  "shipment_date": curdate
		  
		}
		paramdropoff={
			"name": "DDDD",
			"first_name": "string",
			"last_name": "string",
			"company": "string",
			"housenumber":"22",
			"street_number": "string",
			"street_name": "string",
			"line1": "Hamburg, Freie und Hansestadt",
			"line2": "string",
			"state": "string",
			"zipcode": "10587",
			"city": "Berlin",
			"country_code": "DE",
			"phone": "string",
			"email": "string",
			"latitude":" 53.548",
			"longitude":"10.019"
		}
		objfunction=["root","type","label","dropoff/points"]
		instance = Validator()
		api_url_request = os.environ["API_DEVEVELOPER_URL"]
		result = instance.get_all_status("hermes",api_url_request,objfunction,paramlabel,parampickup,paramdropoff,paramtraking,"")
		return result
			
		

	def label(self,userparamlist):

		req_list=["shipment_id","origin/country_code","origin/first_name","origin/last_name","origin/line1","origin/zipcode","origin/city"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			data_line1= str(userparamlist["origin"]["line1"])
			street_info = instance.json_check_line1(data_line1)
			userparamlist["origin"]["street_number"]  = street_info["street_number"]
			userparamlist["origin"]["street_name"]  =street_info["street_name"]
			if userparamlist["origin"]["street_number"]=="":
				userparamlist["origin"]["street_number"]="0"

			reqEmpty=["shipment_id","parcel/weight_in_grams","parcel/height_in_cm","parcel/width_in_cm","parcel/length_in_cm","origin/state","origin/line2","origin/line1","origin/company","origin/email","origin/phone",
					"destination/city","destination/country","destination/country_code","destination/zipcode","destination/state","destination/line2","destination/line1",
					"destination/company","destination/email","destination/phone","destination/first_name","destination/last_name"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)


			streetInfo = str(paramlist["origin"]["street_number"])+str(paramlist["origin"]["street_name"])#+str(paramlist["origin"]["line1"])
			data_param ={
				"partnerid":os.environ["HERMES_PATHNERID"],
				"password":os.environ["HERMES_PASSWORD"],
				"country":paramlist["origin"]["country_code"],
				"firstname":paramlist["origin"]["first_name"],
				"lastname":paramlist["origin"]["last_name"],
				"additionalinfo":"",
				"street":paramlist["origin"]["street_name"],
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

		# return responsePrint
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


	def dropoff(self,userparamlist):
		consumerName = os.environ["HERMES_DROPOFF_CONSUMERNAME"] #" EXT002361"
		consumerPassword= os.environ["HERMES_DROPOFF_CONSUMERPASSWORD"]#'e2b0762a75603b097fc269a3df0c1438668b0f7a472f524a134b17f911332563'
		dropoff_url=os.environ["HERMES_DROPOFF_URL"]#'https://psfinder.hermesworld.com/psfinder-rest-api-impl/rest/findParcelShopsByLocation?'
		
		req_list=["zipcode","city","country_code"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			# street =paramlist["line1"]
			postcode=paramlist["zipcode"]
			city= paramlist["city"]
			countries = paramlist["country_code"]

		else:
			# return checkparamlist["message"]
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)
		fullurl= dropoff_url+'consumerName='+consumerName+'&'+'consumerPassword='+consumerPassword+'&'+'postcode='+postcode+'&'+'city='+city+'&'+'countries='+countries
		# fullurl= dropoff_url+'consumerName='+consumerName+'&'+'consumerPassword='+consumerPassword+'&''+'postcode='+postcode+'&'+'city='+city+'&'&'+'countries='+countries
		response = netw.sendRequestHeaderConfig(fullurl,"","get","")

		data = json.loads(response.text)
		result = []
		for da in data:
			openning =[]
			for op in da["businessHours"]:
				optime={
					"start_at":op["openFrom"],
					"end_at":op["openTill"]
				}
				openning.append(optime)

			res = {
			    "name": da["shopOwner"],
			    "latitude": 0,
			    "longitude": 0,
			    "street_number": "",
			    "street_name": da["address"]["street"],
			    "line1":  da["address"]["street"],
			    "line2": "",
			    "state": "",
			    "zipcode": da["address"]["postCode"],
			    "city": da["address"]["city"],
			    "country_code": "",
			    "logo_url": "",
			    "id": da["parcelShopNumber"],
			    "booking_reference": "",
			    "opening": openning
			}
			result.append(res)

		return result