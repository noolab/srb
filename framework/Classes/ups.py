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
UPS_LABEL_URL = "https://wwwcie.ups.com/webservices/Ship"
class ups(Service):
	"""docstring for envialia"""
	def root(self,userparamlist):
		return {}
	
	def label(self,userparamlist):


		payload="""<envr:Envelope xmlns:auth="http://www.ups.com/schema/xpci/1.0/auth"
			xmlns:envr="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
			xmlns:upss="http://www.ups.com/XMLSchema/XOLTWS/UPSS/v1.0"
			xmlns:common="http://www.ups.com/XMLSchema/XOLTWS/Common/v1.0"
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
			<envr:Header>
			          <upss:UPSSecurity>
			          <upss:UsernameToken>
			          <upss:Username>Freightways123</upss:Username>
			          <upss:Password>Ups-1234</upss:Password>
			          </upss:UsernameToken>
			          <upss:ServiceAccessToken>
			          <upss:AccessLicenseNumber>5D2DB91AA1ED058C</upss:AccessLicenseNumber>
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
			                    <ship:Name>Shoprunback</ship:Name>
			                    <ship:AttentionName>Shoprunback</ship:AttentionName>
			                    <ship:Phone>
			                    <ship:Number>1234567890</ship:Number>
			                    </ship:Phone>
			                    <ship:Address>
			                    <ship:AddressLine>20 rue de paradis</ship:AddressLine>
			                    <ship:City>AMSTERDAM</ship:City>
			                    <ship:PostalCode>1092</ship:PostalCode>
			                    <ship:CountryCode>NL</ship:CountryCode>
			                    </ship:Address>
			              </ship:ShipTo>
			              <ship:ShipFrom>
			                    <ship:Name>Ithyvan</ship:Name>
			                    <ship:AttentionName>ITHYVAN</ship:AttentionName>
			                    <ship:Phone>
			                    <ship:Number>1234567890</ship:Number>
			                    </ship:Phone>
			                    <ship:Address>
			                    <ship:AddressLine>21 rue de paradis</ship:AddressLine>
			                    <ship:City>AMSTERDAM</ship:City>
			                    <ship:PostalCode>1092</ship:PostalCode>
			                    <ship:CountryCode>NL</ship:CountryCode>
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
			                      <ship:Length>7</ship:Length>
			                      <ship:Width>5</ship:Width>
			                      <ship:Height>2</ship:Height>
			                </ship:Dimensions>
			                <ship:PackageWeight>
			                      <ship:UnitOfMeasurement>
			                            <ship:Code>KGS</ship:Code>
			                      </ship:UnitOfMeasurement>
			                      <ship:Weight>0.5</ship:Weight>
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
		k.set_contents_from_string(base64.b64decode(img_data.encode('ascii')))	
		
		link_pdf = "https://s3-us-west-2.amazonaws.com/srbstickers/" + name_file
		data = {
			"origin": userparamlist["origin"],
			"destination": userparamlist["destination"],
			"parcel": userparamlist["parcel"],
			"shipment_id": shipment_id,
			"label_url": link_pdf
		}
		return data