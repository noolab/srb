from Classes.AbstractService import Service
from BuiltInService import requests
from BuiltInService import xmltodict
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

date = datetime.datetime.now()
curdate = re.sub(r'\s.*','',str(date))

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
			"pickup":{
				"post":true
			},
			"price":{
				"post":true
			},
			"label":{
				"post":true
			},
			"status":{
				"get":true
			},
			"tracking":{
				"get":true
			}
		}
		return data
		

	def pickup(self, userparamlist):
		
		instance = Validator()
		req_list=["pickup/date","pickup/slot_start_at","pickup/slot_end_at","origin/company","origin/line1","origin/city","origin/country_code"]
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			# paramlist=userparamlist
			reqEmpty=["origin/email","origin/line2","origin/zipcode","origin/first_name","origin/last_name","origin/phone","origin/city","origin/country_code","parcel/width_in_cm","parcel/height_in_cm",
			"parcel/length_in_cm","parcel/contents","origin/package_location","destination/email"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
			if "weight_in_grams" not in paramlist["parcel"]:
				paramlist["parcel"]["weight_in_grams"]="0.0"

			paramlist["origin"]["name"]  = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
			paramlist["origin"]["package_location"] ="Back Room"
			paramlist["origin"]["state"] = str(paramlist["origin"]["city"])
			data_line1= str(paramlist["origin"]["line1"])
			street_info = instance.json_check_line1(data_line1)
			paramlist["origin"]["street_number"]  = street_info["street_number"]
			paramlist["origin"]["street_name"]  =street_info["street_name"]
			if paramlist["origin"]["street_number"]=="":
				paramlist["origin"]["street_number"]="0"

			
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

		root.find("Pickup/PickupDate").text = paramlist["pickup"]["date"]   #paramlist["pickup_date"] # "2017-05-26"
		root.find("Pickup/ReadyByTime").text = paramlist["pickup"]["slot_start_at"] #paramlist["ready_by_time"] # "10:20"
		root.find("Pickup/CloseTime").text = paramlist["pickup"]["slot_end_at"]  #paramlist["slot_end_at"] # "14:20"
		
		root.find("Place/CompanyName").text = paramlist["origin"]["company"]
		root.find("Place/Address1").text = paramlist["origin"]["line1"]
		root.find("Place/Address2").text = paramlist["origin"]["line2"] 
		root.find("Place/PackageLocation").text = paramlist["origin"]["package_location"] 
		root.find("Place/City").text = paramlist["origin"]["city"] 
		root.find("Place/CountryCode").text = paramlist["origin"]["country_code"] 
		root.find("Place/PostalCode").text = paramlist["origin"]["zipcode"] 

		root.find("PickupContact/PersonName").text = paramlist["origin"]["name"] 
		root.find("PickupContact/Phone").text = paramlist["origin"]["phone"] 

		root.find("ShipmentDetails/NumberOfPieces").text = str(paramlist["parcel"]["number_of_pieces"])
		root.find("ShipmentDetails/Weight").text = str(paramlist["parcel"]["weight_in_grams"])

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

		# Prevent Error
		# try:
		# 	with open("Assets/dhl/json_response_model/003_Pickup.json") as data_file:
		# 		json_model = json.load(data_file)

		# 	final_result=converter.xml_converter_Pickup(json_model,xmlroot,paramlist)
		# 	print ("Pickup Info from DHL: \n"+str(final_result))
		# 	return  final_result
		# except:
		# 	return "Cannot get data from the URL"+str(xmlresponse)
		"""New Modify try to get it direclty """
		try:
			pickup_id=xmlroot.find("ConfirmationNumber").text
		except:
			return xmlresponse
		"""call label function directly"""
		tree = ET.parse('Assets/dhl/requests/002_Shipment_FR_BE.txt')
		root = tree.getroot()

		date = datetime.datetime.now()
		datenow=re.sub(r'\s.*','',str(date))

		s3key1=os.environ["S3_KEY1"]
		s3key2=os.environ["S3_KEY2"]
		
		instance = Validator()
		req_list=["shipment_id","destination/company","destination/line1","destination/city","destination/zipcode","destination/country_code",
		"destination/first_name","destination/last_name","origin/city","origin/line1","origin/country_code","origin/first_name","origin/last_name"]
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			# paramlist=userparamlist
			reqEmpty=["origin/street_number","origin/street_name","destination/street_number","destination/street_name","parcel/contents"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
			paramlist["origin"]["name"] = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
			paramlist["destination"]["name"] = str(paramlist["destination"]["first_name"])+" "+str(paramlist["destination"]["last_name"])
			paramlist["origin"]["country"]  = instance.getCountryName(str(paramlist["origin"]["country_code"]))
			paramlist["destination"]["country"]  = instance.getCountryName(str(paramlist["destination"]["country_code"]))
			paramlist["parcel"]["contents"] = str(pickup_id)
			paramlist["destination"]["state"] =str(paramlist["destination"]["city"])

			data_line1= str(paramlist["destination"]["line1"])
			street_info = instance.json_check_line1(data_line1)
			paramlist["destination"]["street_number"]  = street_info["street_number"]
			paramlist["destination"]["street_name"]  =street_info["street_name"]
			if paramlist["destination"]["street_number"]=="":
				paramlist["destination"]["street_number"]="0"
		else:
			# return checkparamlist["message"]
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)


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

		destination_fullname= str(paramlist["destination"]["first_name"]) +" "+ str(paramlist["destination"]["last_name"])
		
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
		root.find("Consignee/AddressLine").text = str(paramlist["destination"]["street_number"])+str(paramlist["destination"]["street_name"]) #+str(paramlist["destination"]["line1"])
		root.find("Consignee/City").text = paramlist["destination"]["city"]
		root.find("Consignee/Division").text = paramlist["destination"]["state"]
		root.find("Consignee/PostalCode").text = paramlist["destination"]["zipcode"]
		root.find("Consignee/CountryCode").text = paramlist["destination"]["country_code"]
		root.find("Consignee/CountryName").text = paramlist["destination"]["country"]
		root.find("Consignee/Contact/PersonName").text = destination_fullname
		root.find("Consignee/Contact/PhoneNumber").text = paramlist["destination"]["phone"]
		root.find("Consignee/Contact/Email").text = paramlist["destination"]["email"]
		root.find("Consignee/Contact/MobilePhoneNumber").text = paramlist["destination"]["phone"]

		root.find("Commodity/CommodityCode").text = paramlist["shipment_id"]
		root.find("Reference/ReferenceID").text = paramlist["shipment_id"]
		# root.find("ShipmentDetails/NumberOfPieces").text = destination_shipmentId
		root.find("ShipmentDetails/Pieces/Piece/Weight").text = str(parcel_weight_in_grams)
		root.find("ShipmentDetails/Pieces/Piece/Width").text = str(paramlist["parcel"]["width_in_cm"])
		root.find("ShipmentDetails/Pieces/Piece/Height").text = str(paramlist["parcel"]["height_in_cm"])
		root.find("ShipmentDetails/Pieces/Piece/Depth").text = str(paramlist["parcel"]["length_in_cm"])
		root.find("ShipmentDetails/Weight").text = str(parcel_weight_in_grams)
		root.find("ShipmentDetails/Date").text = curdate
		root.find("ShipmentDetails/Contents").text =  paramlist["parcel"]["contents"]

		root.find("Shipper/ShipperID").text = shipperAccountNumber
		root.find("Shipper/CompanyName").text = paramlist["origin"]["company"]
		root.find("Shipper/AddressLine").text = str(paramlist["origin"]["street_number"])+str(paramlist["origin"]["street_name"]) #+str(paramlist["origin"]["line1"])
		# root.find("Shipper/AddressLine").text = origin_line2
		root.find("Shipper/City").text = paramlist["origin"]["city"]
		root.find("Shipper/PostalCode").text = paramlist["origin"]["zipcode"]
		root.find("Shipper/CountryCode").text = paramlist["origin"]["country_code"]
		root.find("Shipper/CountryName").text = paramlist["origin"]["country"]
		# root.find("Shipper/Contact/PersonName").text = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
		root.find("Shipper/Contact/PhoneNumber").text = paramlist["origin"]["phone"]
		root.find("Shipper/Contact/Email").text = paramlist["origin"]["email"]

		root.find("Place/CompanyName").text = paramlist["origin"]["company"]
		root.find("Place/AddressLine").text = str(paramlist["origin"]["street_number"])+str(paramlist["origin"]["street_name"]) #+str(paramlist["origin"]["line1"])
		root.find("Place/City").text = paramlist["origin"]["city"]
		root.find("Place/CountryCode").text = paramlist["origin"]["country_code"]
		root.find("Place/Division").text = paramlist["origin"]["state"]
		root.find("Place/PostalCode").text = paramlist["origin"]["zipcode"]
		root.find("Place/PackageLocation").text = "" ##paramlist["origin"]["place_description"]

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

		"""END call label function directly"""
		
		paramlist["pickup_id"]=pickup_id
		paramlist["carrier_shipment_id"]=shipmentId
		paramlist["label_url"]=link_pdf
		paramlist["shipment_details"]=paramlist["parcel"]
		del paramlist["parcel"]

		# if "destination" in paramlist:
		# 	final_data={
		# 		"origin":paramlist["origin"],
		# 		"pickup":paramlist["pickup"],
		# 		"shipment_details":paramlist["parcel"],
		# 		"destination":paramlist["destination"],
		# 		"pickup_id":pickup_id,
		# 		"carrier_shipment_id": shipmentId,
  #   			"label_url": link_pdf
		# 	}
		# else:
		# 	final_data={
		# 		"origin":paramlist["origin"],
		# 		"pickup":paramlist["pickup"],
		# 		"shipment_details":paramlist["parcel"],
		# 		"pickup_id":pickup_id,
		# 		"carrier_shipment_id": shipmentId,
  #   			"label_url": link_pdf
		# 	}

		return paramlist

	def status(self,paramlist):
		parampickup={
			"shipment_id": "return_id_at_srb",
			"origin": {
			    "first_name": "Rikhil",
			    "last_name":"Rikhil",
			    "phone": "23162",
			    "company": "Saurabh",
			    "line1": "123 Test Ave",
			    "line2": "Test Bus Park",
			    "package_location": "Back Room",
			    "city": "PARIS",
			    "zipcode": "75018",
			    "country_code": "FR"
			  },
			"destination": {
			    "name": "Maison",
			    "shipment_id": "return_id_at_srb",
			    "first_name": "Leo",
			    "last_name": "Martin",
			    "company": "Company Destination",
			    "line1": "Wilsnacker Str. 52",
			    "line2": "line2",
			    "street_number":"21",
				"street_name":"test",
			    "state": "Helsinki",
			    "zipcode": "00101",
			    "country": "Finland",
			    "country_code": "FI",
			    "phone": "3589635732",
			    "email": "eddy@gmail.com",
			    "city": "Helsinki"
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
		paramprice={}
		paramdropoff={}
		paramtraking="3618411160"
		paramlabel ={
			"shipment_id": "return_id_at_srb",
			"origin": {
		    "name": "Ithyvan Schreys",
		    "first_name": "Ithyvan",
		    "last_name": "Schreys",
		    "phone": "d arnouville",
		    "email": "",
		    "company": "Company Origin",
		    "line1": "32 rue de paradis",
		    "street_number":"21",
			"street_name":"test",
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
		    "street_number":"21",
			"street_name":"test",
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
		objfunction=["root","type","pickup","price","pickup/slots","label"]
		instance = Validator()
		api_url_request = os.environ["API_DEVEVELOPER_URL"]
		result = instance.get_all_status("dhl",api_url_request,objfunction,paramlabel,parampickup,paramdropoff,paramtraking,paramprice)
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
			# fullstartdate1=str(newdate)+" 10:00:00:000Z"
			# fullstartdate2=str(newdate)+" 12:00:00:000Z"
			# fullstartdate3=str(newdate)+" 14:00:00:000Z"
			# fullstartdate4=str(newdate)+" 16:00:00:000Z"
			# fullstartdate5=str(newdate)+" 18:00:00:000Z"
			fullstartdate1="10:00:00"
			fullstartdate2="12:00:00"
			fullstartdate3="14:00:00"
			fullstartdate4="16:00:00"
			fullstartdate5="18:00:00"
			data={
		        "date": str(newdate),
		        "timezone":False,
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
		
		instance = Validator()
		req_list=["shipment_id","destination/company","destination/line1","destination/city","destination/zipcode","destination/country_code",
		"destination/first_name","destination/last_name","origin/city","origin/line1","origin/country_code","origin/first_name","origin/last_name"]
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			# paramlist=userparamlist
			reqEmpty=["destination/phone","destination/email","destination/line2","parcel/width_in_cm","parcel/height_in_cm","parcel/length_in_cm","parcel/contents","origin/company","origin/line2","origin/zipcode","origin/phone","origin/state"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
			paramlist["origin"]["name"] = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
			paramlist["destination"]["name"] = str(paramlist["destination"]["first_name"])+" "+str(paramlist["destination"]["last_name"])
			
			paramlist["origin"]["country"] = instance.getCountryName(str(paramlist["origin"]["country_code"]))
			paramlist["destination"]["country"] = instance.getCountryName(str(paramlist["destination"]["country_code"]))

			data_line1= str(paramlist["origin"]["line1"])
			street_info = instance.json_check_line1(data_line1)
			paramlist["origin"]["street_number"]  = street_info["street_number"]
			paramlist["origin"]["street_name"]  =street_info["street_name"]
			if paramlist["origin"]["street_number"]=="":
				paramlist["origin"]["street_number"]="0"

			#destination line1
			dest_line1= str(paramlist["destination"]["line1"])
			street_info = instance.json_check_line1(dest_line1)
			paramlist["destination"]["street_number"]  = street_info["street_number"]
			paramlist["destination"]["street_name"]  =street_info["street_name"]
			if paramlist["destination"]["street_number"]=="":
				paramlist["destination"]["street_number"]="0"

			paramlist["destination"]["state"] = str(paramlist["destination"]["city"])
		else:
			# return checkparamlist["message"]
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

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
		root.find("Consignee/AddressLine").text = str(paramlist["destination"]["street_number"])+str(paramlist["destination"]["street_name"]) #+str(paramlist["destination"]["line1"])
		root.find("Consignee/City").text = paramlist["destination"]["city"]
		root.find("Consignee/Division").text = paramlist["destination"]["state"]
		root.find("Consignee/PostalCode").text = paramlist["destination"]["zipcode"]
		root.find("Consignee/CountryCode").text = paramlist["destination"]["country_code"]
		root.find("Consignee/CountryName").text = paramlist["destination"]["country"]
		root.find("Consignee/Contact/PersonName").text = destination_fullname
		root.find("Consignee/Contact/PhoneNumber").text = paramlist["destination"]["phone"]
		root.find("Consignee/Contact/Email").text = paramlist["destination"]["email"]
		root.find("Consignee/Contact/MobilePhoneNumber").text = paramlist["destination"]["phone"]

		root.find("Commodity/CommodityCode").text = paramlist["shipment_id"]
		root.find("Reference/ReferenceID").text = paramlist["shipment_id"]
		# root.find("ShipmentDetails/NumberOfPieces").text = destination_shipmentId
		root.find("ShipmentDetails/Pieces/Piece/Weight").text = str(parcel_weight_in_grams)
		root.find("ShipmentDetails/Pieces/Piece/Width").text = str(paramlist["parcel"]["width_in_cm"])
		root.find("ShipmentDetails/Pieces/Piece/Height").text = str(paramlist["parcel"]["height_in_cm"])
		root.find("ShipmentDetails/Pieces/Piece/Depth").text = str(paramlist["parcel"]["length_in_cm"])
		root.find("ShipmentDetails/Weight").text = str(parcel_weight_in_grams)
		root.find("ShipmentDetails/Date").text = curdate
		root.find("ShipmentDetails/Contents").text =  paramlist["parcel"]["contents"]

		root.find("Shipper/ShipperID").text = shipperAccountNumber
		root.find("Shipper/CompanyName").text = paramlist["origin"]["company"]
		root.find("Shipper/AddressLine").text = str(paramlist["origin"]["street_number"])+str(paramlist["origin"]["street_name"]) #+str(paramlist["origin"]["line1"])
		# root.find("Shipper/AddressLine").text = origin_line2
		root.find("Shipper/City").text = paramlist["origin"]["city"]
		root.find("Shipper/PostalCode").text = paramlist["origin"]["zipcode"]
		root.find("Shipper/CountryCode").text = paramlist["origin"]["country_code"]
		root.find("Shipper/CountryName").text = paramlist["origin"]["country"]
		# root.find("Shipper/Contact/PersonName").text = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
		root.find("Shipper/Contact/PhoneNumber").text = paramlist["origin"]["phone"]
		root.find("Shipper/Contact/Email").text = paramlist["origin"]["email"]

		root.find("Place/CompanyName").text = paramlist["origin"]["company"]
		root.find("Place/AddressLine").text = str(paramlist["origin"]["street_number"])+str(paramlist["origin"]["street_name"]) #+str(paramlist["origin"]["line1"])
		root.find("Place/City").text = paramlist["origin"]["city"]
		root.find("Place/CountryCode").text = paramlist["origin"]["country_code"]
		root.find("Place/Division").text = paramlist["origin"]["state"]
		root.find("Place/PostalCode").text = paramlist["origin"]["zipcode"]
		root.find("Place/PackageLocation").text = "" #paramlist["origin"]["place_description"]

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
			responseErr = {"status": 500,"errors": [{"detail": str(xmlresponse)}]}
			raise Exception(responseErr)

		paramlist["label_url"] = link_pdf
		paramlist["carrier_shipment_id"] =shipmentId

		# data={
		#   "origin": paramlist["origin"],
		#   "destination": paramlist["destination"],
		#   "parcel": paramlist["parcel"],
		#   "carrier_shipment_id": shipmentId,
		#   "label_url": link_pdf
		# }
		return paramlist








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
			responseErr = {"status": 500,"errors": [{"detail": str(xmlresponse)}]}
			raise Exception(responseErr)
		currency="$"
		# data={
		# 	"destination":paramlist["destination"],
		# 	"origin":paramlist["origin"],
		# 	"parcel":paramlist["parcel"],
		# 	"shipment_id": shipment_id,
		# 	"price":0,
		# 	"currency":currency
	 #    }
		paramlist["currency"]=currency
		paramlist["carrier_shipment_id"]=shipment_id
		paramlist["price"]=0

		return paramlist


	def type(self,paramlist):
		print ("status function")
		true=True
		false=False
		data={
			"type": "pickup",
			"postal": false,
			"pickup": true,
			"dropoff": false,
			"linehaul": false
		}
		return data

	def tracking(self,paramlist):
		date = datetime.datetime.now()
		datenow=re.sub(r'\s.*','',str(date))
		tree = ET.parse('Assets/dhl/requests/tracking.txt')
		root = tree.getroot()

		root.find("Request/ServiceHeader/SiteID").text = os.environ["DHL_USERID"]
		root.find("Request/ServiceHeader/Password").text = os.environ["DHL_PWD"]
		root.find("AWBNumber").text = str(paramlist)

		# trackingNumber =str(paramlist)

		xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		xmlresponse = netw.sendRequest(DHL_URL, xmlresult, "post", "xml", "xml")
		# xmlroot = ET.fromstring(xmlresponse)

		data = xmltodict.parse(xmlresponse)
		try:
			allstep = data["req:TrackingResponse"]["AWBInfo"]["ShipmentInfo"]
		except:
			return xmlresponse


		final_data=[]
		dt ={
			"status":"",
			"steps": []
		}
		for index, l in enumerate(allstep["ShipmentEvent"]):
			res={
	        	"status": l["ServiceEvent"]["Description"],
	        	"location": l["ServiceArea"]["Description"]
	      	}
			dt['steps'].append(res)
			if index == len(allstep["ShipmentEvent"])-1:
				strStatus = l["ServiceEvent"]["Description"]
				if "processed" in strStatus.lower():
					datastatus="processed"
				elif "transit" in strStatus.lower():
					datastatus ="transit"
				elif "delivered" in strStatus.lower():
					datastatus="delivered"
				else:
					datastatus ="unknown"
				dt["status"]=datastatus
		final_data.append(dt)
		return final_data


# ============== README ================
# The processes of each function in this class are:
# 1. Load "request object parameter" from assets (can be xml or json)
# 2. set value to object parameter 
# 3. get "response object" from http with request parameter (just set in step 2)
# 4A. Load "json_model"from assets
# 4B. Note: "json_model" is a standard response object. Each service should have one standard json response object
# 5. convert "response_object" to "json_model" and return result