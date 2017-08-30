from Classes.AbstractService import Service
from BuiltInService import requests 
from Modules.data_converter import data_converter as converter
from Modules.data_validator import Validator 
from Modules.network import networking as netw
from BuiltInService import xmltodict
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
ENVIALIA_URL= os.environ["ENVIALIA_URL"]
ENVIALIA_CODECLI = str(os.environ["ENVIALIA_CODECLI"]) + ""
ENVIALIA_STRCODE = os.environ["ENVIALIA_STRCODE"]
ENVIALIA_PWD = os.environ["ENVIALIA_PWD"]
class envialia(Service):
	"""docstring for envialia"""
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
			"pickup":{
				"post":true
			},
			"pickup/slots":{
				"get":true
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
			"type": "pickup",
			"pickup": true,
			"postal":false,
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
		try:
			responese = netw.sendRequestHeaderConfig(ENVIALIA_URL,'','get','') #self.label(paramlist)
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

		#Cal pickupslots
		response_time_3=0
		start_3 = time.time()
		try:
			rootdata= self.pickupslots(paramlist)
		except:
			response_time_3=-1
		if response_time_3 == 0:
			response_time_3 = time.time() - start_3
		allresponseTime.append(response_time_3)

		#Call pickup
		response_time_4=0
		start_4 = time.time()
		try:
			dataparamlist={
				"origin": {
				    "name": "Rikhil",
				    "phone": "23162",
				    "company": "Saurabh",
				    "line1": "123 Test Ave",
				    "line2": "Test Bus Park",
				    "package_location": "Reception",
				    "city": "PARIS",
				    "zipcode": "75018",
				    "country_code": "FR"
				  },
				  "pickup": {
					"pickup_date": "2017-08-21",
				    "slot_id": "string",
				    "slot_start_at": "10:20",
				    "slot_end_at": "23:20",
				    "number_of_pieces": 0,
				    "special_instructions": "1 palett of 200 kgs - Vehicule avec hayon"
				  },
				  "parcel": {
				    "number_of_pieces": 1,
				    "weight": 200
				  }
			}
			rootdata= self.pickup(dataparamlist)
		except:
			response_time_4=-1
		if response_time_4 == 0:
			response_time_4 = time.time() - start_4
		allresponseTime.append(response_time_4)
		
		final_responseTime=min(allresponseTime)
		result = {
		    "available": available,
		    "response_time": final_responseTime,
		    "timeout": timeout,
		    "limit": 30000
		}
		return result
	
	def login(self,userparamlist):
		xmlresult="""<?xml version="1.0" encoding="utf-8"?>
		<soap:Envelope
			xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
			xmlns:xsd="http://www.w3.org/2001/XMLSchema">
			<soap:Body>
				<LoginWSService___LoginCli>
				    <strCodAge>"""+ENVIALIA_STRCODE+"""</strCodAge>
				    <strCod>"""+ENVIALIA_CODECLI+"""</strCod>
				    <strPass>"""+ENVIALIA_PWD+"""</strPass>
			   	</LoginWSService___LoginCli>
			</soap:Body>
		</soap:Envelope>"""
		xmlresponse = netw.sendRequest(ENVIALIA_URL, xmlresult, "post", "xml", "xml")
		data = xmltodict.parse(xmlresponse)
		try:
			sessionID = data["SOAP-ENV:Envelope"]["SOAP-ENV:Header"]["ROClientIDHeader"]["ID"]
		except:
			responseErr = {
	        	"status": 500,
	        	"errors": [
	            	{
	              		"detail": str(xmlresponse)
	            	}
	        	]
	        }
			raise Exception(responseErr)

		return sessionID


	def pickup(self,userparamlist):
		paramlist = {}
		paramlist["origin"] = {}
		paramlist["origin"]["phone"] = ""
		paramlist["destination"] = {}
		paramlist["destination"]["name"] = ""
		paramlist["destination"]["street_number"] = ""
		paramlist["destination"]["city"] = ""
		paramlist["destination"]["street_name"] = ""
		paramlist["destination"]["city"] = ""
		paramlist["destination"]["zipcode"] = ""
		paramlist["destination"]["phone"] = ""

		#req_list=["pickup/pickup_date","place/line1","pickup/number_of_pieces","requestor/name","place/city","place/zipcode"]
		req_list=["pickup/pickup_date","origin/line1","pickup/number_of_pieces","origin/name","origin/city","origin/zipcode"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			if "destination" in paramlist:
				print ("destnation")
			else:
				paramlist["destination"]= ""
		else:
			# return checkparamlist["message"]
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		pickup_date = re.sub(r'\s.*','',str(paramlist["pickup"]["pickup_date"]))
		pickup_date = re.sub(r'\-','/',str(pickup_date))
		sessionID = self.login(paramlist)
		# return seesionID
		xmldata = """<?xml version="1.0" encoding="utf-8"?>
		<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
			xmlns:xsd="http://www.w3.org/2001/XMLSchema">
			<soap:Header>
				<ROClientIDHeader
					xmlns="http://tempuri.org/">
					<ID>"""+sessionID+"""</ID>
				</ROClientIDHeader>
			</soap:Header>
			<soap:Body>
				<WebServService___GrabaRecogida2 xmlns="http://tempuri.org/">
					<strCodAgeDes>"""+str(ENVIALIA_STRCODE)+"""</strCodAgeDes>
					<strCodAgeCargo>"""+str(ENVIALIA_STRCODE)+"""</strCodAgeCargo>
					<dtFecRec>"""+pickup_date+"""</dtFecRec>
					<intBul>"""+str(paramlist["pickup"]["number_of_pieces"])+"""</intBul>
					<strNomOri>"""+paramlist["origin"]["name"]+"""</strNomOri>
					<strDirOri>"""+str(paramlist["origin"]["street_number"])+str(paramlist["origin"]["street_name"])+str(paramlist["origin"]["line1"])+"""</strDirOri>
					<strPobOri>"""+paramlist["origin"]["city"]+"""</strPobOri>
					<strCPOri>"""+str(paramlist["origin"]["zipcode"])+"""</strCPOri>
					<strTlfOri>"""+str(paramlist["origin"]["phone"])+"""</strTlfOri>
					<strNomDes>Envialia</strNomDes>
					<strDirDes>Avenida de Suiza, 2</strDirDes>
					<strPobDes>Madrid</strPobDes>
					<strCPDes>28821</strCPDes>
					<strTlfDes>+34914573361</strTlfDes>
					<strCodCli>"""+str(ENVIALIA_CODECLI)+"""</strCodCli>
					<strCodTipoServ>E24</strCodTipoServ>
					
				</WebServService___GrabaRecogida2>
			</soap:Body>
		</soap:Envelope>"""
		xmlresponse = netw.sendRequest(ENVIALIA_URL, xmldata, "post", "xml", "xml")
		data = xmltodict.parse(xmlresponse)
		try:
			pickup_id = data["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]["v1:WebServService___GrabaRecogida2Response"]["v1:strCodOut"]
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

		if paramlist["destination"]:
			final_data={
				"origin":paramlist["origin"],
				"pickup":paramlist["pickup"],
				"shipment_details":paramlist["parcel"],
				"destination":paramlist["destination"],
				"pickup_id":pickup_id
			}
		else:
			final_data={
				"origin":paramlist["origin"],
				"pickup":paramlist["pickup"],
				"shipment_details":paramlist["parcel"],
				"pickup_id":pickup_id
			}

		return final_data

	def pickupslots(self, paramlist):
		print ("pickupslots from envialia")
		date = datetime.datetime.now()
		alldays=[]
		for l in range(7):
			date += datetime.timedelta(days=1)
			if date.isoweekday()==6:
				date += datetime.timedelta(days=2)
				print ("saturday +2: "+str(date))
			elif date.isoweekday()==7:
				date += datetime.timedelta(days=1)
				print ("sunday +1: "+str(date))
			else:
				print ("no check")
			newdate=re.sub(r'\s.*',' ',str(date))
			# fullstartdate1=str(newdate)+" 10:00:00:000Z"
			# fullstartdate2=str(newdate)+" 14:00:00:000Z"
			fullstartdate1="10:00:00"
			fullstartdate2="14:00:00"
			data={
		        "date": str(date),
		        "slots": [
			        {
						"start_time": fullstartdate1,
				        "duration": "240",
				        "availability": -1
					},
					{
						"start_time": fullstartdate2,
				        "duration": "240",
				        "availability": -1
					}
				]
			}
			alldays.append(data)
		return alldays