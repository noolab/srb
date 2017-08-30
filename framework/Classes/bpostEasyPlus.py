from Classes.AbstractService import Service
from Modules.data_converter import data_converter as converter
from Modules.network import networking as netw
import os
import xml.etree.ElementTree as ET
import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import time
from BuiltInService import xmltodict
import datetime
from Modules.data_validator import Validator 
# from lxml import etree

BPOST_EASY_PLUS_URL = os.environ["BPOST_RETURN_LABEL_URI"]
BPOST_CONTRACT_ID = os.environ["BPOST_CONTRACT_ID"] 

class bposteasyplus(Service):
	"""docstring for bposteasyplus"""
	def root(self, paramlist):
		true=True
		false=False
		data={"/": {"get": true},"/type": {"get": true},"/label": {"post": true},"/price": {"post": false},"/status": {"get": true},"tracking":{"get":false}}

		return data

	def status(self, paramlist):
		allresponseTime=[]
		paramlist=""
		start = time.time()
		available = True
		response_time = 0
		
		nsd = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/', 'v001':  'http://schema.bpost.be/services/service/postal/ExternalMailItemReturnsCSMessages/v001'}

		tree = ET.parse('Assets/bpostEasyPlus/request/xmlrequest.txt')
		# tree = etree.parse('Assets/bpostEasyPlus/request/xmlrequest.txt')
		root = tree.getroot()

		# root.find('soapenv:Body/v001:getReturnLabelRequest/v001:ContractInfo/v001:ContractID',root.nsmap).text = BPOST_CONTRACT_ID
		# root.find("soapenv:Body/getReturnLabelRequest/ContractInfo/ContractID",namespaces=nsd).text = BPOST_CONTRACT_ID
		
		# xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		xmlresult="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v001="http://schema.bpost.be/services/service/postal/ExternalMailItemReturnsCSMessages/v001">
		<soapenv:Header/>
		<soapenv:Body>
			<v001:getReturnLabelRequest>
				<v001:ContractInfo>
					<v001:ContractID>""" + os.environ["BPOST_CONTRACT_ID"] + """</v001:ContractID>
				</v001:ContractInfo>
				<v001:Addressee>
					<v001:Name>Ithyvan SCHREYS</v001:Name>
					<v001:Streetname>avenue de la habette</v001:Streetname>
					<v001:Streetnumber>11</v001:Streetnumber>
					<v001:PostalCode>94000</v001:PostalCode>
					<v001:MunicipalityName>CRETEIL</v001:MunicipalityName>
					<v001:CountryISO2Code>FR</v001:CountryISO2Code>
				</v001:Addressee>
				<v001:Sender>
					<v001:Name>Leo MARTIN</v001:Name>
					<v001:Streetname>59 rue des petits champs</v001:Streetname>
					<v001:Streetnumber>59</v001:Streetnumber>
					<v001:PostalCode>75001</v001:PostalCode>
					<v001:MunicipalityName>PARIS</v001:MunicipalityName>
					<v001:CountryISO2Code>FR</v001:CountryISO2Code>
				</v001:Sender>
				<v001:ReturnInfo>
					<v001:CustomerReference>123456789</v001:CustomerReference>
				</v001:ReturnInfo>
			</v001:getReturnLabelRequest>
		</soapenv:Body>
		</soapenv:Envelope>"""

		headersConfig = {'Content-Type': 'text/xml', 'Authorization': ("Basic " + os.environ["BPOST_BASIC_AUTH"]), 'SOAPAction': "http://schema.bpost.be/services/service/postal/ExternalLabelServiceCS/v001/getReturnLabel"}
		try:
			xmlresponse = netw.sendRequestHeaderConfig(BPOST_EASY_PLUS_URL, xmlresult, "post", headersConfig)
		except:
			available = False
			response_time = -1
		if response_time == 0:
			response_time = time.time() - start

		timeout = False

		if response_time > 30:
			timeout = True
		allresponseTime.append(response_time)

		response_time_1=0
		start_1 = time.time()
		try:
			rootdata= self.root(paramlist)
		except:
			response_time_1=-1
		if response_time_1 == 0:
			response_time_1 = time.time() - start_1
		allresponseTime.append(response_time_1)

		response_time_2=0
		start_2 = time.time()
		try:
			rootdata= self.type(paramlist)
		except:
			response_time_2=-1
		if response_time_2 == 0:
			response_time_1 = time.time() - start_2
		allresponseTime.append(response_time_2)

		final_responseTime=min(allresponseTime)

		result = {
  			"available": available,
  			"response_time": final_responseTime,
  			"timeout": timeout,
  			"limit": 30000
		}
		return result



	def label(sef,userparamlist):
		#tree = ET.parse('Assets/bpostEasyPlus/request/xmlrequest.txt')
		#root = tree.getroot()

		# root.find('soapenv:Body/v001:getReturnLabelRequest/v001:ContractInfo/v001:ContractID',root.nsmap).text = BPOST_CONTRACT_ID
		# root.find("soapenv:Body/v001:getReturnLabelRequest/v001:ContractInfo/v001:ContractID").text = BPOST_CONTRACT_ID
		
		# xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		event={}
		event["destination"] = {}
		event["origin"] = {}
		event["destination"]["line1"] = ""
		event["destination"]["line2"] = ""
		event["origin"]["line1"] = ""
		event["origin"]["line2"] = ""
		req_list=["destination/street_name","origin/street_name","destination/street_number","destination/zipcode","destination/city","destination/country_code","origin/street_number",
		"origin/name","origin/zipcode","origin/city","origin/country_code","shipment_id"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			event=userparamlist
		else:
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)
			# return checkparamlist["message"]

		# full_destination_address = event["destination"]["line1"] + " " + event["destination"]["line2"]
		# full_origin_address = event["origin"]["line1"] + " " + event["origin"]["line2"]
		xmlresult="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v001="http://schema.bpost.be/services/service/postal/ExternalMailItemReturnsCSMessages/v001">
	       <soapenv:Header/>
	       <soapenv:Body>
	          <v001:getReturnLabelRequest>
	            <v001:ContractInfo>
	              <v001:ContractID>""" + os.environ["BPOST_CONTRACT_ID"] + """</v001:ContractID>
	            </v001:ContractInfo>
	            <v001:Addressee>
	                <v001:Name>""" + event["destination"]["name"] + """</v001:Name>
	                <v001:Streetname>""" + event["destination"]["street_name"] + """</v001:Streetname>
	                <v001:Streetnumber>""" + event["destination"]["street_number"] + " " + """</v001:Streetnumber>
	                <v001:PostalCode>""" + event["destination"]["zipcode"] + """</v001:PostalCode>
	                <v001:MunicipalityName>""" + event["destination"]["city"] + """</v001:MunicipalityName>
	                <v001:CountryISO2Code>""" + event["destination"]["country_code"] + """</v001:CountryISO2Code>
	            </v001:Addressee>
	            <v001:Sender>
	              <v001:Name>""" + event["origin"]["name"] + """</v001:Name>
	              <v001:Streetname>""" + event["origin"]["street_name"] + """</v001:Streetname>
	              <v001:Streetnumber>""" + event["origin"]["street_number"] + " " + """</v001:Streetnumber>
	              <v001:PostalCode>""" + event["origin"]["zipcode"] + """</v001:PostalCode>
	              <v001:MunicipalityName>""" + event["origin"]["city"] + """</v001:MunicipalityName>
	              <v001:CountryISO2Code>""" + event["origin"]["country_code"] + """</v001:CountryISO2Code>
	            </v001:Sender>
	            <v001:ReturnInfo>
	              <v001:CustomerReference>""" + event["shipment_id"] + """</v001:CustomerReference>
	            </v001:ReturnInfo>
	          </v001:getReturnLabelRequest>
	       </soapenv:Body>
	    </soapenv:Envelope>"""

		headersConfig={'Content-Type': 'text/xml', 'Authorization': ("Basic " + os.environ["BPOST_BASIC_AUTH"]), 'SOAPAction': "http://schema.bpost.be/services/service/postal/ExternalLabelServiceCS/v001/getReturnLabel"}
		
		xmlresponse = netw.sendRequestHeaderConfig(BPOST_EASY_PLUS_URL, xmlresult, "post", headersConfig)
		data = xmltodict.parse(xmlresponse)

		c = boto.connect_s3(os.environ["AWS_S3_KEY1"], os.environ["AWS_S3_KEY2"])
		bucket = c.get_bucket("srbstickers", validate=False)
		name_file = str(time.time()) + ".pdf"
		k = Key(bucket)
		k.key = name_file
		k.contentType="application/pdf"
		k.ContentDisposition="inline"
		# k.set_contents_from_string(data['soapenv:Envelope']['soapenv:Body']['msg:getReturnLabelResponse']['msg:ReturnLabelInfo']['msg:ReturnLabel_PDF'].decode('base64'))
		img_data=data['soapenv:Envelope']['soapenv:Body']['msg:getReturnLabelResponse']['msg:ReturnLabelInfo']['msg:ReturnLabel_PDF']
		k.set_contents_from_string(base64.b64decode(img_data.encode('ascii')))	
	
		try:
			shipment_id = data['soapenv:Envelope']['soapenv:Body']['msg:getReturnLabelResponse']['msg:ReturnLabelInfo']['msg:Leg3']['msg:ItemInfo']['msg:Code']
		except:
			# return xmlresponse
			responseErr = {
				"status": 500,
				"errors": [
					{
						"detail": str(xmlresponse)
					}
				]
			}
			raise Exception(responseErr)

		link_pdf = "https://s3-us-west-2.amazonaws.com/srbstickers/" + name_file


		final_response = {
			"origin": event["origin"],
			"destination": event["destination"],
			"parcel": event["parcel"],
			"carrier_shipment_id": shipment_id,
			"label_url": link_pdf
		}

		return final_response

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

		