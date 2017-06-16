# -*- coding: UTF-8 -*-
import tempfile
import requests
import sys
import json
import datetime
import os
import boto
import time
from boto.s3.key import Key
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from time import mktime
from pprint import pprint  #json read
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from pysimplesoap.client import SoapClient
import xmltodict
import datetime
from zeep import Client

def getLabel(event,context):
    # TEST JSON : TO DELETE AFTER IMPLEMENTATION IN LAMBDA
    # connection_file = open('sample.json', 'r')
    # conn_string = json.load(connection_file)
    # firstName = conn_string['origin']['first_name']
    # lastName = conn_string['origin']['last_name']
    # company = conn_string['origin']['company']
    # streetNumber = conn_string['origin']['street_number']
    # zipCode = conn_string['origin']['zipcode']
    # city = conn_string['origin']['city']
    # shipment_id = conn_string['destination']['shipment_id']
    # return_id = conn_string['return_id']
    # phoneNumber = conn_string['origin']['phone']
    # dropoff_point_id = conn_string['dropoff_informations']['dropoff_point_id']

    firstName = event['origin']['first_name']
    lastName = event['origin']['last_name']
    company = event['origin']['company']
    streetNumber = event['origin']['street_number']
    zipCode = event['origin']['zipcode']
    city = event['origin']['city']
    shipment_id = event['destination']['shipment_id']
    return_id = event['return_id']
    phone = event['origin']['phone']
    dropoff_point_id = event['dropoff_informations']['dropoff_point_id']

    # REQUEST SOAP ON RELAIS COLIS API
    xml = """<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
    <ServiceAuthHeader xmlns="http://www.relaiscolis.com/WSRetourV2/">
    <UserName>wsretsl15</UserName>
    <Password>rwsl2015</Password>
    </ServiceAuthHeader>
    </soap:Header>
    <soap:Body>
    <EnregistrerRetours xmlns="http://www.relaiscolis.com/WSRetourV2/">
    <listRetourRequest>
    <RetourRequest>
    <CodeEnseigne>SL</CodeEnseigne>
    <NumCommande>""" + return_id + """</NumCommande>
    <NumClient>""" + return_id + """</NumClient>
    <NomClient>""" + firstName + " " + lastName + """</NomClient>
    <NomClient4Lettre>""" + lastName[:4] +  """</NomClient4Lettre>
    <CodeRelais>""" + dropoff_point_id + """</CodeRelais>
    <Teldomicile>""" + phoneNumber + """</Teldomicile>
    <TelPortable>""" + phoneNumber + """</TelPortable>
    <ReferenceEnseigne>RefReturnsPolicy</ReferenceEnseigne>
    <TypeMateriel>00</TypeMateriel>
    <ListPrestations></ListPrestations>
    </RetourRequest>
    </listRetourRequest>
    </EnregistrerRetours>
    </soap:Body>
    </soap:Envelope>"""

    headers = {'content-type': 'text/xml'}
    response = requests.post(url="http://www.relaiscolis.com/WSRetourSwap/WSRetourV2.asmx?WSDL",data=xml,headers=headers)
    data_response = xmltodict.parse(response.content)

    date_limite_depot = datetime.datetime.strptime(data_response['soap:Envelope']['soap:Body']['EnregistrerRetoursResponse']['EnregistrerRetoursResult']['ListRetourResponse']['RetourResponse']['RetourInfos']['DateLimite'], "%Y-%m-%dT%H:%M:%S.%f")
    transport_return_number = data_response['soap:Envelope']['soap:Body']['EnregistrerRetoursResponse']['EnregistrerRetoursResult']['ListRetourResponse']['RetourResponse']['RetourInfos']['NumRetour']
    cab_number = data_response['soap:Envelope']['soap:Body']['EnregistrerRetoursResponse']['EnregistrerRetoursResult']['ListRetourResponse']['RetourResponse']['RetourInfos']['NumCAB']


    # START PDF GENERATION
    name_file = str(time.time()) + ".pdf"
    c = canvas.Canvas(name_file)
    c.setLineWidth(.3)
    c.setFont('Helvetica', 12)
    c.drawString(70,820,'BORDEREAU A COLLER SUR LE COLIS')

    c.drawString(55,810,'En cas d usage de ruban adhesif veiller a ne pas')

    c.drawString(120,800,'depasser de l encadrer')


    c.rect(30,340,530,650, stroke=1, fill=0) # le grand rectangle Centre
    c.rect(360,770,200,100, stroke=1, fill=0 ) #petite rectangle a droite

    c.drawString(410,800,'RETOUR WEB')

    # rectangle pour l image shoprunback
    c.rect(140,700,350,60, stroke=1, fill=0)
    srbLogo = 'srb_logo.jpg'
    c.drawImage(srbLogo,240,705, width= 130, height= 50)
    #c.showPage();

    relaisColisLogo = 'relais-colis_logo.jpeg'
    c.drawImage(relaisColisLogo, 60, 705, width= 45, height= 50)

    c.drawString(45,680, 'EXPEDITEUR :')
    c.drawString(200,680, firstName + " " + lastName)
    c.drawString(200,665, 'Marchand : ' + company)
    c.drawString(200,650, streetNumber)
    c.drawString(200,635, zipCode + ", " + city)
    c.drawString(200,620, 'No Retour : ' + return_id)
    c.drawString(200,605, 'No Colis Retour : ' + transport_return_number)

    # GENERATION CAB
    img_data = data_response['soap:Envelope']['soap:Body']['EnregistrerRetoursResponse']['EnregistrerRetoursResult']['ListRetourResponse']['RetourResponse']['RetourInfos']['CAB']

    fh = open("relaisColisBarcode.png", "wb")
    fh.write(img_data.decode('base64'))
    fh.close()

    with open("relaisColisBarcode.png", "wb") as fh:
        fh.write(img_data.decode('base64'))

    relaisColisBarcode = 'relaisColisBarcode.png'
    c.drawImage(relaisColisBarcode, 120, 520, width=350, height=60)

    c.drawString(45,485,'DESTINAIRE :')
    c.drawString(200,485,'SHOPRUNBACK')
    c.drawString(200,470,'59 rue des petits champs')
    c.drawString(200,455,'75001 PARIS')

    c.drawString(45,410,'AGENCE :')
    c.drawString(200,410,'Relais Colis')
    c.drawString(200,395,'7 rue de l’Ormeteau')
    c.drawString(200,380,'ZAC de l’Orme Rond')
    c.drawString(200,365,'77170 SERVON')

    c.rect(430,340,70,60, stroke=1, fill=0 ) #petite rectangle P3
    c.drawString(460,365,'P3')

    c.line(50,320,520,320)
    c.drawString(40,318,'<')
    c.drawString(522,318,'>')

    c.drawString(70,300,'BORDEREAU A PRESENTER AU COMMERCANT ET A CONSERVER')
    c.drawString(70,280,'DATE LIMITE DE DEPOT : ' + date_limite_depot.strftime("%Y-%m-%d"))

    # rectangle pour l image shoprunback
    c.rect(140,210,450,60, stroke=1, fill=0)
    srbLogo = 'srb_logo.jpg'
    c.drawImage(srbLogo, 320, 215, width= 130, height= 50)

    # LOGO RELAIS COLIS
    relaisColisLogo = 'relais-colis_logo.jpeg'
    c.drawImage(relaisColisLogo, 60, 215, width= 45, height= 50)


    c.drawString(45,190, 'EXPEDITEUR : ')
    c.drawString(200,190, firstName + " " + lastName)
    c.drawString(200,175, 'No Colis Retour : ' + transport_return_number)

    c.drawString(45,140,'DESTINAIRE :')
    c.drawString(200,140,'SHOPRUNBACK')
    c.drawString(200,125,'95 rue des petits champs')
    c.drawString(200,110,'75001 PARIS')

    c.rect(30,40,530,60, stroke=1, fill=0)
    c.drawString(160,85,'Date remise : ' + '..../..../....')
    c.drawString(160,65,'Relais Colis No : ' + dropoff_point_id)
    c.drawString(160,45,'Cachet commercial du commercant : ' + '...............')

    c.save()

    # TODO : METTRE LE LABEL SUR AWS S3
    # TODO : METTRE LE LABEL SUR AWS S3

    # c = boto.connect_s3(os.environ["AWS_S3_KEY1"], os.environ["AWS_S3_KEY2"])
    # c = boto.connect_s3("AKIAJKZ7KCBQFGFGD2ZA", "2HM3b8GPRMQFb4B86pokgXpk6A6bESo7R3NRRw61")
    # bucket = c.get_bucket("srbstickers", validate=False)
    # k = Key(bucket)
    # k.key = name_file
    # k.contentType="application/pdf"
    # k.ContentDisposition="inline"
    # k.set_contents_from_string(c)

    # link_pdf = "https://s3-us-west-2.amazonaws.com/srbstickers/" + name_file
    # print(link_pdf)

    final_response = {
        "origin": event["origin"],
        "destination": event["destination"],
        "parcel": event["parcel"],
        "shipment_id": transport_return_number,
        "label_url": "TODO WITH S3 IMPLEMENTATION"
      }

    # TEST JSON : TO DELETE AFTER IMPLEMENTATION IN LAMBDA
    # final_response = {
    #     "origin": conn_string["origin"],
    #     "destination": conn_string["destination"],
    #     "parcel": conn_string["parcel"],
    #     "shipment_id": transport_return_number,
    #     "label_url": "TODO WITH S3 IMPLEMENTATION"
    #   }
    return final_response
