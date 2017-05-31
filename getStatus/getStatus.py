import requests
import time
import datetime
# from datetime import datetime
import re

def lambda_handler(event,context):
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
	headers = {'Content-Type': 'application/xml'}
	start=time.time()
	available=True
	response_time=0

	try:
		resp=requests.post('https://xmlpitest-ea.dhl.com/XMLShippingServlet', data=xml, headers=headers).text
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
	# print result
	return result


print lambda_handler('a','bS')

# def dateme():
# 	date = datetime.datetime.now()
# 	datenow=re.sub(r'\s.*','',str(date))
# 	fmt = '%Y-%m-%d %H:%M:%S'
# 	d1 = datetime.datetime.strptime('2017-05-31 07:43:13', fmt)
# 	d2 = datetime.datetime.strptime('2017-05-31 08:43:13', fmt)
# 	diff=(d2-d1).days
# 	print diff
# 	print '-------'
# 	d1_ts = time.mktime(d1.timetuple())
# 	d2_ts = time.mktime(d2.timetuple())
# 	print int(d2_ts-d1_ts) / 60
# 	# print ((d2-d1).days) * 24 * 60
# dateme()