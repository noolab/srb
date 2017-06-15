import json
import requests
import time
import os

def getStatus(event, context):
  start = time.time()
  available = True
  response_time = 0

  try:
    xml = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v001="http://schema.bpost.be/services/service/postal/ExternalMailItemReturnsCSMessages/v001">
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

    headers = {'Content-Type': 'text/xml', 'Authorization': ("Basic " + os.environ["BPOST_BASIC_AUTH"]), 'SOAPAction': "http://schema.bpost.be/services/service/postal/ExternalLabelServiceCS/v001/getReturnLabel"}

    response = requests.post(os.environ["BPOST_RETURN_LABEL_URI"], data=xml, headers=headers).text
  except:
    available = False
    response_time = -1

  if response_time == 0:
    response_time = time.time() - start

  timeout = False

  if response_time > 30:
    timeout = True

  result = {
      "available": available,
      "response_time": response_time,
      "timeout": timeout,
      "limit": 30000
  }
  return result
