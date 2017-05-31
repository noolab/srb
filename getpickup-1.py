import requests
import xml.etree.ElementTree as ET
import datetime
import re
import time
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
	pickup_date=event["pickup"]["pickup_date"]
	readyByTime=event["pickup"]["ready_by_time"]
	close_time=event["pickup"]["close_time"]
	special_instruction=event["pickup"]["special_instructions"]
	postal_code=event["place"]["post_code"]
	country_code=event["place"]["country_code"]
	city=event["place"]["city"]
	package_location=event["place"]["package_location"]
	numberOfPiece=str(event["shipment_details"]["number_of_pieces"])
	weight=float(event["shipment_details"]["weight_in_grams"])/1000
	weight_kg=str(weight)


	xml = """<?xml version="1.0" encoding="UTF-8"?>
	<req:BookPURequest xsi:schemaLocation="http://www.dhl.com book-pickup-global-req_EA.xsd" schemaVersion="1.0" xmlns:req="http://www.dhl.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	    <Request>
	        <ServiceHeader>
	            <MessageTime>2013-08-03T11:28:56.000-08:00</MessageTime>
	            <MessageReference>1234567890123456789012345678901</MessageReference>
	  	    <SiteID>SRBFrance</SiteID> 
	  	    <Password>jXxlVhceKE</Password> 
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
	        <SpecialInstructions>"""+special_instruction+"""</SpecialInstructions> 
	     </Pickup>
	    <PickupContact>
	        <PersonName>"""+event["requestor"]["name"]+"""</PersonName>
	        <Phone>"""+event["requestor"]["phone"]+"""</Phone>
	    </PickupContact>
	   <ShipmentDetails>
	        <AccountType>D</AccountType>
	        <AccountNumber>123456789</AccountNumber>
	        <NumberOfPieces>"""+numberOfPiece+"""</NumberOfPieces>
	        <Weight>"""+weight_kg+"""</Weight>
	        <WeightUnit>K</WeightUnit>
	        <GlobalProductCode>D</GlobalProductCode>
	        <DoorTo>DD</DoorTo>
	        <Pieces>
	        </Pieces>
	        <SpecialService>I</SpecialService>
	    </ShipmentDetails>
	</req:BookPURequest>"""
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
		# data={"messageError":"pickup_id not found! Please check your input again"}
	return data
# getpickup('a','b')



	