import requests
import xml.etree.ElementTree as ET
import datetime
import re
import time
import os
def getpickup(event,context):
	# date = datetime.datetime.now()
	datenow=str(datetime.datetime.now())
	datenow=re.sub(r'\..*','',datenow)
	dateinput=event["pickup"]["pickup_date"]+' '+event["pickup"]["close_time"]+':00'
	cmp1=time.strptime(datenow, "%Y-%m-%d %H:%M:%S")
	cmp2=time.strptime(dateinput, "%Y-%m-%d %H:%M:%S")
	if cmp1 > cmp2:
		data={"messageError":"your pickup_date and close_time not valid! please check again"}
		return data

	if "pickup_date" not in event["pickup"]:
		return "pickup_date is missing. .."

	pickup_date=event["pickup"]["pickup_date"]
	if "ready_by_time" not in event["pickup"]:
		return "ready_by_time is missing ..."

	readyByTime=event["pickup"]["ready_by_time"]
	if "close_time" not in event["pickup"]:
		return "close_time is missing.."
	close_time=event["pickup"]["close_time"]
	if "special_instructions" not in event["pickup"]:
		return "special_instructions is missing"
	special_instruction=event["pickup"]["special_instructions"]
	if "post_code" not in event["place"]:
		return "post_code is missing..."
	postal_code=event["place"]["post_code"]
	if "country_code" not in event["place"]:
		return "country_code is missing .."
	country_code=event["place"]["country_code"]
	if "city" not in event["place"]:
		return "city is missing.."
	city=event["place"]["city"]
	if "package_location" not in event["place"]:
		return "package_location is missing.."
	package_location=event["place"]["package_location"]
	if "number_of_pieces" not in event["shipment_details"]:
		return "number_of_pieces is missing.."
	numberOfPiece=str(event["shipment_details"]["number_of_pieces"])
	if "weight" not in event["shipment_details"]:
		return "weight in shipment_details is missing.."
	weight=str(event["shipment_details"]["weight"])

	if weight=="":
		return "weight is required"

	if event["place"]["line1"]=="":
		return "Address is required"

	if package_location=="":
		return "package_location is required"

	if city=="":
		return "city is required"

	if country_code=="":
		return "country_code is required"

	if pickup_date=="":
		return "pickup_date is required"

	if readyByTime=="":
		return "readyByTime is required"

	if close_time=="":
		return "close_time is required"


	xml = """<?xml version="1.0" encoding="UTF-8"?>
	<req:BookPURequest xsi:schemaLocation="http://www.dhl.com book-pickup-global-req_EA.xsd" schemaVersion="1.0" xmlns:req="http://www.dhl.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	    <Request>
	        <ServiceHeader>
	            <MessageTime>2013-08-03T11:28:56.000-08:00</MessageTime>
	            <MessageReference>1234567890123456789012345678901</MessageReference>
	  	    <SiteID>"""+os.environ["DHL_USERID"]+"""</SiteID> 
	  	    <Password>"""+os.environ["DHL_PWD"]+"""</Password> 
	        </ServiceHeader>
	    </Request>
	    <RegionCode>EU</RegionCode>
	    <Requestor>
	        <AccountType>D</AccountType>
	        <AccountNumber>223932540</AccountNumber>
	        <RequestorContact>
	            <PersonName>No Name</PersonName>
	            <Phone>+3373435520</Phone>
	        </RequestorContact>
	        <CompanyName>SHOPRUNBACK</CompanyName>
	    </Requestor>
	   <Place>
		<LocationType>C</LocationType>        
		<CompanyName>"""+event["requestor"]["company"]+"""</CompanyName>        
		<Address1>"""+event["place"]["line1"]+"""</Address1>       
	        <Address2>"""+event["place"]["line2"]+"""</Address2>        
		<PackageLocation>"""+package_location+"""</PackageLocation>        
		<City>"""+city+"""</City>        
		<CountryCode>"""+country_code+"""</CountryCode>        
		<PostalCode>"""+postal_code+"""</PostalCode>        
	</Place>
	    <Pickup>
	        <PickupDate>"""+pickup_date+"""</PickupDate>
	        <ReadyByTime>"""+readyByTime+"""</ReadyByTime>
	        <CloseTime>"""+close_time+"""</CloseTime> 
	     </Pickup>
	    <PickupContact>
	        <PersonName>"""+event["requestor"]["name"]+"""</PersonName>
	        <Phone>"""+event["requestor"]["phone"]+"""</Phone>
	    </PickupContact>
	   <ShipmentDetails>
	        <AccountType>D</AccountType>
	        <AccountNumber>223932540</AccountNumber>
	        <NumberOfPieces>"""+numberOfPiece+"""</NumberOfPieces>
	        <Weight>"""+weight+"""</Weight>
	        <WeightUnit>K</WeightUnit>
	        <GlobalProductCode>D</GlobalProductCode>
	        <DoorTo>DD</DoorTo>
	        <Pieces>
	        </Pieces>
	        <SpecialService>YV</SpecialService>
	    </ShipmentDetails>
	</req:BookPURequest>"""
	#print xml
	headers = {'Content-Type': 'application/xml'} # set what your server accepts
	resp=requests.post('https://xmlpitest-ea.dhl.com/XMLShippingServlet', data=xml, headers=headers).text
	root = ET.fromstring(resp)
	try:
		pickup_id= root.find('ConfirmationNumber').text
		data=[
			{
			    "pickup_id": pickup_id,
			    "requestor": event["requestor"],
			    "place": event["place"],
			    "pickup": event["pickup"],
			    "shipment_details": event["shipment_details"]
			}
		]
	except:
		return resp
		#data={"messageError":"pickup_id not found! Please check your input again"}
	return data