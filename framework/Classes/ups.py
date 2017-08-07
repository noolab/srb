from Classes.AbstractService import Service
from BuiltInService import requests 
from Modules.data_converter import data_converter as converter
from Modules.data_validator import Validator 
from Modules.network import networking as netw
from BuiltInService import xmltodict
import os
from random import randrange

import re
import time
import datetime
import xml.etree.ElementTree as ET
import json
import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
UPS_LABEL_URL = os.environ["UPS_LABEL_URL"] 
UPS_USERNAME =  os.environ["UPS_USERNAME"]
UPS_PASSWD = os.environ["UPS_PASSWD"]
UPS_ACCESSLICENCE_NUMBER  =  os.environ["UPS_ACCESSLICENCE_NUMBER"]
UPS_TRACK_URL = os.environ["UPS_TRACK_URL"]
UPS_STATUS_URL = os.environ["UPS_STATUS_URL"]

class ups(Service):
	"""docstring for envialia"""
	def root(self,userparamlist):
		true=True
		data={
			"/":{
				"get":true
			},
			"type":{
				"get":true
			},
			"label":{
				"get":true
			},
			"status":{
				"get":true
			}
		}
		return data

	def type(self,paramlist):
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
	def status(self,paramlist):
		start=time.time()
		available=True
		response_time=0
		try:
			# xmlresponse=netw.sendRequest(UPS_STATUS_URL,"","get","","")
			xmlresponse= requests.get(UPS_STATUS_URL)
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

	def tracking(self,paramlist):
		trackingNumber = str(paramlist)
		payload="""<soapenv:Envelope
			xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
			xmlns:v1="http://www.ups.com/XMLSchema/XOLTWS/UPSS/v1.0"
			xmlns:v3="http://www.ups.com/XMLSchema/XOLTWS/Track/v2.0"
			xmlns:v11="http://www.ups.com/XMLSchema/XOLTWS/Common/v1.0">
			<soapenv:Header>
				<v1:UPSSecurity>
					<v1:UsernameToken>
						<v1:Username>"""+UPS_USERNAME+"""</v1:Username>
						<v1:Password>"""+UPS_PASSWD+"""</v1:Password>
					</v1:UsernameToken>
					<v1:ServiceAccessToken>
						<v1:AccessLicenseNumber>"""+UPS_ACCESSLICENCE_NUMBER+"""</v1:AccessLicenseNumber>
					</v1:ServiceAccessToken>
				</v1:UPSSecurity>
			</soapenv:Header>
			<soapenv:Body>
				<v3:TrackRequest>
					<v11:Request>
						<v11:RequestOption>1</v11:RequestOption>
						<v11:TransactionReference>
							<v11:CustomerContext>Your Test Case Summary Description</v11:CustomerContext>
						</v11:TransactionReference>
					</v11:Request>
					<v3:InquiryNumber>"""+trackingNumber+"""</v3:InquiryNumber>
				</v3:TrackRequest>
			</soapenv:Body>
		</soapenv:Envelope>"""
		headersConfig = {'content-type': 'text/xml;charset="utf-8"'}
		try:
			response=requests.post(UPS_TRACK_URL, data=payload, headers=headersConfig).text
			data = xmltodict.parse(response)
		except:
			return response

		try:
			# allres = data["soapenv:Envelope"]["soapenv:Body"]["trk:TrackResponse"]["trk:Shipment"]["trk:Package"]["trk:Activity"]
			location =  data["soapenv:Envelope"]["soapenv:Body"]["trk:TrackResponse"]["trk:Shipment"]["trk:Package"]["trk:Activity"]["trk:ActivityLocation"]["trk:Address"]["trk:City"]
			status = data["soapenv:Envelope"]["soapenv:Body"]["trk:TrackResponse"]["trk:Shipment"]["trk:Package"]["trk:Activity"]["trk:Status"]["trk:Description"]
		except:
			return response

		final_data=[{
			"steps": [{
				"status": status,
				"location": location
			}]
		}]
		return final_data
	
	def label(self,userparamlist):
		paramlist = {}
		paramlist["origin"] ={}
		paramlist["origin"]["phone"]=""

		req_list=["origin/name","origin/first_name","origin/last_name","origin/city","origin/zipcode","origin/country_code","destination/name","destination/phone","destination/zipcode","destination/country_code"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
		else:
			return checkparamlist["message"]

		attentionNameOri = str(paramlist["origin"]["first_name"]) + str(paramlist["origin"]["last_name"])
		attentionNameDes =str(paramlist["destination"]["first_name"])+ str(paramlist["destination"]["last_name"])
		weight_in_kg = str(float(paramlist["parcel"]["weight_in_grams"])/1000)
		
		payload="""<envr:Envelope xmlns:auth="http://www.ups.com/schema/xpci/1.0/auth"
			xmlns:envr="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
			xmlns:upss="http://www.ups.com/XMLSchema/XOLTWS/UPSS/v1.0"
			xmlns:common="http://www.ups.com/XMLSchema/XOLTWS/Common/v1.0"
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
			<envr:Header>
			          <upss:UPSSecurity>
			          <upss:UsernameToken>
			          <upss:Username>"""+UPS_USERNAME+"""</upss:Username>
			          <upss:Password>"""+UPS_PASSWD+"""</upss:Password>
			          </upss:UsernameToken>
			          <upss:ServiceAccessToken>
			          <upss:AccessLicenseNumber>"""+UPS_ACCESSLICENCE_NUMBER+"""</upss:AccessLicenseNumber>
			          </upss:ServiceAccessToken>
			          </upss:UPSSecurity>
			</envr:Header>
			<envr:Body>
			      <ship:ShipmentRequest xsi:schemaLocation="http://www.ups.com/XMLSchema/XOLTWS/Ship/v1.0"
			      xmlns:ship="http://www.ups.com/XMLSchema/XOLTWS/Ship/v1.0"
			      xmlns:ifs="http://www.ups.com/XMLSchema/XOLTWS/IF/v1.0">
			      <common:Request>
			            <common:RequestOption>nonvalidate</common:RequestOption>
			            <common:TransactionReference>
			            <common:CustomerContext>Your Customer Context</common:CustomerContext>
			            </common:TransactionReference>
			            </common:Request>
			      <ship:Shipment>
			              <ship:ReturnService>
			                    <ship:Code>9</ship:Code>
			              </ship:ReturnService>

			              <ship:Description>Description</ship:Description>
			              <ship:Shipper>
			                    <ship:Name>Hamza Alaya</ship:Name>
			                    <ship:AttentionName>ALAYA</ship:AttentionName>
			                    <ship:Phone>
			                    <ship:Number>1234567890</ship:Number>
			                    </ship:Phone>
			                    <ship:ShipperNumber>9R5R36</ship:ShipperNumber>
			                    <ship:FaxNumber>1234567890</ship:FaxNumber>
			                    <ship:Address>
			                    <ship:AddressLine>21 rue du bas</ship:AddressLine>
			                    <ship:City>AMSTERDAM</ship:City>
			                    <ship:PostalCode>1093</ship:PostalCode>
			                    <ship:CountryCode>NL</ship:CountryCode>
			                    </ship:Address>
			              </ship:Shipper>
			              <ship:ShipTo>
			                    <ship:Name>"""+paramlist["destination"]["company"]+"""</ship:Name>
			                    <ship:AttentionName>"""+attentionNameDes+"""</ship:AttentionName>
			                    <ship:Phone>
			                    <ship:Number>"""+paramlist["destination"]["phone"]+"""</ship:Number>
			                    </ship:Phone>
			                    <ship:Address>
			                    <ship:AddressLine>"""+paramlist["destination"]["line1"]+"""</ship:AddressLine>
			                    <ship:City>"""+paramlist["destination"]["city"]+"""</ship:City>
			                    <ship:PostalCode>"""+paramlist["destination"]["zipcode"]+"""</ship:PostalCode>
			                    <ship:CountryCode>"""+paramlist["destination"]["country_code"]+"""</ship:CountryCode>
			                    </ship:Address>
			              </ship:ShipTo>
			              <ship:ShipFrom>
			                    <ship:Name>"""+paramlist["origin"]["company"]+"""</ship:Name>
			                    <ship:AttentionName>"""+attentionNameOri+"""</ship:AttentionName>
			                    <ship:Phone>
			                    <ship:Number>"""+paramlist["origin"]["phone"]+"""</ship:Number>
			                    </ship:Phone>
			                    <ship:Address>
			                    <ship:AddressLine>"""+paramlist["origin"]["line1"]+"""</ship:AddressLine>
			                    <ship:City>"""+paramlist["origin"]["city"]+"""</ship:City>
			                    <ship:PostalCode>"""+paramlist["origin"]["zipcode"]+"""</ship:PostalCode>
			                    <ship:CountryCode>"""+paramlist["origin"]["country_code"]+"""</ship:CountryCode>
			                    </ship:Address>
			              </ship:ShipFrom>
			              <ship:PaymentInformation>
			                    <ship:ShipmentCharge>
			                    <ship:Type>01</ship:Type>
			                    <ship:BillShipper>
			                    <ship:AccountNumber>9R5R36</ship:AccountNumber>
			                    </ship:BillShipper>
			                    </ship:ShipmentCharge>
			              </ship:PaymentInformation>
			              <ship:Service>
			                    <ship:Code>11</ship:Code>n>
			              </ship:Service>
			             <ship:Package>
			                <ship:Description>Description</ship:Description>
			                <ship:Packaging>
			                      <ship:Code>02</ship:Code>
			                      <ship:Description>Description</ship:Description>
			                </ship:Packaging>
			                <ship:Dimensions>
			                      <ship:UnitOfMeasurement>
			                            <ship:Code>CM</ship:Code>
			                      </ship:UnitOfMeasurement>
			                      <ship:Length>"""+str(paramlist["parcel"]["length_in_cm"])+"""</ship:Length>
			                      <ship:Width>"""+str(paramlist["parcel"]["width_in_cm"])+"""</ship:Width>
			                      <ship:Height>"""+str(paramlist["parcel"]["height_in_cm"])+"""</ship:Height>
			                </ship:Dimensions>
			                <ship:PackageWeight>
			                      <ship:UnitOfMeasurement>
			                            <ship:Code>KGS</ship:Code>
			                      </ship:UnitOfMeasurement>
			                      <ship:Weight>"""+str(weight_in_kg)+"""</ship:Weight>
			                </ship:PackageWeight>
			             </ship:Package>
			      </ship:Shipment>
			      <ship:LabelSpecification>
			              <ship:LabelImageFormat>
			                    <ship:Code>GIF</ship:Code>
			                    <ship:Description>GIF</ship:Description>
			              </ship:LabelImageFormat>
			              <ship:HTTPUserAgent>Mozilla/4.5</ship:HTTPUserAgent>
			      </ship:LabelSpecification>
			      </ship:ShipmentRequest>
			</envr:Body>
			</envr:Envelope>"""
		headersConfig = {'content-type': 'text/xml;charset="utf-8"'}
		response = netw.sendRequestHeaderConfig(UPS_LABEL_URL, payload, "post", headersConfig)
		data = xmltodict.parse(response)
		try:
			img_data = data["soapenv:Envelope"]["soapenv:Body"]["ship:ShipmentResponse"]["ship:ShipmentResults"]["ship:PackageResults"]["ship:ShippingLabel"]["ship:GraphicImage"]
			
		except:
			return response
		try:
			shipment_id = data["soapenv:Envelope"]["soapenv:Body"]["ship:ShipmentResponse"]["ship:ShipmentResults"]["ship:ShipmentIdentificationNumber"]
		except:
			shipment_id ='0000'
		c = boto.connect_s3(os.environ["AWS_S3_KEY1"], os.environ["AWS_S3_KEY2"])
		bucket = c.get_bucket("srbstickers", validate=False)
		name_file = str(time.time()) + ".pdf"
		k = Key(bucket)
		k.key = name_file
		k.contentType="application/pdf"
		k.ContentDisposition="inline"
		# k.set_contents_from_string(base64.b64decode(img_data.encode('ascii')))
		imgpic =str(time.time()) + ".png"
		with open('/tmp/'+imgpic, 'wb') as f:
	 		f.write(base64.b64decode(img_data.encode('ascii')))
	 		# f.write(base64.b64decode(img_data))
		filedir = '/tmp/'+imgpic
		k.set_contents_from_filename(filedir)
		link_pdf = "https://s3-us-west-2.amazonaws.com/srbstickers/" + name_file
		data = {
			"origin": paramlist["origin"],
			"destination": paramlist["destination"],
			"parcel": paramlist["parcel"],
			"shipment_id": shipment_id,
			"label_url": link_pdf
		}
		return data