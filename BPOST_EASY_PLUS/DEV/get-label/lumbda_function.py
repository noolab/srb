import requests
import boto
import time
from boto.s3.key import Key
import xml.etree.ElementTree as ET
import base64
import datetime
import re
import os
from random import randrange
from boto.s3.connection import S3Connection

def getLabel(event,context):

  # DESTINATION PARAMS
  if "name" not in event["destination"]:
    return "Missing parameter: [destination][name]"

  if "line1" not in event["destination"]:
    return "Missing parameter: [destination][line1]"

  full_destination_address = event["destination"]["line1"] + " " + event["destination"]["line2"]

  if "zipcode" not in event["destination"]:
    return "Missing parameter: [destination][zipcode]"

  if "city" not in event["destination"]:
    return "Missing parameter: [destination][city]"

  if "country_code" not in event["destination"]:
    return "Missing parameter: [destination][country_code]"

  # ORIGIN PARAMS

  if "name" not in event["origin"]:
    return "origin_name is missing.."

  if "line1" not in event["origin"]:
    return "Missing parameter: [origin][line1]"

  full_origin_address = event["origin"]["line1"] + " " + event["origin"]["line2"]

  if "zipcode" not in event["origin"]:
    return "Missing parameter: [origin][zipcode]"

  if "city" not in event["origin"]:
    return "Missing parameter: [origin][city]"

  if "country_code" not in event["origin"]:
    return "Missing parameter: [origin][country_code]"

  # RETURN INFORMATIONS

  if "return_id" not in event:
    return "Missing parameter: [return_id]"

  # BUILD XML
  xml="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v001="http://schema.bpost.be/services/service/postal/ExternalMailItemReturnsCSMessages/v001">
       <soapenv:Header/>
       <soapenv:Body>
          <v001:getReturnLabelRequest>
            <v001:ContractInfo>
              <v001:ContractID>""" + os.environ["BPOST_CONTRACT_ID"] + """</v001:ContractID>
            </v001:ContractInfo>
            <v001:Addressee>
                <v001:Name>""" + event["destination"]["name"] + """</v001:Name>
                <v001:Streetname>""" + full_destination_address + """</v001:Streetname>
                <v001:Streetnumber>""" + event["destination"]["Streetnumber"] + " " + """</v001:Streetnumber>
                <v001:PostalCode>""" + event["destination"]["zipcode"] + """</v001:PostalCode>
                <v001:MunicipalityName>""" + event["destination"]["city"] + """</v001:MunicipalityName>
                <v001:CountryISO2Code>""" + event["destination"]["country_code"] + """</v001:CountryISO2Code>
            </v001:Addressee>
            <v001:Sender>
              <v001:Name>""" + event["origin"]["name"] + """</v001:Name>
              <v001:Streetname>#{_return.address1_from[0..38].downcase.gsub(/[^a-z0-9\s]/i, '')}</v001:Streetname>
              <v001:Streetnumber> </v001:Streetnumber>
              <v001:PostalCode>""" + event["origin"]["zipcode"] + """</v001:PostalCode>
              <v001:MunicipalityName>""" + event["origin"]["city"] + """</v001:MunicipalityName>
              <v001:CountryISO2Code>""" + event["origin"]["country_code"] + """</v001:CountryISO2Code>
            </v001:Sender>
            <v001:ReturnInfo>
              <v001:CustomerReference>""" + event["return_id"] + """</v001:CustomerReference>
            </v001:ReturnInfo>
          </v001:getReturnLabelRequest>
       </soapenv:Body>
    </soapenv:Envelope>"""

  print xml
  headers = {'Content-Type': 'text/xml', 'Authorization': ("Basic " + os.environ["BPOST_BASIC_AUTH"]), 'SOAPAction': "http://schema.bpost.be/services/service/postal/ExternalLabelServiceCS/v001/getReturnLabel"}

  response = requests.post(os.enviro["BPOST_RETURN_LABEL_URI"], data=xml, headers=headers).text


  # c = boto.connect_s3("AKIAJKZ7KCBQFGFGD2ZA", "2HM3b8GPRMQFb4B86pokgXpk6A6bESo7R3NRRw61")
  # b = c.get_bucket("srbstickers", validate=False)
  # print b

  # print "start ET"
  # root = ET.fromstring(response)
  # data=[]
  # print root
  # for child in root.findall('LabelImage'):
  #   pdf=child.find('OutputFormat').text+'.pdf'
  #   img_data=child.find('OutputImage').text
  #   #print pdf
  #   print img_data
  #   name_file=str(time.time())+".pdf"
  #   k = Key(b)
  #   print k
  #   k.key = name_file
  #   k.contentType="application/pdf"
  #   k.ContentDisposition="inline"
  #   # k.set_contents_from_string(img_data)
  #   k.set_contents_from_string(img_data.decode('base64'))
  #   link_pdf="https://s3-us-west-2.amazonaws.com/srbstickers/"+name_file

  # #-------------
  # allroot = ET.fromstring(response)
  # shipmentId="0"
  # for getchild in allroot.findall('AirwayBillNumber'):
  #   if len(getchild)<0:
  #     shipmentId= ''
  #   else:
  #     shipmentId=getchild.text

  return response

