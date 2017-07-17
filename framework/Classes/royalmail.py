from Classes.AbstractService import Service
from BuiltInService import requests
import xml.etree.ElementTree as ET
from Modules.data_converter import data_converter as converter
from Modules.data_validator import Validator 
from Modules.network import networking as netw
from BuiltInService import xmltodict
import time
import datetime
import re
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import os
# import sha
import hashlib
import binascii
import base64
import random

import http.client
# import requests
conn = http.client.HTTPSConnection("api.royalmail.net")
ROYALMAIL_URL= os.environ["ROYALMAIL_URL"]
ROYALMAIL_AUTH_PWD = os.environ["ROYALMAIL_AUTH_PWD"]
ROYALMAIL_USERNAME =	os.environ["ROYALMAIL_USERNAME"]
ROYALMAIL_APPID = os.environ["ROYALMAIL_APPID"]
ROYALMAIL_TRANSACTIONID = os.environ["ROYALMAIL_TRANSACTIONID"]
ROYALMAIL_CLIENT_ID = os.environ["ROYALMAIL_CLIENT_ID"]
ROYALMAIL_SECRET_ID = os.environ["ROYALMAIL_SECRET_ID"]
class royalmail(Service):

	def root(self,paramlist):
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
		date = datetime.datetime.now()
		datenow=re.sub(r'\s.*','',str(date))
		tree = ET.parse('Assets/royalmail/requests/createshipment.txt')
		root = tree.getroot()
		
		start=time.time()
		available=True
		response_time=0
		xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		try:
			xmlresponse = netw.sendRequest(ROYALMAIL_URL, xmlresult, "post", "xml", "xml")
			xmlroot = ET.fromstring(xmlresponse)
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

	def getAuth(self):
		password = ROYALMAIL_AUTH_PWD
		creationDate =  time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(time.time()))
		
		nonce =  str(random.randint(0,9999999999))+''
		nonce=nonce.encode('ascii')

		hashedPassword = base64.b64encode(hashlib.sha1(password.encode('UTF-8')).digest())
		digest = hashlib.sha1(nonce + creationDate.encode('UTF-8') + hashedPassword.decode("utf-8").encode('UTF-8')).digest()
		passwordDigest = base64.b64encode(digest)

		encodedNonce = base64.b64encode(nonce)

		  
		print ('nonce:', nonce)
		print ('password digest:', passwordDigest)
		print ('encoded nonce:', encodedNonce)
		print ('creation date:', creationDate)

		return [passwordDigest,encodedNonce,creationDate]

	def label(self,userparamlist):
		auth=self.getAuth()
		auth_pwd= auth[0].decode("utf-8")
		auth_nonce= auth[1].decode("utf-8")
		auth_created= str(auth[2])  #.decode('utf-8')

		paramlist={}
		paramlist["origin"]={}
		paramlist["origin"]["line2"]=""
		paramlist["destination"]={}
		paramlist["destination"]["line2"]=""
		paramlist["destination"]["email"]=""
		paramlist["parcel"]={}
		paramlist["parcel"]["weight_in_grams"]=""
		paramlist["parcel"]["length_in_cm"]=""
		paramlist["parcel"]["width_in_cm"] = ""
		paramlist["parcel"]["height_in_cm"] =""
		req_list=["destination/line1","origin/line1","shipment_date","destination/name","destination/phone","destination/zipcode","destination/country_code"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
		else:
			return checkparamlist["message"]

		payload = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:oas="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:v2="http://www.royalmailgroup.com/api/ship/V2" xmlns:v1="http://www.royalmailgroup.com/integration/core/V1">
		   <soapenv:Header>
		<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
		                   <wsse:UsernameToken>
		                      <wsse:Username>"""+ROYALMAIL_USERNAME+"""</wsse:Username>
		                      <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">""" + auth_pwd + """</wsse:Password>
		                      <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">""" + auth_nonce+ """</wsse:Nonce>
		                      <wsu:Created>""" +auth_created+ """</wsu:Created>
		                   </wsse:UsernameToken>
		        </wsse:Security>
		</soapenv:Header>
		   <soapenv:Body>
		      <v2:createShipmentRequest>
		         <v2:integrationHeader>
		            <v1:version>2</v1:version>
		            <v1:identification>
		               <v1:applicationId>"""+ROYALMAIL_APPID+"""</v1:applicationId>
		               <v1:transactionId>"""+ROYALMAIL_TRANSACTIONID+"""</v1:transactionId>
		            </v1:identification>
		         </v2:integrationHeader>
		         <v2:requestedShipment>
		            <!--Optional:-->
		            <v2:shipmentType>
		               <code>Return</code>
		            </v2:shipmentType>
		            <!--Optional:-->
		            <v2:serviceOccurrence>1</v2:serviceOccurrence>
		            <!--Optional:-->
		            <v2:serviceType>
		               <code>R</code>
		            </v2:serviceType>
		            <!--Optional:-->
		            <v2:serviceOffering>
		               <serviceOfferingCode>
		                  <code>TSS</code>
		               </serviceOfferingCode>
		            </v2:serviceOffering>
		            <!--Optional:-->
		            <v2:serviceFormat>
		            	<serviceFormatCode>
		            		<code>E</code>
		               </serviceFormatCode>
		            </v2:serviceFormat>
		            <v2:shippingDate>"""+paramlist["shipment_date"]+"""</v2:shippingDate>
	               <v2:recipientContact>
	                  <v2:name>"""+paramlist["destination"]["name"]+"""</v2:name>
	                  <v2:complementaryName></v2:complementaryName>
	                  <v2:telephoneNumber>
	                     <countryCode>0044</countryCode>
	                     <telephoneNumber>"""+paramlist["destination"]["phone"]+"""</telephoneNumber>
	                  </v2:telephoneNumber>
	                  <v2:electronicAddress>
	                     <electronicAddress>"""+paramlist["destination"]["email"]+"""</electronicAddress>
	                  </v2:electronicAddress>
	               </v2:recipientContact>
	               <v2:recipientAddress>
	                  <addressLine1>"""+paramlist["destination"]["line1"]+"""</addressLine1>
	                  <addressLine2>"""+paramlist["destination"]["line2"]+"""</addressLine2>
	                  <postTown>Cairo</postTown>
	                  <postcode>"""+paramlist["destination"]["zipcode"]+"""</postcode>
	                  <country>
	                     <countryCode>
	                        <code>"""+paramlist["destination"]["country_code"]+"""</code>
	                     </countryCode>
	                  </country>
	               </v2:recipientAddress>
		            <v2:customerReference>CustSuppRef1</v2:customerReference>
		            <v2:senderReference>SenderReference1</v2:senderReference>
		            <v2:internationalInfo>
		               <v2:parcels>
		                  <v2:parcel>
		                     <v2:weight>
		                        <unitOfMeasure>
		                           <unitOfMeasureCode>
		                              <code>g</code>
		                           </unitOfMeasureCode>
		                        </unitOfMeasure>
		                        <value>"""+str(paramlist["parcel"]["weight_in_grams"])+"""</value>
		                     </v2:weight>
		                     <v2:length>
		                        <unitOfMeasure>
		                           <unitOfMeasureCode>
		                              <code>g</code>
		                           </unitOfMeasureCode>
		                        </unitOfMeasure>
		                        <value>"""+str(paramlist["parcel"]["length_in_cm"])+"""</value>
		                     </v2:length>
		                     <v2:height>
		                        <unitOfMeasure>
		                           <unitOfMeasureCode>
		                              <code>cm</code>
		                           </unitOfMeasureCode>
		                        </unitOfMeasure>
		                        <value>"""+str(paramlist["parcel"]["height_in_cm"])+"""</value>
		                     </v2:height>
		                     <v2:width>
		                        <unitOfMeasure>
		                           <unitOfMeasureCode>
		                              <code>cm</code>
		                           </unitOfMeasureCode>
		                        </unitOfMeasure>
		                        <value>"""+str(paramlist["parcel"]["width_in_cm"])+"""</value>
		                     </v2:width>
		                     <v2:purposeOfShipment>
		                        <code>31</code>
		                     </v2:purposeOfShipment>
		                     <v2:invoiceNumber>INV001</v2:invoiceNumber><v2:contentDetails>
		                        <v2:contentDetail>
		                           <v2:countryOfManufacture>
		                              <countryCode>
		                                 <code>GB</code>
		                              </countryCode>
		                           </v2:countryOfManufacture>
		                           <v2:description>Personal Effects</v2:description>
		                           <v2:unitWeight>
		                              <unitOfMeasure>
		                                 <unitOfMeasureCode>
		                                    <code>g</code>
		                                 </unitOfMeasureCode>
		                              </unitOfMeasure>
		                              <value>3</value>
		                           </v2:unitWeight>
		                           <v2:unitQuantity>1</v2:unitQuantity>
		                           <v2:unitValue>500</v2:unitValue>
		                           <v2:currencyCode>
		                              <code>GBP</code>
		                           </v2:currencyCode>
		                           <v2:tariffCode>
		                              <code>22</code>
		                           </v2:tariffCode>
		                           <v2:tariffDescription>
		                              <code>tarDesc1</code>
		                           </v2:tariffDescription>
		                           <v2:articleReference>1</v2:articleReference>
		                        </v2:contentDetail>
		                        <v2:contentDetail>
		                           <v2:countryOfManufacture>
		                              <countryCode>
		                                 <code>FR</code>
		                              </countryCode>
		                           </v2:countryOfManufacture>
		                           <v2:manufacturersName>Tissot</v2:manufacturersName>
		                           <v2:description>Wrist Watch</v2:description>
		                           <v2:unitWeight>
		                              <unitOfMeasure>
		                                 <unitOfMeasureCode>
		                                    <code>1</code>
		                                 </unitOfMeasureCode>
		                              </unitOfMeasure>
		                              <value>500</value>
		                           </v2:unitWeight>
		                           <v2:unitQuantity>1</v2:unitQuantity>
		                           <v2:unitValue>278</v2:unitValue>
		                           <v2:currencyCode>
		                              <code>GBP</code>
		                           </v2:currencyCode>
		                           <v2:tariffCode>
		                              <code>44</code>
		                           </v2:tariffCode>
		                           <v2:tariffDescription>
		                              <code>tarDesc2</code>
		                           </v2:tariffDescription>
		                           <v2:articleReference>2</v2:articleReference>
		                        </v2:contentDetail>
		                     </v2:contentDetails>
		                  </v2:parcel>
		               </v2:parcels>
		               <v2:invoiceDate>2017-07-04</v2:invoiceDate>
		               <v2:termsOfDelivery>EXW</v2:termsOfDelivery>
		               <v2:purchaseOrderRef>PURCH1</v2:purchaseOrderRef>
		            </v2:internationalInfo>
		         </v2:requestedShipment>
		      </v2:createShipmentRequest>
		   </soapenv:Body>
		</soapenv:Envelope>"""

		headersConfig = {
		    'x-ibm-client-id': ROYALMAIL_CLIENT_ID,
		    'x-ibm-client-secret': ROYALMAIL_SECRET_ID,
		    'soapaction': "createShipment",
		    'content-type': "text/xml",
		    'accept': "application/xml"
		    }
		response = netw.sendRequestHeaderConfig(ROYALMAIL_URL, payload, "post", headersConfig)
		data = xmltodict.parse(response)

		try:
			shipmentNumber=data['SOAP-ENV:Envelope']['SOAP-ENV:Body']['createShipmentResponse']['completedShipmentInfo']['allCompletedShipments']['completedShipments']['shipments']['shipmentNumber']
		except:
			return data

		auth2=self.getAuth()
		auth_created2=str(auth2[2])
		printlabelxml = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:oas="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:v2="http://www.royalmailgroup.com/api/ship/V2" xmlns:v1="http://www.royalmailgroup.com/integration/core/V1">
		   <soapenv:Header>

		<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
		                   <wsse:UsernameToken>
		                      <wsse:Username>pete@cbfulfilment.co.ukAPI</wsse:Username>
		                      <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">""" + auth2[0].decode("utf-8") + """</wsse:Password>
		                      <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">""" + auth2[1].decode("utf-8") + """</wsse:Nonce>
		                      <wsu:Created>""" + auth_created2 + """</wsu:Created>
		                   </wsse:UsernameToken>
		        </wsse:Security>
		   </soapenv:Header>
		   <soapenv:Body>
		      <v2:printLabelRequest>
		                <v2:integrationHeader>
		            <v1:version>2</v1:version>
		            <v1:identification>
		               <v1:applicationId>RMG-API-G-01</v1:applicationId>
		               <v1:transactionId>00228383</v1:transactionId>
		            </v1:identification>
		         </v2:integrationHeader>
		         <v2:shipmentNumber>"""+shipmentNumber+"""</v2:shipmentNumber>
		         <v2:outputFormat>PDF</v2:outputFormat>
		         <v2:localisedAddress>
		            <v2:recipientContact>
		               <v2:name>"""+paramlist["destination"]["name"]+"""</v2:name>
		               <v2:complementaryName></v2:complementaryName>
		            </v2:recipientContact>
		            <v2:recipientAddress>
		           	<addressLine1>"""+paramlist["destination"]["line1"]+"""</addressLine1>
		               <addressLine2>"""+paramlist["destination"]["line2"]+"""</addressLine2>
		               <postTown>ddd</postTown>
		               <postcode>"""+paramlist["destination"]["zipcode"]+"""</postcode>
		            </v2:recipientAddress>
		         </v2:localisedAddress>
		      </v2:printLabelRequest>
		   </soapenv:Body>
		</soapenv:Envelope>
		"""
		headersConfig2 = {
		    'x-ibm-client-id': ROYALMAIL_CLIENT_ID,
		    'x-ibm-client-secret': ROYALMAIL_SECRET_ID,
		    'soapaction': "printLabel",
		    'content-type': "text/xml",
		    'accept': "application/xml"
		}
		responsePrint = netw.sendRequestHeaderConfig(ROYALMAIL_URL, printlabelxml, "post", headersConfig2)
		dataresult = xmltodict.parse(responsePrint)

		c = boto.connect_s3(os.environ["AWS_S3_KEY1"], os.environ["AWS_S3_KEY2"])
		bucket = c.get_bucket("srbstickers", validate=False)
		name_file = str(time.time()) + ".pdf"
		k = Key(bucket)
		k.key = name_file
		k.contentType="application/pdf"
		k.ContentDisposition="inline"
		# k.set_contents_from_string(data['soapenv:Envelope']['soapenv:Body']['msg:getReturnLabelResponse']['msg:ReturnLabelInfo']['msg:ReturnLabel_PDF'].decode('base64'))
		try:
			img_data=dataresult['SOAP-ENV:Envelope']['SOAP-ENV:Body']['printLabelResponse']['label']
		except:
			return responsePrint

		k.set_contents_from_string(base64.b64decode(img_data.encode('ascii')))	
		
		link_pdf = "https://s3-us-west-2.amazonaws.com/srbstickers/" + name_file


		final_response = {
			"origin": paramlist["origin"],
			"destination": paramlist["destination"],
			"parcel": paramlist["parcel"],
			"shipment_id": shipmentNumber,
			"label_url": link_pdf
		}
		

		return final_response