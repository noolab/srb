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
		data={
			"/":{
				"get":true
			},
			"type":{
				"get":true
			},
			"pickup":{
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
			"type": "pickup",
			"pickup": true,
			"postal":false,
			"dropoff": false,
			"linehaul": false
		}
		return data
	def status(self,paramlist):
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

		result = {
		    "available": available,
		    "response_time": response_time,
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
			return xmlresponse

		return sessionID


	def pickup(self,userparamlist):
		paramlist = {}
		paramlist["requestor"] = {}
		paramlist["requestor"]["phone"] = ""
		paramlist["destination"] = {}
		paramlist["destination"]["name"] = ""
		paramlist["destination"]["street_number"] = ""
		paramlist["destination"]["city"] = ""
		paramlist["destination"]["street_number"] = ""
		paramlist["destination"]["city"] = ""
		paramlist["destination"]["zipcode"] = ""
		paramlist["destination"]["phone"] = ""

		req_list=["pickup/pickup_date","place/line1","pickup/number_of_pieces","requestor/name","place/street_number","place/city","place/post_code"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			if "destination" in paramlist:
				print ("destnation")
			else:
				paramlist["destination"]= ""
		else:
			return checkparamlist["message"]

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
					<strNomOri>"""+paramlist["requestor"]["name"]+"""</strNomOri>
					<strDirOri>"""+str(paramlist["place"]["street_number"])+str(paramlist["place"]["line1"])+"""</strDirOri>
					<strPobOri>"""+paramlist["place"]["city"]+"""</strPobOri>
					<strCPOri>"""+str(paramlist["place"]["post_code"])+"""</strCPOri>
					<strTlfOri>"""+str(paramlist["requestor"]["phone"])+"""</strTlfOri>
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
			return xmlresponse
		if paramlist["destination"]:
			final_data={
				"requestor":paramlist["requestor"],
				"place":paramlist["place"],
				"pickup":paramlist["pickup"],
				"shipment_details":paramlist["shipment_details"],
				"destination":paramlist["destination"],
				"pickup_id":pickup_id
			}
		else:
			final_data={
				"requestor":paramlist["requestor"],
				"place":paramlist["place"],
				"pickup":paramlist["pickup"],
				"shipment_details":paramlist["shipment_details"],
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
			fullstartdate1=str(newdate)+" 10:00:00:000Z"
			fullstartdate2=str(newdate)+" 14:00:00:000Z"
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