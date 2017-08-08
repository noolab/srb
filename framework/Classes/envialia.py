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
ENVIALIA_URL= os.environ["ENVIALIA_URL"]
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
			"pickup": true,
			"label": true,
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
	
	def login(self):
		# tree = ET.parse('Assets/envialia/requests/loginxml.txt')
		# root = tree.getroot()
		# with open("Assets/envialia/requests/loginxml.txt") as data_file:
		# 	xmldic_data=xmltodict.parse(data_file.read())
		
		# xmldic_data["soap:Envelope"]["soap:Body"]["LoginWSService___Login"]["strCod"] = "1111111"
		# xmldic_data["soap:Envelope"]["soap:Body"]["LoginWSService___Login"]["strPass"] = "1111111"
		# data=xmldic_data["soap:Envelope"]["soap:Body"]["LoginWSService___Login"]["strCod"]
		# root.find("LoginWSService___Login/strCod").text = ""
		# root.find("LoginWSService___Login/strPass").text = ""
		xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		xmlresponse = netw.sendRequest(ENVIALIA_URL, xmlresult, "post", "", "xml")
		data = xmltodict.parse(xml)
		try:
			sessionID = data["SOAP-ENV:Envelope"]["SOAP-ENV:Header"]["ROClientIDHeader"]["ID"]
		except:
			return responsePrint

		return sessionID


	def pickup(self,paramlist):
		sessionID = self.login()
		xmldata = """<?xml version="1.0" encoding="utf-8"?>
		<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
			xmlns:xsd="http://www.w3.org/2001/XMLSchema">
			<soap:Header>
				<ROClientIDHeader
					xmlns="http://tempuri.org/">
					<ID>"""+seesionID+"""</ID>
				</ROClientIDHeader>
			</soap:Header>
			<soap:Body>
				<WebServService___GrabaRecogida2
					xmlns="http://tempuri.org/">
					<strCod>WS003</strCod>
					<strCodAgeOri></strCodAgeOri>
					<strCodAgeDes></strCodAgeDes>
					<strCodAgeCargo></strCodAgeCargo>
					<dtFecRec></dtFecRec>
					<dtHoraRecIni></dtHoraRecIni>
					<dtHoraRecIniTarde></dtHoraRecIniTarde>
					<dtHoraRecFin></dtHoraRecFin>
					<dtHoraRecFinTarde></dtHoraRecFinTarde>
					<intBul></intBul>
					<dPeso></dPeso>
					<dValor></dValor>
					<dAnticipo></dAnticipo>
					<strCodVeh></strCodVeh>
					<strNomOri></strNomOri>
					<strTipoViaOri></strTipoViaOri>
					<strDirOri></strDirOri>
					<strNumOri></strNumOri>
					<strPisoOri></strPisoOri>
					<strPobOri></strPobOri>
					<strCPOri></strCPOri>
					<strTlfOri></strTlfOri>
					<strCodProOri></strCodProOri>
					<strNomDes></strNomDes>
					<strTipoViaDes>--tipo-via-destino</strTipoViaDes>
					<strDirDes></strDirDes>
					<strNumDes></strNumDes>
					<strPisoDes></strPisoDes>
					<strPobDes></strPobDes>
					<strCPDes></strCPDes>
					<strTlfDes></strTlfDes>
					<strCodProDes></strCodProDes>
					<strObs></strObs>
					<strCodCli></strCodCli>
					<strCodCliDep></strCodCliDep>
					<strPersContacto></strPersContacto>
					<boAutKM></boAutKM>
					<strCodTipoServ></strCodTipoServ>
					<boSabado></boSabado>
					<strCodRep></strCodRep>
					<strCodEnv></strCodEnv>
					<strRef></strRef>
					<strTipoRecOld></strTipoRecOld>
					<strObsDes></strObsDes>
					<dRefund.></dRefund.>
					<dCobCli></dCobCli>
					<dImpuesto></dImpuesto>
					<dBaseImp></dBaseImp>
					<boAcuse></boAcuse>
					<boRetorno></boRetorno>
					<boGestOri></boGestOri>
					<boGestDes></boGestDes>
					<strCodPais></strCodPais>
					<boRemSMS></boRemSMS>
					<boRemEmail></boRemEmail>
					<strRemMoviles></strRemMoviles>
					<strRemDirEmails></strRemDirEmails>
					<boRemAlta></boRemAlta>
					<boRemInci></boRemInci>
					<boRemResInci></boRemResInci>
					<boRemRep></boRemRep>
					<boDesSMS></boDesSMS>
					<boDesEmail></boDesEmail>
					<strDesMoviles></strDesMoviles>
					<strDesDirEmails></strDesDirEmails>
					<boDesAlta></boDesAlta>
					<boDesFin></boDesFin>
					<boDesInci></boDesInci>
					<boDesResInci></boDesResInci>
					<boDesRep></boDesRep>
					<strCampo1></strCampo1>
					<strCampo2></strCampo2>
					<strCampo3></strCampo3>
					<strCampo4></strCampo4>
					<boCampo5></boCampo5>
				</WebServService___GrabaRecogida2>
			</soap:Body>
		</soap:Envelope>"""


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