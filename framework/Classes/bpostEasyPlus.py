# -*- coding: utf-8 -*-
from Classes.AbstractService import Service
from Modules.data_converter import data_converter as converter
from Modules.network import networking as netw
import os
import xml.etree.ElementTree as ET
import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import time
from BuiltInService import xmltodict
import datetime
from Modules.data_validator import Validator 
# from lxml import etree

BPOST_EASY_PLUS_URL = os.environ["BPOST_RETURN_LABEL_URI"]
BPOST_CONTRACT_ID = os.environ["BPOST_CONTRACT_ID"] 

class bposteasyplus(Service):
	"""docstring for bposteasyplus"""
	def root(self, paramlist):
		true=True
		false=False
		data={"/": {"get": true},"/type": {"get": true},"/label": {"post": true},"/price": {"post": false},"/status": {"get": true},"tracking":{"get":false}}

		return data

	def status(self, paramlist):
		objfunction=["root","type","label"]
		start = time.time()
		available = True
		allresponseTime=[]
		response_time = 0
		timeout = False
		paramlabel={
		  "origin": {
		    "name": "Ithyvan Schreys",
		    "first_name": "Ithyvan",
		    "last_name": "Schreys",
		    "phone": "0622889977",
		    "email": "eddy@shoprunback.com",
		    "company": "Company Origin",
		    "line1": "12 avenue de la habette",
		    "line2": "",
		    "street_number": "12",
		    "street_name": "avenue de la habette",
		    "state": "",
		    "zipcode": "94000",
		    "country_code": "FR",
		    "city": "CRETEIL"
		  },
		  "destination": {
		    "name": "Leo Martin",
		    "first_name": "Leo",
		    "last_name": "Martin",
		    "company": "Company Destination",
		    "street_number": "59",
		    "street_name": "rue des petits champs",
		    "line1": "59 rue des petits champs",
		    "line2": "",
		    "state": "IDF",
		    "zipcode": "75001",
		    "country_code": "FR",
		    "phone": "0688997788",
		    "email": "",
		    "city": "Paris"
		  },
		  "parcel": {
		    "length_in_cm": 10,
		    "width_in_cm": 10,
		    "height_in_cm": 10,
		    "weight_in_grams": 1950
		  },
		  "shipment_id": "979797",
		  "dropoff": {
		    "point_id": "C10G3"
		  }
		}
		param=""
		for service in objfunction:
			try:
				if service=="label":
					data = self.label(paramlabel)
				elif service =="pickup":
					data =self.pickup(parampickup)
				elif service =="dropoff":
					data = self.dropoff(paramdropoff)
				elif service =="root":
				    data = self.root(param)
				elif service =="type":
					data=self.type(param)
				if response_time == 0:
			  		response_time = time.time() - start
			  		allresponseTime.append(response_time)

				if response_time > 30:
					timeout = True
					available = False
					response_time = -1
					result={
						"available": available,
						"response_time": response_time,
						"timeout": timeout,
						"service":service,
						"limit": 30000
					}
					return result
			except:
				available = False
				response_time = -1
				result={
			  		"available": available,
			  		"response_time": response_time,
			  		"timeout": timeout,
			  		"service":service,
			  		"limit": 30000
			  	}
				return result
		final_responseTime=max(allresponseTime)
		result={
	  		"available": available,
	  		"response_time": final_responseTime,
	  		"timeout": timeout,
	  		"limit": 30000
	  	}
		return result



	def label(sef,userparamlist):
		
		req_list=["destination/line1","destination/zipcode","destination/city","destination/country_code","origin/line1",
		"origin/first_name","origin/last_name","origin/zipcode","origin/city","origin/country_code","shipment_id"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			# event=userparamlist
			reqEmpty=["destination/first_name","destination/last_name"]
			event = instance.jsonCheckEmpty(reqEmpty,userparamlist)
			event["origin"]["name"] = str(event["origin"]["first_name"])+str(event["origin"]["last_name"])
			event["destination"]["name"] = str(event["destination"]["first_name"])+" "+str(event["destination"]["last_name"])

			data_line1= str(event["origin"]["line1"])
			street_info = instance.json_check_line1(data_line1)
			event["origin"]["street_number"]  = street_info["street_number"]
			event["origin"]["street_name"]  =street_info["street_name"]
			if event["origin"]["street_number"]=="":
				event["origin"]["street_number"]="0"

			#destination line1
			dest_line1= event["destination"]["line1"]
			
			street_info = instance.json_check_line1(dest_line1)
			event["destination"]["street_number"]  = street_info["street_number"]
			event["destination"]["street_name"]  =street_info["street_name"]
			if event["destination"]["street_number"]=="":
				event["destination"]["street_number"]="0"
		else:
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)
			# return checkparamlist["message"]

		# full_destination_address = event["destination"]["line1"] + " " + event["destination"]["line2"]
		# full_origin_address = event["origin"]["line1"] + " " + event["origin"]["line2"]
		xmlresult=u"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v001="http://schema.bpost.be/services/service/postal/ExternalMailItemReturnsCSMessages/v001">
	       <soapenv:Header/>
	       <soapenv:Body>
	          <v001:getReturnLabelRequest>
	            <v001:ContractInfo>
	              <v001:ContractID>""" + os.environ["BPOST_CONTRACT_ID"] + """</v001:ContractID>
	            </v001:ContractInfo>
	            <v001:Addressee>
	                <v001:Name>""" + event["destination"]["name"] + """</v001:Name>
	                <v001:Streetname>""" + event["destination"]["street_name"] + """</v001:Streetname>
	                <v001:Streetnumber>""" + event["destination"]["street_number"] + " " + """</v001:Streetnumber>
	                <v001:PostalCode>""" + event["destination"]["zipcode"] + """</v001:PostalCode>
	                <v001:MunicipalityName>""" + event["destination"]["city"] + """</v001:MunicipalityName>
	                <v001:CountryISO2Code>""" + event["destination"]["country_code"] + """</v001:CountryISO2Code>
	            </v001:Addressee>
	            <v001:Sender>
	              <v001:Name>""" + event["origin"]["name"] + """</v001:Name>
	              <v001:Streetname>""" + event["origin"]["street_name"] + """</v001:Streetname>
	              <v001:Streetnumber>""" + event["origin"]["street_number"] + " " + """</v001:Streetnumber>
	              <v001:PostalCode>""" + event["origin"]["zipcode"] + """</v001:PostalCode>
	              <v001:MunicipalityName>""" + event["origin"]["city"] + """</v001:MunicipalityName>
	              <v001:CountryISO2Code>""" + event["origin"]["country_code"] + """</v001:CountryISO2Code>
	            </v001:Sender>
	            <v001:ReturnInfo>
	              <v001:CustomerReference>""" + event["shipment_id"] + """</v001:CustomerReference>
	            </v001:ReturnInfo>
	          </v001:getReturnLabelRequest>
	       </soapenv:Body>
	    </soapenv:Envelope>"""

		headersConfig={'Content-Type': 'text/xml', 'Authorization': ("Basic " + os.environ["BPOST_BASIC_AUTH"]), 'SOAPAction': "http://schema.bpost.be/services/service/postal/ExternalLabelServiceCS/v001/getReturnLabel"}
		
		xmlresponse = netw.sendRequestHeaderConfig(BPOST_EASY_PLUS_URL, xmlresult, "post", headersConfig)
		data = xmltodict.parse(xmlresponse)

		c = boto.connect_s3(os.environ["AWS_S3_KEY1"], os.environ["AWS_S3_KEY2"])
		bucket = c.get_bucket("srbstickers", validate=False)
		name_file = str(time.time()) + ".pdf"
		k = Key(bucket)
		k.key = name_file
		k.contentType="application/pdf"
		k.ContentDisposition="inline"
		# k.set_contents_from_string(data['soapenv:Envelope']['soapenv:Body']['msg:getReturnLabelResponse']['msg:ReturnLabelInfo']['msg:ReturnLabel_PDF'].decode('base64'))
		img_data=data['soapenv:Envelope']['soapenv:Body']['msg:getReturnLabelResponse']['msg:ReturnLabelInfo']['msg:ReturnLabel_PDF']
		k.set_contents_from_string(base64.b64decode(img_data.encode('ascii')))	
	
		try:
			shipment_id = data['soapenv:Envelope']['soapenv:Body']['msg:getReturnLabelResponse']['msg:ReturnLabelInfo']['msg:Leg3']['msg:ItemInfo']['msg:Code']
		except:
			# return xmlresponse
			responseErr = {
				"status": 500,
				"errors": [
					{
						"detail": str(xmlresponse)
					}
				]
			}
			raise Exception(responseErr)

		link_pdf = "https://s3-us-west-2.amazonaws.com/srbstickers/" + name_file

		event["label_url"]=link_pdf
		event["carrier_shipment_id"] = shipment_id
		# if "parcel" in event:
		# 	final_response = {
		# 		"origin": event["origin"],
		# 		"destination": event["destination"],
		# 		"parcel": event["parcel"],
		# 		"carrier_shipment_id": shipment_id,
		# 		"label_url": link_pdf
		# 	}
		# else:
		# 	final_response = {
		# 		"origin": event["origin"],
		# 		"destination": event["destination"],
		# 		"carrier_shipment_id": shipment_id,
		# 		"label_url": link_pdf
		# 	}

		return event

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

		