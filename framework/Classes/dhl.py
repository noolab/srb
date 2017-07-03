from Classes.AbstractService import Service
from BuiltInService import requests
# from BuiltInService 
# from ..BuiltInService 
import re
import time
import datetime
# from BuiltInService 
import xml.etree.ElementTree as ET
from Modules.data_converter import data_converter as converter
from Modules.data_validator import Validator 
from Modules.network import networking as netw
# from BuiltInService
import json
import os
from random import randrange

import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection


DHL_URL = os.environ["DHL_URL"]  #"https://xmlpitest-ea.dhl.com/XMLShippingServlet"
# netw = networking()
class dhl(Service):	
	
	def root(self,paramlist):
		true=True
		data={
			"/":{
				"get":true
			},
			"type":{
				"get":true
			},
			"pickup/slots":{
				"get":true
			},
			"price":{
				"get":true
			},
			"status":{
				"get":true
			}
		}
		return data
		

	def pickup(self, userparamlist):
		paramlist={}
		paramlist["place"]={}
		paramlist["requestor"]={}
		paramlist["shipment_details"]={}
		paramlist["place"]["line2"]=""
		paramlist["place"]["post_code"]=""
		paramlist["requestor"]["name"] =""
		paramlist["requestor"]["phone"]="" 
		paramlist["shipment_details"]["number_of_pieces"]=""
		instance = Validator()
		req_list=["pickup/pickup_date","pickup/ready_by_time","pickup/close_time","requestor/company","place/line1","place/package_location",
		"place/city","place/country_code","shipment_details/weight"]
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
		else:
			return checkparamlist["message"]
			


		# STEP 1: Load "request object parameter" from assets (can be xml or json) 
		tree = ET.parse('Assets/dhl/requests/003_Pickup.txt')
		root = tree.getroot()

		# STEP 2: set value to object property
		datenow=str(datetime.datetime.now())
		datenow=re.sub(r'\..*','',datenow)
		messageReference=str(randrange(0,10000000000000000000000000000000))
		messageTime=str(datenow)+"T11:28:56.000-08:00"
		root.find("Request/ServiceHeader/MessageTime").text = messageTime
		root.find("Request/ServiceHeader/MessageReference").text = messageReference

		root.find("Request/ServiceHeader/SiteID").text = os.environ["DHL_USERID"]
		root.find("Request/ServiceHeader/Password").text = os.environ["DHL_PWD"]

		root.find("Pickup/PickupDate").text = paramlist["pickup"]["pickup_date"]   #paramlist["pickup_date"] # "2017-05-26"
		root.find("Pickup/ReadyByTime").text = paramlist["pickup"]["ready_by_time"] #paramlist["ready_by_time"] # "10:20"
		root.find("Pickup/CloseTime").text = paramlist["pickup"]["close_time"]  #paramlist["close_time"] # "14:20"
		
		root.find("Place/CompanyName").text = paramlist["requestor"]["company"]
		root.find("Place/Address1").text = paramlist["place"]["line1"]
		root.find("Place/Address2").text = paramlist["place"]["line2"] 
		root.find("Place/PackageLocation").text = paramlist["place"]["package_location"] 
		root.find("Place/City").text = paramlist["place"]["city"] 
		root.find("Place/CountryCode").text = paramlist["place"]["country_code"] 
		root.find("Place/PostalCode").text = paramlist["place"]["post_code"] 

		root.find("PickupContact/PersonName").text = paramlist["requestor"]["name"] 
		root.find("PickupContact/Phone").text = paramlist["requestor"]["phone"] 

		root.find("ShipmentDetails/NumberOfPieces").text = str(paramlist["shipment_details"]["number_of_pieces"])
		root.find("ShipmentDetails/Weight").text = str(paramlist["shipment_details"]["weight"])

		# more variable can be set to xml here ... 

		xmlresult = ET.tostring(root, encoding='ascii', method='xml')

		# STEP 3: 	REQUEST DATA
		# the 2 following lines are called when accessing real data from http
		xmlresponse = netw.sendRequest(DHL_URL, xmlresult, "post", "xml", "xml")
		xmlroot = ET.fromstring(xmlresponse)

		""" The following lines are for testing purpose only (the json data is in local, not a real data from http)
		 Sometimes the http response an error object. To test with error object use file "ObjectName_Fail.xml"
		 located at the same level with "ObjectName_Success.xml"
		"""
		#xmlresponse = ET.parse("Assets/dhl/test_response/003_Pickup_Success.xml")
		#xmlroot = xmlresponse.getroot()

		# Prevent Error
		try:
		# STEP 4: Load "json_model"from assets
			with open("Assets/dhl/json_response_model/003_Pickup.json") as data_file:
				json_model = json.load(data_file)

			# STEP 5. convert "response_object" to "json_model" and return result ##NEED PARAMSLIST
			# final_result = converter.xml_converter(json_model, xmlroot)
			final_result=converter.xml_converter_Pickup(json_model,xmlroot,paramlist)
			print ("Pickup Info from DHL: \n"+str(final_result))
			return  final_result
		except:
			return "Cannot get data from the URL"+str(xmlresponse)

	def status(self,paramlist):
		print ("type function")
		date = datetime.datetime.now()
		datenow=re.sub(r'\s.*','',str(date))
		tree = ET.parse('Assets/dhl/requests/003_Pickup.txt')
		root = tree.getroot()
		root.find("Pickup/PickupDate").text = datenow
		# root.find("Request/ServiceHeader/SiteID").text = os.environ["DHL_USERID"]
		# root.find("Request/ServiceHeader/Password").text = os.environ["DHL_PWD"]
		start=time.time()
		available=True
		response_time=0
		xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		try:
			xmlresponse = netw.sendRequest(DHL_URL, xmlresult, "post", "xml", "xml")
			xmlroot = ET.fromstring(xmlresponse)
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


	def pickupslots(self, paramlist):
		print ("pickupslots from DHL")
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
			fullstartdate2=str(newdate)+" 12:00:00:000Z"
			fullstartdate3=str(newdate)+" 14:00:00:000Z"
			fullstartdate4=str(newdate)+" 16:00:00:000Z"
			fullstartdate5=str(newdate)+" 18:00:00:000Z"
			data={
		        "date": str(date),
		        "slots": [
			        {
						"start_time": fullstartdate1,
				        "duration": "120",
				        "availability": -1
					},
					{
						"start_time": fullstartdate2,
				        "duration": "120",
				        "availability": -1
					},
					{
						"start_time": fullstartdate3,
				        "duration": "120",
				        "availability": -1
					},
					{
						"start_time": fullstartdate4,
				        "duration": "120",
				        "availability": -1
					},
					{
						"start_time": fullstartdate5,
				        "duration": "120",
				        "availability": -1
					}
				]
		    }

			alldays.append(data)
		return alldays

	def label(self,userparamlist):
		print ("label function")
		tree = ET.parse('Assets/dhl/requests/002_Shipment_FR_BE.txt')
		root = tree.getroot()

		date = datetime.datetime.now()
		datenow=re.sub(r'\s.*','',str(date))

		s3key1=os.environ["S3_KEY1"]
		s3key2=os.environ["S3_KEY2"]

		paramlist = {}
		paramlist["origin"] = {}
		paramlist["parcel"] = {}
		paramlist["destination"] = {}
		paramlist["destination"]["phone"] = ""
		paramlist["destination"]["email"] = ""
		paramlist["destination"]["line2"] = ""
		paramlist["parcel"]["width_in_cm"] = ""
		paramlist["parcel"]["weight_in_grams"] = "0.0"
		paramlist["parcel"]["height_in_cm"] = ""
		paramlist["parcel"]["length_in_cm"] = ""
		paramlist["contents"] = ""
		# paramlist["origin"]["first_name"] = ""
		# paramlist["origin"]["last_name"] = ""
		paramlist["origin"]["company"] = ""
		paramlist["origin"]["line2"] = ""
		paramlist["origin"]["zipcode"] = ""
		paramlist["origin"]["phone"] = ""
		paramlist["origin"]["state"] = ""
		paramlist["origin"]["place_description"] =""
		
		instance = Validator()
		req_list=["origin/city","shipment_date","destination/shipment_id","destination/company","destination/line1","destination/city","destination/state","destination/zipcode","destination/country_code","destination/country","destination/name",
		"destination/first_name","destination/last_name","origin/city","origin/line1","origin/country","origin/country_code","origin/name"]
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
		else:
			return checkparamlist["message"]


		origin_countrycode=str(paramlist["origin"]["country_code"])
		if origin_countrycode=="FR":
			shipperAccountNumber= str(os.environ["SHIPPER_ACCOUNT_NUMBER_EXPORT"])
		else:
			shipperAccountNumber=str(os.environ["SHIPPER_ACCOUNT_NUMBER_IMPORT"])

		messageTime=str(datenow)+"T11:28:56.000-08:00"
		messageReference=str(randrange(0,10000000000000000000000000000000))
		
		parcel_weight_in_grams=str(paramlist["parcel"]["weight_in_grams"])
		parcel_weight_in_grams=str(float(parcel_weight_in_grams)/1000)
		if parcel_weight_in_grams <= "0":
			parcel_weight_in_grams="0.0"

		destination_fullname= str(paramlist["destination"]["first_name"]) + str(paramlist["destination"]["last_name"])
		
		origin_countrycode=str(paramlist["origin"]["country_code"])
		destination_countryCode = str(paramlist["destination"]["country_code"])
		if origin_countrycode == "FR" and destination_countryCode == "FR":
			root.find("ShipmentDetails/GlobalProductCode").text = "N"
		else:
			root.find("ShipmentDetails/GlobalProductCode").text = "U"

		root.find("Request/ServiceHeader/MessageTime").text = messageTime
		root.find("Request/ServiceHeader/MessageReference").text = messageReference

		root.find("Request/ServiceHeader/SiteID").text = os.environ["DHL_USERID"]
		root.find("Request/ServiceHeader/Password").text = os.environ["DHL_PWD"]

		root.find("Billing/ShipperAccountNumber").text = shipperAccountNumber
		root.find("Billing/BillingAccountNumber").text = shipperAccountNumber
		root.find("Consignee/CompanyName").text = paramlist["destination"]["company"]
		root.find("Consignee/AddressLine").text = paramlist["destination"]["line1"]
		root.find("Consignee/City").text = paramlist["destination"]["city"]
		root.find("Consignee/Division").text = paramlist["destination"]["state"]
		root.find("Consignee/PostalCode").text = paramlist["destination"]["zipcode"]
		root.find("Consignee/CountryCode").text = paramlist["destination"]["country_code"]
		root.find("Consignee/CountryName").text = paramlist["destination"]["country"]
		root.find("Consignee/Contact/PersonName").text = destination_fullname
		root.find("Consignee/Contact/PhoneNumber").text = paramlist["destination"]["phone"]
		root.find("Consignee/Contact/Email").text = paramlist["destination"]["email"]
		root.find("Consignee/Contact/MobilePhoneNumber").text = paramlist["destination"]["phone"]

		root.find("Commodity/CommodityCode").text = paramlist["destination"]["shipment_id"]
		root.find("Reference/ReferenceID").text = paramlist["destination"]["shipment_id"]
		# root.find("ShipmentDetails/NumberOfPieces").text = destination_shipmentId
		root.find("ShipmentDetails/Pieces/Piece/Weight").text = str(parcel_weight_in_grams)
		root.find("ShipmentDetails/Pieces/Piece/Width").text = str(paramlist["parcel"]["width_in_cm"])
		root.find("ShipmentDetails/Pieces/Piece/Height").text = str(paramlist["parcel"]["height_in_cm"])
		root.find("ShipmentDetails/Pieces/Piece/Depth").text = str(paramlist["parcel"]["length_in_cm"])
		root.find("ShipmentDetails/Weight").text = str(parcel_weight_in_grams)
		root.find("ShipmentDetails/Date").text = paramlist["shipment_date"]
		root.find("ShipmentDetails/Contents").text =  paramlist["contents"]

		root.find("Shipper/ShipperID").text = shipperAccountNumber
		root.find("Shipper/CompanyName").text = paramlist["origin"]["company"]
		root.find("Shipper/AddressLine").text = paramlist["origin"]["line1"]
		# root.find("Shipper/AddressLine").text = origin_line2
		root.find("Shipper/City").text = paramlist["origin"]["city"]
		root.find("Shipper/PostalCode").text = paramlist["origin"]["zipcode"]
		root.find("Shipper/CountryCode").text = paramlist["origin"]["country_code"]
		root.find("Shipper/CountryName").text = paramlist["origin"]["country"]
		# root.find("Shipper/Contact/PersonName").text = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
		root.find("Shipper/Contact/PhoneNumber").text = paramlist["origin"]["phone"]
		root.find("Shipper/Contact/Email").text = paramlist["origin"]["email"]

		root.find("Place/CompanyName").text = paramlist["origin"]["company"]
		root.find("Place/AddressLine").text = paramlist["origin"]["line1"]
		root.find("Place/City").text = paramlist["origin"]["city"]
		root.find("Place/CountryCode").text = paramlist["origin"]["country_code"]
		root.find("Place/Division").text = paramlist["origin"]["state"]
		root.find("Place/PostalCode").text = paramlist["origin"]["zipcode"]
		root.find("Place/PackageLocation").text = paramlist["origin"]["place_description"]

		c = boto.connect_s3(s3key1, s3key2)
		b = c.get_bucket("srbstickers", validate=False)

		xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		xmlresponse = netw.sendRequest(DHL_URL, xmlresult, "post", "xml", "xml")
		xmlroot = ET.fromstring(xmlresponse)

		for child in xmlroot.findall('LabelImage'):
			pdf=child.find('OutputFormat').text+'.pdf'
			img_data=child.find('OutputImage').text
			name_file=str(time.time())+".pdf"
			k = Key(b)
			k.key = name_file
			k.contentType="application/pdf"
			k.ContentDisposition="inline"
			# k.set_contents_from_string(img_data.decode('base64'))
			k.set_contents_from_string(base64.b64decode(img_data.encode('ascii')))
			link_pdf="https://s3-us-west-2.amazonaws.com/srbstickers/"+name_file

		
		shipmentId="0"
		for getchild in xmlroot.findall('AirwayBillNumber'):
			if len(getchild)<0:
				shipmentId= ''
			else:
				shipmentId=getchild.text

		if shipmentId=="0":
			return xmlresponse
		data={
		  "origin": paramlist["origin"],
		  "destination": paramlist["destination"],
		  "parcel": paramlist["parcel"],
		  "shipment_id": shipmentId,
		  "label_url": link_pdf
		}
		return data








	def price(self,paramlist):
		print ("price function")
		date = datetime.datetime.now()
		datenow=re.sub(r'\s.*','',str(date))
		tree = ET.parse('Assets/dhl/requests/003_Pickup.txt')
		root = tree.getroot()

		root.find("Request/ServiceHeader/SiteID").text = os.environ["DHL_USERID"]
		root.find("Request/ServiceHeader/Password").text = os.environ["DHL_PWD"]
		root.find("Pickup/PickupDate").text = datenow

		xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		xmlresponse = netw.sendRequest(DHL_URL, xmlresult, "post", "xml", "xml")
		xmlroot = ET.fromstring(xmlresponse)
		try:
			shipment_id=xmlroot.find("ConfirmationNumber").text
		except:
			return xmlresponse
		currency="$"
		data={
			"destination":paramlist["destination"],
			"origin":paramlist["origin"],
			"parcel":paramlist["parcel"],
			"shipment_id": shipment_id,
			"price":0,
			"currency":currency
	    }
		return data


	def type(self,paramlist):
		print ("status function")
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



# ============== README ================
# The processes of each function in this class are:
# 1. Load "request object parameter" from assets (can be xml or json)
# 2. set value to object parameter 
# 3. get "response object" from http with request parameter (just set in step 2)
# 4A. Load "json_model"from assets
# 4B. Note: "json_model" is a standard response object. Each service should have one standard json response object
# 5. convert "response_object" to "json_model" and return result