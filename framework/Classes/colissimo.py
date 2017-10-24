from Classes.AbstractService import Service
from Modules.data_converter import data_converter as converter
from Modules.network import networking as netw
from Modules.data_validator import Validator 
from BuiltInService import requests
from BuiltInService import xmltodict
import os
import time
import datetime
import json
import re

import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
responese =""
class colissimo(Service):

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
				"post":false
			},
			"pickup":{
				"post":true
			},
			"tracking":{
				"get":true
			}

		}
		return data

	def status(self,paramlist):
		paramtraking ="8R30646307058"
		paramlabel={
			"origin":{
				"country_code": "FR",
				"line1": "main address",
				"zipcode": "75007",
				"city": "Paris",
				"company": "companyName"
			},
			"destination":{
				"last_name": "lastName",
				"first_name": "firstName",
				"line1": "main address",
				"country_code": "FR",
				"city": "Paris",
				"zipcode": "75017",
				"company":"shoprunback"
			}
		}

		objfunction=["root","type","label","tracking"]
		instance = Validator()
		api_url_request = os.environ["API_DEVEVELOPER_URL"]
		result = instance.get_all_status("colissimo",api_url_request,objfunction,paramlabel,"","",paramtraking,"")
		return result

		

	def type(self,paramlist):
		print("type")
		true=True
		false=False
		data={"type": "pickup","postal": false,"pickup": true,"dropoff": false,"linehaul": false}
		return data

	def label(self,userparamlist):
		date = datetime.datetime.now()
		curdate = re.sub(r'\s.*','',str(date))
		COLISSIMO_LABEL_URL =  os.environ["COLISSIMO_LABEL_URL"]
		COLISSIMO_PASSWORD = os.environ["COLISSIMO_PASSWORD"]
		COLISSIMO_CONTRACTNUMBER = os.environ["COLISSIMO_CONTRACTNUMBER"]

		req_list=["origin/line1","origin/country_code","origin/zipcode","origin/city","origin/company","destination/first_name","destination/last_name","destination/country_code","destination/city","destination/zipcode","destination/company","destination/line1"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			# reqEmpty=["origin/line2","destination/line2"]
			# paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
		else:
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		try:
			response = requests.post(
			    url= COLISSIMO_LABEL_URL,
			    headers={
			        "Content-Type": "application/json; charset=utf-8",
			    },
			    data=json.dumps({
			        "password": COLISSIMO_PASSWORD,#"quai77", #shop75
			        "outputFormat": {
			            "x": "0",
			            "y": "0",
			            "outputPrintingType": "PDF_10x15_300dpi"
			        },
			        "contractNumber": COLISSIMO_CONTRACTNUMBER,#"816721", #963250
			        "letter": {
			            "sender": {
			                "address": {
			                    "countryCode": paramlist["origin"]["country_code"],
			                    "line2": paramlist["origin"]["line1"],
			                    "zipCode": paramlist["origin"]["zipcode"],
			                    "city": paramlist["origin"]["city"],
			                    "companyName": paramlist["origin"]["company"]
			                }
			            },
			            "parcel": {
			                "weight": "1"
			            },
			            "addressee": {
			                "address": {
			                    "lastName": paramlist["destination"]["last_name"],
			                    "firstName": paramlist["destination"]["first_name"],
			                    "line2": paramlist["destination"]["line1"],
			                    "countryCode": paramlist["destination"]["country_code"],
			                    "city": paramlist["destination"]["city"],
			                    "zipCode": paramlist["destination"]["zipcode"],
			                    "companyName":paramlist["destination"]["company"]
			                }
			            },
			            "service": {
			                "depositDate": curdate,
			                "productCode": "CORE"
			            }
			        }
			    }),
			timeout=30)
	       
			name_file = str(time.time()) + ".pdf"
			getpdf=re.sub(r'(.*?pdfUrl\"\:)(\".*?\")(.*)',r'\2',str(response.content))
			getpdf =re.sub(r'\"','',str(getpdf))
			c = boto.connect_s3(os.environ["S3_KEY1"], os.environ["S3_KEY2"])
			b = c.get_bucket("srbstickers", validate=False)

			k = Key(b)
			k.key = name_file
			k.contentType="application/pdf"
			k.ContentDisposition="inline"
			# k.set_contents_from_string(img_data.decode('base64'))
			r = requests.get(getpdf)
			img_data = r.content
			k.set_contents_from_string(img_data)
			link_pdf="https://s3-us-west-2.amazonaws.com/srbstickers/"+name_file
			paramlist["label_url"] = link_pdf

		except requests.exceptions.RequestException:
			print('HTTP Request failed')
			paramlist={"status": 400,"errors": [{"detail":"HTTP Request failed" }]}

		return paramlist

	def tracking(self,paramlist):
		print("tracking colisimo")
		tracking_id = str(paramlist) #8R30646307058
		accountNumber = "816721"
		password = "quai77"
		url =os.environ["COLISSIMO_URL_TRACKING"]  #"https://www.coliposte.fr/tracking-chargeur-cxf/TrackingServiceWS"

		xmldata="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:char="http://chargeur.tracking.geopost.com/">
		   <soapenv:Header/>
		   <soapenv:Body>
		      <char:track>
		         <!--Optional:-->
		         <accountNumber>"""+accountNumber+"""</accountNumber>
		         <!--Optional:-->
		         <password>"""+password+"""</password>
		         <!--Optional:-->
		         <skybillNumber>"""+tracking_id+"""</skybillNumber>
		      </char:track>
		   </soapenv:Body>
		</soapenv:Envelope>"""
		headers = {'Content-Type': 'application/xml'}
		# try:
		# 	resp = requests.post(url=url, data=xmldata, headers=headers)
		# except:
		# 	return resp.content
		xmlresponse = netw.sendRequest(url, xmldata, "post", "xml", "xml")
		data = xmltodict.parse(xmlresponse)
		# resp = requests.post(url=url, data=xmldata, headers=headers)
		# return resp.content
		try:
			status = data["soap:Envelope"]["soap:Body"]["ns1:trackResponse"]["return"]["eventLibelle"]
			location = data["soap:Envelope"]["soap:Body"]["ns1:trackResponse"]["return"]["eventCode"]
		except:
			return xmlresponse

		dt =[{
			"status":status,
			"steps": [
				{
					"status": status,
					"location": location
				}
			]
		}]
		return dt