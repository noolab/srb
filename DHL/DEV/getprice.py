import requests
import xml.etree.ElementTree as ET
import datetime
import re
def getprice(event,context):
	date = datetime.datetime.now()
	datenow=re.sub(r'\s.*','',str(date))
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
	            <PersonName>Rikhil</PersonName>
	            <Phone>23162</Phone>
	        </RequestorContact>
	        <CompanyName>Saurabh</CompanyName>
	    </Requestor>
	   <Place>
		<LocationType>B</LocationType>        
		<CompanyName>Test and Co</CompanyName>        
		<Address1>123 Test Ave</Address1>       
	        <Address2>Test Bus Park</Address2>        
		<PackageLocation>Reception</PackageLocation>        
		<City>PARIS</City>        
		<CountryCode>FR</CountryCode>        
		<PostalCode>75018</PostalCode>        
	</Place>
	    <Pickup>
	        <PickupDate>"""+datenow+"""</PickupDate>
	        <ReadyByTime>"""+'10:20'+"""</ReadyByTime>
	        <CloseTime>"""+'17:20'+"""</CloseTime>
	        <SpecialInstructions>1 palett of 200 kgs - Vehicule avec hayon</SpecialInstructions> 
	     </Pickup>
	    <PickupContact>
	        <PersonName>Subhayu</PersonName>
	        <Phone>4801313131</Phone>
	    </PickupContact>
	   <ShipmentDetails>
	        <AccountType>D</AccountType>
	        <AccountNumber>123456789</AccountNumber>
	        <NumberOfPieces>1</NumberOfPieces>
	        <Weight>200</Weight>
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
	print resp
	root = ET.fromstring(resp)
	shipment_id= root.find('ConfirmationNumber').text
	currency="$"
	data={
		"destination":event["destination"],
		"origin":event["origin"],
		"parcel":event["parcel"],
		"shipment_id": shipment_id,
		"price":0,
		"currency":currency
    }
	return data

# def test():
# 	date = datetime.datetime.now()
# 	datenow=re.sub(r'\s.*','',str(date))
# 	print date
# test()
# print getprice('d','as')
# print pickup('2017-05-04','10:20','17:20')
# {"pickupDate":"2017-05-05",
# "readyTime":"10:20",
# "closeTime":"17:20"}
