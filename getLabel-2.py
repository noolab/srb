import requests
import boto
import time
from boto.s3.key import Key
import xml.etree.ElementTree as ET
import base64
import datetime
import re
# import tinys3
from boto.s3.connection import S3Connection
def getLabel(event,context):
	date = datetime.datetime.now()
	datenow=re.sub(r'\s.*','',str(date))
	shipmentdate=str(event["shipment_date"])
	destination_shipmentId=str(event["destination"]["shipment_id"])
	destination_company=str(event["destination"]["company"])
	destination_line1=str(event["destination"]["line1"])
	destination_line2=str(event["destination"]["line2"])
	destination_zipcode=str(event["destination"]["zipcode"])
	destination_countryCode=str(event["destination"]["country_code"])
	destination_country=str(event["destination"]["country"])
	destination_name=str(event["destination"]["name"])
	destination_firstname=str(event["destination"]["first_name"])
	destination_lastname=str(event["destination"]["last_name"])
	destination_firstname_lastname=str(destination_firstname)+" "+str(destination_lastname)
	destination_phone=str(event["destination"]["phone"])
	destination_email=str(event["destination"]["email"])
	destination_city=str(event["destination"]["city"])

	parcel_weight_in_grams=float(event["parcel"]["weight_in_grams"])/1000
	parcel_weight_in_kg=str(parcel_weight_in_grams)
	parcel_width_in_cm=str(event["parcel"]["width_in_cm"])
	parcel_height_in_cm=str(event["parcel"]["height_in_cm"])
	parcel_length_in_cm=str(event["parcel"]["length_in_cm"])
	content= str(event["contents"])
	origin_company=str(event["origin"]["company"])
	origin_city=str(event["origin"]["city"])
	origin_line1=str(event["origin"]["line1"])
	origin_line2=str(event["origin"]["line2"])+""
	origin_country=str(event["origin"]["country"])
	origin_zipcode=str(event["origin"]["zipcode"])+""
	origin_countrycode=str(event["origin"]["country_code"])
	origin_name=str(event["origin"]["name"])
	origin_phone=str(event["origin"]["phone"])
	origin_email=str(event["origin"]["email"])
	origin_state=str(event["origin"]["state"])
	origin_packagelocation=str(event["origin"]["place_description"])
	xml="""  <?xml version="1.0" encoding="UTF-8" ?> 
	 <req:ShipmentRequest xmlns:req="http://www.dhl.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.dhl.com ship-val-global-req.xsd" schemaVersion="1.0">
	 <Request>
	 <ServiceHeader>
	  <MessageTime>2002-08-20T11:28:56.000-08:00</MessageTime> 
	  <MessageReference>1234567890123456789012345678901</MessageReference> 
	  <SiteID></SiteID> 
	  <Password></Password>
	  </ServiceHeader>
	  </Request>
	  <RegionCode>EU</RegionCode> 
	  <NewShipper>Y</NewShipper> 
	  <LanguageCode>en</LanguageCode> 
	  <PiecesEnabled>Y</PiecesEnabled> 
	 <Billing>
	  <ShipperAccountNumber></ShipperAccountNumber> 
	  <ShippingPaymentType>S</ShippingPaymentType> 
	  <BillingAccountNumber></BillingAccountNumber> 
	  <DutyPaymentType>R</DutyPaymentType> 
	  </Billing>
	 <Consignee>
	  <CompanyName>"""+destination_company+"""</CompanyName> 
	  <AddressLine>"""+destination_line1+"""</AddressLine> 
	  <AddressLine>"""+destination_line2+"""</AddressLine> 
	  <City>"""+destination_city+"""</City> 
	  <Division></Division> 
	  <PostalCode>"""+destination_zipcode+"""</PostalCode> 
	  <CountryCode>"""+destination_countryCode+"""</CountryCode> 
	  <CountryName>"""+destination_country+"""</CountryName> 
	 <Contact>
	  <PersonName>"""+destination_firstname_lastname+"""</PersonName> 
	  <PhoneNumber>"""+destination_phone+"""</PhoneNumber>
	  <PhoneExtension></PhoneExtension> 
	  <FaxNumber></FaxNumber> 
	  <Telex></Telex>
	  <Email>"""+destination_email+"""</Email> 
	  </Contact>
	  </Consignee>
	 <Commodity>
	  <CommodityCode>"""+destination_shipmentId+"""</CommodityCode> 
	  <CommodityName>cn</CommodityName> 
	  </Commodity>
	 <Dutiable>
	  <DeclaredValue>0</DeclaredValue> 
	  <DeclaredCurrency>EUR</DeclaredCurrency> 
	  <ScheduleB>3002905110</ScheduleB> 
	  <ExportLicense>D123456</ExportLicense> 
	  <ShipperEIN>112233445566</ShipperEIN> 
	  <ShipperIDType>S</ShipperIDType> 
	  <ImportLicense>ImportLic</ImportLicense> 
	  <ConsigneeEIN>ConEIN2123</ConsigneeEIN> 
	  <TermsOfTrade>DTP</TermsOfTrade> 
	  </Dutiable>
	 <ShipmentDetails>
	  <NumberOfPieces>1</NumberOfPieces> 
	 <Pieces>
	 <Piece>
	  <PieceID>1</PieceID> 
	  <PackageType>YP</PackageType> 
	  <Weight>"""+parcel_weight_in_kg+"""</Weight> 
	  <DimWeight>0.0</DimWeight>
	  <Width>"""+parcel_width_in_cm+"""</Width> 
	  <Height>"""+parcel_height_in_cm+"""</Height>
	  <Depth>"""+parcel_length_in_cm+"""</Depth>
	  </Piece>
	  </Pieces>
	  <Weight>"""+parcel_weight_in_kg+"""</Weight> 
	  <WeightUnit>K</WeightUnit> 
	  <GlobalProductCode>D</GlobalProductCode> 
	  <LocalProductCode>U</LocalProductCode> 
	  <Date>"""+shipmentdate+"""</Date> 
	  <Contents>"""+content+"""</Contents> 
	  <DoorTo>DD</DoorTo> 
	  <DimensionUnit>C</DimensionUnit> 
	 <InsuredAmount>00.00</InsuredAmount>  
	 <PackageType>EE</PackageType> 
	  <IsDutiable>N</IsDutiable> 
	  <CurrencyCode>EUR</CurrencyCode> 
	  </ShipmentDetails>
	 <Shipper>
	  <ShipperID>12345</ShipperID> 
	  <CompanyName>"""+origin_company+"""</CompanyName> 
	  <RegisteredAccount>123456789</RegisteredAccount> 
	  <AddressLine>"""+origin_line1+"""</AddressLine> 
	  <AddressLine>"""+origin_line2+"""</AddressLine> 
	  <City>"""+origin_city+"""</City> 
	  <Division></Division> 
	  <PostalCode>"""+origin_zipcode+"""</PostalCode> 
	  <CountryCode>"""+origin_countrycode+"""</CountryCode> 
	  <CountryName>"""+origin_country+"""</CountryName> 
	 <Contact>
	  <PersonName>enquiry sing</PersonName> 
	  <PhoneNumber>"""+origin_phone+"""</PhoneNumber>
	  <PhoneExtension></PhoneExtension> 
	  <FaxNumber></FaxNumber> 
	  <Telex></Telex>
	  <Email>"""+origin_email+"""</Email> 
	  </Contact>
	  </Shipper>
	 <Place>
	  <ResidenceOrBusiness>B</ResidenceOrBusiness> 
	  <CompanyName>"""+origin_company+"""</CompanyName> 
	  <AddressLine>"""+origin_line1+"""</AddressLine> 
	  <AddressLine>"""+origin_line2+"""</AddressLine> 
	  <City>"""+origin_city+"""</City> 
	  <CountryCode>"""+origin_countrycode+"""</CountryCode> 
	  <DivisionCode>"""+origin_state+"""</DivisionCode> 
	  <Division>FR</Division> 
	  <PostalCode>"""+origin_zipcode+"""</PostalCode> 
	  <PackageLocation>"""+origin_packagelocation+"""</PackageLocation> 
	  </Place>
	  <EProcShip>N</EProcShip> 
  	<LabelImageFormat>PDF</LabelImageFormat> 
	</req:ShipmentRequest>"""
	c = boto.connect_s3("AKIAJKZ7KCBQFGFGD2ZA", "2HM3b8GPRMQFb4B86pokgXpk6A6bESo7R3NRRw61")
	b = c.get_bucket("srbstickers", validate=False)
	print b
	headers = {'Content-Type': 'application/xml'} # set what your server accepts
	resp=requests.post('https://xmlpitest-ea.dhl.com/XMLShippingServlet', data=xml, headers=headers).text
	print "start ET"
	# print resp

	# conn = tinys3.Connection('AKIAJIXKF5KD5RGPMTNQ','riG3NZfR8CpC2monYlvUaBXIFkYfKTw6nD8Q4',tls=True,endpoint='s3.us-east-2.amazonaws.com')
	

	root = ET.fromstring(resp)
	data=[]
	print root
	for child in root.findall('LabelImage'):
		pdf=child.find('OutputFormat').text+'.pdf'
		img_data=child.find('OutputImage').text
		#print pdf
		print img_data
		name_file=str(time.time())+".pdf"
		k = Key(b)
		print k
		k.key = name_file
		k.contentType="application/pdf"
		k.ContentDisposition="inline"
		# k.set_contents_from_string(img_data)
		k.set_contents_from_string(img_data.decode('base64'))
		link_pdf="https://s3-us-west-2.amazonaws.com/srbstickers/"+name_file

	#-------------
	shipmentId="0"
	allroot = ET.fromstring(resp)
	for getchild in allroot.findall('AirwayBillNumber'):
		if len(getchild)<0:
			shipmentId= ''
		else:
			shipmentId=getchild.text
	if shipmentId=="0":
		return resp

	data={
	  "origin": event["origin"],
	  "destination": event["destination"],
	  "parcel": event["parcel"],
	  "shipment_id": shipmentId,
	  "label_url": link_pdf
	}
	return data
# print getLabel('12','22')

