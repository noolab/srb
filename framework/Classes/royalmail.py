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

date = datetime.datetime.now()
curdate = re.sub(r'\s.*','',str(date))
# import requests
conn = http.client.HTTPSConnection("api.royalmail.net")
ROYALMAIL_URL= os.environ["ROYALMAIL_URL"]
ROYALMAIL_AUTH_PWD = os.environ["ROYALMAIL_AUTH_PWD"]
ROYALMAIL_USERNAME =	os.environ["ROYALMAIL_USERNAME"]
ROYALMAIL_APPID = os.environ["ROYALMAIL_APPID"]
ROYALMAIL_TRANSACTIONID = os.environ["ROYALMAIL_TRANSACTIONID"]
ROYALMAIL_CLIENT_ID = os.environ["ROYALMAIL_CLIENT_ID"]
ROYALMAIL_SECRET_ID = os.environ["ROYALMAIL_SECRET_ID"]
ROYALMAIL_URL_TRACKING = os.environ["ROYALMAIL_URL_TRACKING"]
class royalmail(Service):

	def root(self,paramlist):
		true=True
		false= False
		data={
			"/":{
				"get":true
			},
			"type":{
				"get":true
			},
			"label":{
				"post":true
			},
			"status":{
				"get":true
			},
			"tracking":{
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
		allresponseTime=[]
		paramlist=""

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

		#Call Rooot =======
		response_time_1=0
		start_1 = time.time()
		try:
			rootdata= self.root(paramlist)
		except:
			response_time_1=-1
		if response_time_1 == 0:
			response_time_1 = time.time() - start_1
		allresponseTime.append(response_time_1)

		#Cal type
		response_time_2=0
		start_2 = time.time()
		try:
			rootdata= self.type(paramlist)
		except:
			response_time_2=-1
		if response_time_2 == 0:
			response_time_1 = time.time() - start_2
		allresponseTime.append(response_time_2)

		#Cal label
		response_time_3=0
		start_3 = time.time()
		try:
			dataparam={
			  "origin": {
			    "name": "Test Type",
			    "first_name": "Ithyvan",
			    "last_name": "Schreys",
			    "phone": "0622889977",
			    "email": "eddy@shoprunback.com",
			    "company": "Company Origin",
			    "line1": "11 avenue de la habette",
			    "line2": "la habette",
			    "street_number": "212121",
			    "state": "",
			    "zipcode": "94000",
			    "country": "France",
			    "country_code": "FR",
			    "city": "CRETEIL",
			    "place_description": "At home"
			  },
			  "destination": {
			    "name": "Client Base fulfilment ltd",
			    "shipment_id": "return_id_at_srb",
			    "first_name": "Leo",
			    "last_name": "Martin",
			    "company": "Company Destination",
			    "street_number": "121212",
			    "line1": "Clientbase Fulfilment",
			    "line2": "Woodview Road",
			    "state": "IDF",
			    "zipcode": "TQ4 7SR",
			    "country": "France",
			    "country_code": "GB",
			    "phone": "07801123456",
			    "email": "tom.smith@royalmail.com",
			    "city": "PAIGNTON"
			  },
			  "parcel": {
			    "length_in_cm": 10,
			    "width_in_cm": 10,
			    "height_in_cm": 10,
			    "content": "TESTS",
			    "weight_in_grams": 1950
			  },
			  "shipment_date": curdate,
			  
			  "shipment_id": "9999"
			}
			rootdata= self.label(dataparam)
		except:
			response_time_3=-1
		if response_time_3 == 0:
			response_time_3 = time.time() - start_3
		allresponseTime.append(response_time_3)
		
		#Cal Tracking
		response_time_4=0
		start_4 = time.time()
		try:
			paramlist='FL067074022GB'
			rootdata= self.tracking(paramlist)
		except:
			response_time_4=-1
		if response_time_4 == 0:
			response_time_4 = time.time() - start_4
		allresponseTime.append(response_time_4)

		final_responseTime=min(allresponseTime)
		result = {
		    "available": available,
		    "response_time": final_responseTime,
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
		paramlist["origin"]["line1"]=""
		paramlist["origin"]["line2"]=""
		paramlist["origin"]["zipcode"]=""
		paramlist["origin"]["country_code"]=""
		paramlist["origin"]["country"]=""
		paramlist["origin"]["city"]=""
		paramlist["origin"]["state"]=""
		paramlist["destination"]={}
		paramlist["destination"]["line1"]=""
		paramlist["destination"]["line2"]=""
		paramlist["destination"]["first_name"]=""
		paramlist["destination"]["last_name"]=""
		paramlist["destination"]["street_number"]=""
		paramlist["destination"]["country"]=""
		paramlist["destination"]["email"]=""
		paramlist["parcel"]={}
		paramlist["parcel"]["weight_in_grams"]=""
		paramlist["parcel"]["length_in_cm"]=""
		paramlist["parcel"]["width_in_cm"] = ""
		paramlist["parcel"]["height_in_cm"] =""
		req_list=["destination/name","destination/phone","destination/zipcode","destination/country_code"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			# paramlist=userparamlist
			reqEmpty=["origin/street_number","origin/street_name","origin/state","origin/country"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
		else:
			# return checkparamlist["message"]
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		

		line1=str(paramlist["origin"]["street_number"]+str(paramlist["origin"]["street_name"]))
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
              <v1:dateTime>2017-07-18T08:52:03</v1:dateTime>
              <v1:version>2</v1:version>
              <v1:identification>
                 <v1:applicationId>"""+ROYALMAIL_APPID+"""</v1:applicationId>
                  <v1:transactionId>"""+ROYALMAIL_TRANSACTIONID+"""</v1:transactionId>
              </v1:identification>
           </v2:integrationHeader>
           <v2:requestedShipment>
              <v2:shipmentType>
                 <code>Return</code>
              </v2:shipmentType>
        <v2:serviceOccurrence>1</v2:serviceOccurrence>
              <v2:serviceType>
      <code>R</code>
                  </v2:serviceType>
        <v2:serviceOffering>
      <serviceOfferingCode>
         <code>TSS</code>
                  </serviceOfferingCode>
        </v2:serviceOffering>
              <v2:serviceFormat>
                 <serviceFormatCode/>
              </v2:serviceFormat>
              <v2:shippingDate>"""+curdate+"""</v2:shippingDate>
               <v2:recipientContact>
                 <v2:name>Client Base fulfilment ltd</v2:name>
                 <v2:telephoneNumber>
                    <countryCode>0044</countryCode>
                    <telephoneNumber>07801123456</telephoneNumber>
                 </v2:telephoneNumber>
                 <v2:electronicAddress>
                    <electronicAddress>tom.smith@royalmail.com</electronicAddress>
                 </v2:electronicAddress>
              </v2:recipientContact>
              <v2:recipientAddress>  
                  <addressLine1>Clientbase Fulfilment</addressLine1>
                 <addressLine2>Woodview Road</addressLine2>
                 <postTown>PAIGNTON</postTown>
                 <postcode>TQ4 7SR</postcode>
                 <country>
                    <countryCode>
                       <code>GB</code>
                    </countryCode>
                 </country>
             </v2:recipientAddress>
       <v2:items>
          <v2:item>
       <v2:numberOfItems>1</v2:numberOfItems>
       <v2:weight>
          <unitOfMeasure>
             <unitOfMeasureCode>
          <code>g</code>
             </unitOfMeasureCode>
          </unitOfMeasure>
         <value>100</value>
      </v2:weight>
           </v2:item>
        </v2:items>
        <v2:customerReference>CustSuppRef1</v2:customerReference>
              <v2:senderReference>SenderReference1</v2:senderReference>

              <v2:importerAddress>
				<addressLine1>"""+line1+"""</addressLine1>
				<addressLine2>"""+paramlist["origin"]["line2"]+"""</addressLine2>
				<stateOrProvince>
					<stateOrProvinceCode>
						<code>"""+paramlist["origin"]["state"]+"""</code>
						<name>string</name>
					</stateOrProvinceCode>
				</stateOrProvince>
				<postTown>"""+paramlist["origin"]["city"]+"""</postTown>
				<postcode>"""+paramlist["origin"]["zipcode"]+"""</postcode>
				<country>
					<countryCode>
						<code>"""+paramlist["origin"]["country_code"]+"""</code>
						<name>"""+paramlist["origin"]["country"]+"""</name>
					</countryCode>
				</country>
			</v2:importerAddress>

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
			responseErr = {
	        	"status": 500,
	        	"errors": [
	            	{
	              		"detail": str(response)
	            	}
	        	]
	        }
			raise Exception(responseErr)

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
		               <v1:applicationId>"""+ROYALMAIL_APPID+"""</v1:applicationId>
		               <v1:transactionId>"""+ROYALMAIL_TRANSACTIONID+"""</v1:transactionId>
		            </v1:identification>
		         </v2:integrationHeader>
		         <v2:shipmentNumber>"""+shipmentNumber+"""</v2:shipmentNumber>
		         <v2:outputFormat>PDF</v2:outputFormat>
		         <v2:localisedAddress>
		            <v2:recipientContact>
		               <v2:name>Client Base fulfilment ltd</v2:name>
		               <v2:complementaryName></v2:complementaryName>
		            </v2:recipientContact>
		            <v2:recipientAddress>
		           	<addressLine1>Clientbase Fulfilment</addressLine1>
		               <addressLine2>Woodview Road</addressLine2>
		               <postTown>PAIGNTON</postTown>
		               <postcode>TQ4 7SR</postcode>
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
			# return responsePrint
			responseErr = {
	        	"status": 500,
	        	"errors": [
	            	{
	              		"detail": str(responsePrint)
	            	}
	        	]
	        }
			raise Exception(responseErr)

		k.set_contents_from_string(base64.b64decode(img_data.encode('ascii')))	
		
		link_pdf = "https://s3-us-west-2.amazonaws.com/srbstickers/" + name_file


		# final_response = {
		# 	"origin": paramlist["origin"],
		# 	"destination": {
		# 	    "name": "Client Base fulfilment ltd",
		# 	    "shipment_id": "return_id_at_srb",
		# 	    "first_name": paramlist["destination"]["first_name"],
		# 	    "last_name": paramlist["destination"]["last_name"],
		# 	    "company": "Company Destination",
		# 	    "street_number": paramlist["destination"]["street_number"],
		# 	    "line1": "Clientbase Fulfilment",
		# 	    "line2": "Woodview Road",
		# 	    "state": "",
		# 	    "zipcode": "TQ4 7SR",
		# 	    "country": "",
		# 	    "country_code": "GB",
		# 	    "phone": "07801123456",
		# 	    "email": "tom.smith@royalmail.com",
		# 	    "city": "PAIGNTON"
		# 	},
		# 	"parcel": paramlist["parcel"],
		# 	"carrier_shipment_id": shipmentNumber,
		# 	"label_url": link_pdf
		# }
		

		if 'shiment_id' in paramlist:
			del paramlist['shiment_id']

		paramlist["carrier_shipment_id"]= shipmentNumber
		paramlist["label_url"] =link_pdf
		
		return paramlist



	def tracking(self,paramlist):
		print("tracking getSingleItemHistoryRequest get from xml sample")
		# auth=self.getAuth()
		# auth_pwd= auth[0].decode("utf-8")
		# auth_nonce=auth[1].decode("utf-8")
		# auth_created= auth[2]
		
		trackingNumber = str(paramlist)#'FL067074022GB'
		# return trackingNumber
		payload="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://www.royalmailgroup.com/api/track/V1" xmlns:v11="http://www.royalmailgroup.com/integration/core/V1">
		  <soapenv:Header/>
		  <soapenv:Body>
		  <v1:getSingleItemHistoryRequest>

		          <v1:integrationHeader>
		            <v11:dateTime>2014-01-06T02:49:45</v11:dateTime>
		            <v11:version>1.0</v11:version> 
		     
		            <v11:identification>
		              <v11:applicationId>"""+ROYALMAIL_APPID+"""</v11:applicationId>
		              <v11:transactionId>"""+ROYALMAIL_TRANSACTIONID+"""</v11:transactionId>
		            </v11:identification>
		          </v1:integrationHeader>
		          <v1:trackingNumber>"""+trackingNumber+"""</v1:trackingNumber>
		        </v1:getSingleItemHistoryRequest>
		  </soapenv:Body>
		  </soapenv:Envelope>"""

		headersConfig = {
			'x-ibm-client-id': ROYALMAIL_CLIENT_ID,
		   	'x-ibm-client-secret': ROYALMAIL_SECRET_ID,
		   	'soapaction': "urn:getSingleItemHistory",
		   	'content-type': "text/xml",
		   	'accept': "application/xml"
		}
		print("=====================")
		print (payload)
		#response = netw.sendRequestHeaderConfig(ROYALMAIL_URL, payload, "post", headersConfig)
		try:
			response=requests.post(ROYALMAIL_URL_TRACKING, data=payload, headers=headersConfig).text
			data = xmltodict.parse(response)
		except:
			return response

		# return payload
		try:
			allres = data["soapenv:Envelope"]["soapenv:Body"]["NS1:getSingleItemHistoryResponse"]["NS1:trackDetail"]
		except:
			return response

		final_data=[]
		dt ={
			"status":"",
			"steps": []
		}

		for index,l in enumerate(allres):
			trackDate = l["NS1:trackDate"]
			location =l["NS1:trackPoint"]
			status = l["NS1:header"]
			obj={
				"status": status,
				"location": location
			}
			dt["steps"].append(obj)
			if index == len(allres)-1:
				strStatus = l["NS1:header"]
				if "processed" in strStatus.lower():
					datastatus="processed"
				elif "transit" in strStatus.lower():
					datastatus ="transit"
				elif "delivered" in strStatus.lower():
					datastatus="delivered"
				else:
					datastatus ="unknown"
				dt["status"]=datastatus
		
		final_data.append(dt)
		return final_data