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
		paramlabel={}
		paramtraking={}
		parampickup={
			"origin": {
			    "first_name": "Rikhil",
			    "last_name":"Rikhil",
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
				"date": "2017-08-21",
			    "slot_id": "string",
			    "slot_start_at": "10:20",
			    "slot_end_at": "23:20",
			    "number_of_pieces": 0,
			    "special_instructions": "1 palett of 200 kgs - Vehicule avec hayon"
			  },
			  "parcel": {
			    "number_of_pieces": 1,
			    "weight_in_grams": 200
			  }
		}
		objfunction=["root","type","pickup"]
		instance = Validator()
		api_url_request = os.environ["API_DEVEVELOPER_URL"]
		result = instance.get_all_status("envialia",api_url_request,objfunction,paramlabel,parampickup,"",paramtraking,"")
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
		
		#req_list=["pickup/pickup_date","place/line1","pickup/number_of_pieces","requestor/name","place/city","place/zipcode"]
		req_list=["pickup/date","origin/line1","parcel/number_of_pieces","origin/first_name","origin/last_name","origin/city","origin/zipcode"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			reqEmpty=["origin/phone","destination/street_number","destination/line1","destination/phone","destination/city","destination/zipcode"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
			paramlist["origin"]["name"] = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])

			data_line1= str(paramlist["origin"]["line1"])
			street_info = instance.json_check_line1(data_line1)
			paramlist["origin"]["street_number"]  = street_info["street_number"]
			paramlist["origin"]["street_name"]  =street_info["street_name"]
			if paramlist["origin"]["street_number"]=="":
				paramlist["origin"]["street_number"]="0"

		else:
			# return checkparamlist["message"]
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		pickup_date = re.sub(r'\s.*','',str(paramlist["pickup"]["date"]))
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
					<intBul>"""+str(paramlist["parcel"]["number_of_pieces"])+"""</intBul>
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
		        "date": str(newdate),
		        "timezone":False,
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