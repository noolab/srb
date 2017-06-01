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

def getpickupTest(event):
	# date = datetime.datetime.now()

	if "pickup" not in event:
		return "Please specify a pickup"
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
	print xml
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

print getpickupTest({
      "requestor": {
        "name": "Djibril",
        "phone": "+855886697345",
        "company": "Nagadev"
      },
      "place": {
        "line1": "166 Street 118",
        "line2": "Sangkat Phsar Chaas",
        "package_location": "Phsaar",
        "city": "Paris",
        "post_code": "95380",
        "country_code": "FR"
      },
      "pickup": {
        "pickup_date": "2017-06-03",
        "slot_id": "11111",
        "close_time": "23:00",
        "number_of_pieces": 1,
        "special_instructions": "Be careful its my computer"
      },
      "shipment_details": {
        "number_of_pieces": 1,
        "weight": 1
      }
    })



	