import requests
import boto
import time
from boto.s3.key import Key
import xml.etree.ElementTree as ET
import base64
import datetime
import re
import os
# import tinys3
from boto.s3.connection import S3Connection
def getLabel(event,context):
	date = datetime.datetime.now()
	datenow=re.sub(r'\s.*','',str(date))
	messageTime=str(datenow)+"T11:28:56.000-08:00"


	if "shipment_date" not in event:
		return "shipmentdate is missing..."

	shipmentdate=str(event["shipment_date"])

	if shipmentdate=="":
		return "shipmentdate is missing..."

	if "shipment_id" not in event["destination"]:
		return "destination_shipmentId is missing..."
	destination_shipmentId=str(event["destination"]["shipment_id"])
	if destination_shipmentId=="":
		return "destination_shipmentId is missing..."

	if "company" not in event["destination"]:
		return "CompanyName destination  is missing..."

	destination_company=str(event["destination"]["company"])

	if destination_company=="":
		return "CompanyName destination is missing..."
	if "line1" not in event["destination"]:
		return "One of the address in destination must be completed..."
	if "line2" not in event["destination"]:
		return "one of the addressin destination must be completed.."

	destination_line1=str(event["destination"]["line1"])
	destination_line2=str(event["destination"]["line2"])

	if destination_line1=="" and destination_line2=="":
		return "One of the address in destination must be completed..."

	destination_line1=destination_line1+" "+destination_line2
	if "city" not in event["destination"]:
		return "city in  destination  is missing..."
	destination_city=str(event["destination"]["city"])
	if "state" not in event["destination"]:
		return "state in  destination  is missing..."
	destination_state=str(event["destination"]["state"])

	if "zipcode" not in event["destination"]:
		return "zipcode in  destination  is missing..."
	destination_zipcode=str(event["destination"]["zipcode"])

	if "country_code" not in event["destination"]:
		return "destination_countryCode  is missing..."
	destination_countryCode=str(event["destination"]["country_code"])
	if destination_countryCode=="":
		return "destination_countryCode is mandatory"
	if "country" not in event["destination"]:
		return "destination_country_name is missing"

	destination_country=str(event["destination"]["country"])
	if destination_country=="":
		return "destination_country_name is mandatory"
	if "name" not in event["destination"]:
		return "destination_name is missing.."
	destination_name=str(event["destination"]["name"])
	if destination_name=="":
		return "destination_name is mandatory"
	if "phone" not in event["destination"]:
		return "destination_phone is missing .."
	destination_phone=str(event["destination"]["phone"])
	if destination_phone=="":
		return "destination_phone is mandatory"

	if "first_name" not in event["destination"]:
		return "destination_firstname is missing ...."
	destination_firstname=str(event["destination"]["first_name"])

	if "last_name" not in event["destination"]:
		return "destination_lastname is missing .."
	destination_lastname=str(event["destination"]["last_name"])
	
	if "email" not in event["destination"]:
		return "destination_email is missing ..."
	destination_email=str(event["destination"]["email"])

	if "weight_in_grams" not in event["parcel"]:
		return "weight_in_grams is missing ..."
	parcel_weight_in_grams=str(event["parcel"]["weight_in_grams"])
	parcel_weight_in_grams=str(float(parcel_weight_in_grams)/1000)
	if parcel_weight_in_grams <= "0":
		parcel_weight_in_grams="0.0"

	if "width_in_cm" not in event["parcel"]:
		return "width_in_cm is missing .."
	parcel_width_in_cm=str(event["parcel"]["width_in_cm"])
	if parcel_width_in_cm=="0":
		return "width_in_cm must be more than 0"
	if "height_in_cm" not in event["parcel"]:
		return "height_in_cm is missing .."
	parcel_height_in_cm=str(event["parcel"]["height_in_cm"])
	

	if "length_in_cm" not in event["parcel"]:
		return "length_in_cm is missing.."
	parcel_length_in_cm=str(event["parcel"]["length_in_cm"])
	if parcel_length_in_cm=="0":
		return "parcel_length_in_cm cannot be 0"

	if "contents" not in event:
		content=""
	else:
		content= str(event["contents"])

	if "first_name" not in event["origin"]:
		return "origin_firstname is missing .."
	origin_firstname=str(event["origin"]["first_name"])
	if origin_firstname=="":
		return "origin_firstname cannot be empty"
	if "last_name" not in event["origin"]:
		return "origin_lastname is missing"
	origin_lastname=str(event["origin"]["last_name"])
	if origin_lastname=="":
		return "origin_lastname cannot be empty"
	if "company" not in event["origin"]:
		return "origin_company is missing"
	origin_company=str(event["origin"]["company"])
	# if origin_company=="":
	# 	return "origin_company cannot be empty"
	if "city" not in event["origin"]:
		return "origin_city is missing.."
	origin_city=str(event["origin"]["city"])

	if origin_city=="":
		return "origin_city cannot be empty"
	if "line1" not in event["origin"]:
		return "origin_line1 is missing"
	origin_line1=str(event["origin"]["line1"])
	if origin_line1 =="":
		return "origin_line1 cannot be empty"
	if "line2" not in event["origin"]:
		return "origin_line2 is missing"

	origin_line2=str(event["origin"]["line2"])+""
	# if origin_line2=="":
	# 	return "origin_line2 cannot be empty"
	# if origin_line1=="" and origin_line2=="":
	# 	return "origin_line1_address is mandatory"
	origin_line1=origin_line1+" "+origin_line2

	if "country" not in event["origin"]:
		return "origin_country is missing"

	origin_country=str(event["origin"]["country"])
	if origin_country=="":
		return "origin_country cannot be empty"
	if "zipcode" not in event["origin"]:
		return "origin zipcode is missing "
	origin_zipcode=str(event["origin"]["zipcode"])+""
	# if origin_zipcode=="":
	#  	return "origin_zipcode cannot be empty "

	if "country_code" not in event["origin"]:
		return "origin_countrycode is missing..."

	origin_countrycode=str(event["origin"]["country_code"])
	if origin_countrycode=="":
		return "origin_countrycode cannot be empty"

	if "name" not in event["origin"]:
		return "origin_name is missing.."
	origin_name=str(event["origin"]["name"])
	if origin_name=="":
		return "origin_name cannot be empty"
	if "phone" not in event["origin"]:
		return "origin_phone is missing..."
	origin_phone=str(event["origin"]["phone"])
	if origin_phone == "":
		return "origin_phone cannot be empty"
	if "email" not in event["origin"]:
		return "origin email is missing .."
	origin_email=str(event["origin"]["email"])
	# if origin_email =="":
	# 	return 'origin_email cannot be empty'
	if "state" not in event["origin"]:
		return "origin_state is missing.."
	origin_state=str(event["origin"]["state"])
	# if origin_state=="":
	# 	return "origin_state cannot be empty"
	if "place_description" not in event["origin"]:
		return "place_description is missing"
	origin_packagelocation=str(event["origin"]["place_description"])
	# if origin_packagelocation=='':
	# 	return "origin_packagelocation cannot be empty"
	xml="""  <?xml version="1.0" encoding="UTF-8" ?> 
	 <req:ShipmentRequest xmlns:req="http://www.dhl.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.dhl.com ship-val-global-req.xsd" schemaVersion="1.0">
	 <Request>
	 <ServiceHeader> 
	  <MessageTime>"""+messageTime+"""</MessageTime>
	  <MessageReference>1234567890123456789012345678901</MessageReference>
	  <SiteID>"""+os.environ["DHL_USERID"]+"""</SiteID> 
	  <Password>"""+os.environ["DHL_PWD"]+"""</Password>
	  </ServiceHeader>
	  </Request>
	  <RegionCode>EU</RegionCode> 
	  <NewShipper>Y</NewShipper> 
	  <LanguageCode>en</LanguageCode> 
	  <PiecesEnabled>Y</PiecesEnabled> 
	 <Billing>
	  <ShipperAccountNumber>223932540</ShipperAccountNumber> 
	  <ShippingPaymentType>S</ShippingPaymentType> 
	  <BillingAccountNumber>223932540</BillingAccountNumber> 
	  <DutyPaymentType>R</DutyPaymentType> 
	  </Billing>
	 <Consignee>
	  <CompanyName>"""+destination_company+"""</CompanyName> 
	  <AddressLine>"""+destination_line1+"""</AddressLine> 
	  <City>"""+destination_city+"""</City> 
	  <Division>"""+destination_state+"""</Division> 
	  <PostalCode>"""+destination_zipcode+"""</PostalCode> 
	  <CountryCode>"""+destination_countryCode+"""</CountryCode> 
	  <CountryName>"""+destination_country+"""</CountryName> 
	 <Contact>
	  <PersonName>"""+destination_firstname+" "+destination_lastname+"""</PersonName> 
	  <PhoneNumber>"""+destination_phone+"""</PhoneNumber>
	  <Email>"""+destination_email+"""</Email>
	  <MobilePhoneNumber>"""+destination_phone+"""</MobilePhoneNumber> 
	</Contact>
	  </Consignee>
	 <Commodity>
	  <CommodityCode>"""+destination_shipmentId+"""</CommodityCode> 
	  </Commodity>
	 <ShipmentDetails>
	  <NumberOfPieces>1</NumberOfPieces> 
	 <Pieces>
	 <Piece>
	  <PieceID>1</PieceID> 
	  <PackageType>YP</PackageType> 
	  <Weight>"""+parcel_weight_in_grams+"""</Weight> 
	  <Width>"""+parcel_width_in_cm+"""</Width> 
	  <Height>"""+parcel_height_in_cm+"""</Height> 
	  <Depth>"""+parcel_length_in_cm+"""</Depth> 
	  </Piece>
	  </Pieces>
	  <Weight>"""+parcel_weight_in_grams+"""</Weight> 
	  <WeightUnit>K</WeightUnit> 
	  <GlobalProductCode>D</GlobalProductCode> 
	  <Date>"""+shipmentdate+"""</Date>  
	  <DimensionUnit>C</DimensionUnit> 
	  <Content>"""+content+"""</Content>
	  <CurrencyCode>EUR</CurrencyCode> 
	  </ShipmentDetails>
	 <Shipper>
	  <ShipperID>12345</ShipperID> 
	  <CompanyName>"""+origin_company+"""</CompanyName> 
	  <AddressLine>"""+origin_line1+"""</AddressLine> 
	  <AddressLine>"""+origin_line2+"""</AddressLine> 
	  <City>"""+origin_city+"""</City> 
	  <Division></Division> 
	  <PostalCode>"""+origin_zipcode+"""</PostalCode> 
	  <CountryCode>"""+origin_countrycode+"""</CountryCode> 
	  <CountryName>"""+origin_country+"""</CountryName> 
	 <Contact>
	  <PersonName>"""+origin_firstname+" "+origin_lastname+"""</PersonName>
	  <PhoneNumber>"""+origin_phone+"""</PhoneNumber> 
	  <Email>"""+origin_email+"""</Email> 
	  </Contact>
	  </Shipper>
	  <SpecialService>
  	<SpecialServiceType>PT</SpecialServiceType>
  	</SpecialService> 
	 <Place>
	  <ResidenceOrBusiness>R</ResidenceOrBusiness> 
	  <CompanyName>"""+origin_company+"""</CompanyName> 
	  <AddressLine>"""+origin_line1+"""</AddressLine>
	  <City>"""+origin_city+"""</City> 
	  <CountryCode>"""+origin_countrycode+"""</CountryCode> 
	  <Division>"""+origin_state+"""</Division> 
	  <PostalCode>"""+origin_zipcode+"""</PostalCode> 
	  <PackageLocation>"""+origin_packagelocation+"""</PackageLocation> 
	  </Place>
	  <EProcShip>N</EProcShip> 
  	<LabelImageFormat>PDF</LabelImageFormat>
	</req:ShipmentRequest>"""
	print xml
	c = boto.connect_s3(os.environ["S3_PUB_KEY"], os.environ["S3_PRV_KEY"])
	b = c.get_bucket(os.environ["S3_BUCKET_NAME"], validate=False)
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
		link_pdf=os.environ["S3_URL"]+name_file

	#-------------
	allroot = ET.fromstring(resp)
	shipmentId="0"
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

