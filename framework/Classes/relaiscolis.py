from Classes.AbstractService import Service
from Modules.data_converter import data_converter as converter
from Modules.network import networking as netw
import os
import os.path
from BuiltInService import xmltodict
import xml.etree.ElementTree as ET
import base64
import boto
from Modules.data_validator import Validator 

from boto.s3.key import Key
from boto.s3.connection import S3Connection
import time
import datetime
from random import randint
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

RELAISCOLIS_URL= os.environ["RELAISCOLIS_URL"]
RELAISCOLIS_USERNAME = os.environ["RELAISCOLIS_USERNAME"]
RELAISCOLIS_PWD = os.environ["RELAISCOLIS_PWD"]
RELAISCOLIS_URL_STATUS_DROPOFF = os.environ["RELAISCOLIS_URL_STATUS_DROPOFF"]
class relaiscolis(Service):

	def root(self,paramlist):
		true = True 
		false = False 
		result={
			"/": {
	        	"get": true
	      	},
	      	"/type": {
	       		"get": true
	      	},
	      	"/dropoffpoints": {
	        	"get": true
	      	},
	      	"/reserve_dropoff_slots": {
	        	"get": false
	     	 },
	      	"/status": {
	        	"get": true
	      	},
	      	"/label": {
	        	"get": true
	      	}
		}
		return result

	def status(self,paramlist):
		lat = '48.8640556'
		lng = '2.3478669'
		# CREATE URI
		uri = RELAISCOLIS_URL_STATUS_DROPOFF + lng + ":" + lat + "&dist=30000&nb=5&ie=UTF-8&charset=UTF-8&authKey=JSBS20140827164219887761188235&lg=eng"
		start = time.time()
		available = True
		response_time = 0
		# CALL
		try:
			# response = requests.get(uri)
			response = netw.sendRequestHeaderConfig(uri,'','get','')
		except:
			available = False
			response_time = -1

		if response_time == 0:
	  		response_time = time.time() - start

		timeout = False
		if response_time > 30:
	  		timeout = True

		result={
	  		"available": available,
	  		"response_time": response_time,
	  		"timeout": timeout,
	  		"limit": 30000
	  	}
		return result

	def dropoffpoints(self,paramlist):
		# GET LAT + LNG
		lng = paramlist["longitude"]
		lat = paramlist["latitude"]
		# CREATE URI
		uri = RELAISCOLIS_URL_STATUS_DROPOFF + lng + ":" + lat + "&dist=30000&nb=5&ie=UTF-8&charset=UTF-8&authKey=JSBS20140827164219887761188235&lg=eng"
			# CALL

		# response = requests.get(uri)
		response = netw.sendRequestHeaderConfig(uri,'','get','')
		data = xmltodict.parse(response.text)

		relay_list = []

		for relay in data["response"]["poiList"]["item"]:
			sub_tab = []
			for x in relay["poi"]["datasheet"]["descList"]["desc"]:
					if int(x["idx"]) >= 6 and int(x["idx"]) <= 19:
						sub_tab.append(x)
			relay_list.append({
		      	'distance': relay["dist"],
		     	'name': relay["poi"]["name"],
		      	'id': relay["poi"]["id"],
		      	'longitude': relay["poi"]["location"]["coords"]["lon"],
		      	'latitude': relay["poi"]["location"]["coords"]["lat"],
		      	'city': relay["poi"]["location"]["city"],
		      	'line1': relay["poi"]["location"]["formattedAddressLine"],
		      	'zipcode': relay["poi"]["location"]["postalCode"],
		      	'country': relay["poi"]["location"]["countryLabel"],
		      	'opening': {
		        	'monday': { 'am': sub_tab[0]["value"], 'pm': sub_tab[1]["value"]},
		        	'tuesday': { 'am': sub_tab[2]["value"], 'pm': sub_tab[3]["value"]},
		        	'wednesday': { 'am': sub_tab[4]["value"], 'pm': sub_tab[5]["value"]},
		        	'thursday': { 'am': sub_tab[6]["value"], 'pm': sub_tab[7]["value"]},
		        	'friday': { 'am': sub_tab[8]["value"], 'pm': sub_tab[9]["value"]},
		        	'saturday': { 'am': sub_tab[10]["value"], 'pm': sub_tab[11]["value"]},
		        	'sunday': { 'am': sub_tab[12]["value"], 'pm': sub_tab[13]["value"]}
		        }
		    })
		return relay_list

	def type(self,paramlist):
		true=True
		false=False
		data={
	  		"type": "dropoff",
	  		"postal": false,
	  		"pickup": false,
	  		"dropoff": true,
	  		"linehaul": false
		}
		return data


	def label(self,userparamlist):

		# tree = ET.parse('Assets/relaiscolis/request/labelxml.txt')
		# root = tree.getroot()


		req_list=["origin/first_name","origin/last_name","origin/company","origin/street_number","origin/line1","origin/zipcode","origin/city","destination/shipment_id","origin/phone","dropoff_informations/dropoff_point_id","return_id"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			event=userparamlist
		else:
			return checkparamlist["message"]

		firstName = event['origin']['first_name']
		lastName = event['origin']['last_name']
		company = event['origin']['company']
		streetNumber = str(event['origin']['street_number']) + str(event["origin"]["line1"])
		zipCode = event['origin']['zipcode']
		city = event['origin']['city']
		shipment_id = event['destination']['shipment_id']
		return_id = event['return_id']
		phone = event['origin']['phone']
		dropoff_point_id = event['dropoff_informations']['dropoff_point_id']

		name=firstName+' '+lastName
		#root.find("soap:Envelope/soap:Body/EnregistrerRetours/listRetourRequest/RetourRequest/NomClient").text = name

		if(len(lastName)>=4):
			name4letters=str(lastName[0:3])
		else:
			numberzero=4-len(lastName)
			name4letters=str(lastName)
			for x in range(1, numberzero):
				name4letters=lastName+'0'
		#root.find("soap:Envelope/soap:Body/EnregistrerRetours/listRetourRequest/RetourRequest/NomClient4Lettre").text = name4letters

		numid=str(return_id)
		#root.find("soap:Envelope/soap:Body/EnregistrerRetours/listRetourRequest/RetourRequest/NumCommande").text = str(numid)
		#root.find("soap:Envelope/soap:Body/EnregistrerRetours/listRetourRequest/RetourRequest/NumClient").text = str(numid)

		#root.find("soap:Envelope/soap:Body/EnregistrerRetours/listRetourRequest/RetourRequest/CodeRelais").text = str(dropoff_point_id)

		phoneNumber = event['origin']['phone']
		#root.find("soap:Envelope/soap:Body/EnregistrerRetours/listRetourRequest/RetourRequest/Teldomicile").text = str(phoneNumber)
		#root.find("soap:Envelope/soap:Body/EnregistrerRetours/listRetourRequest/RetourRequest/TelPortable").text = str(phoneNumber)

		xml = """<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
	    <soap:Header>
	    <ServiceAuthHeader xmlns="http://www.relaiscolis.com/WSRetourV2/">
	    <UserName>"""+RELAISCOLIS_USERNAME+"""</UserName>
	    <Password>"""+RELAISCOLIS_PWD+"""</Password>
	    </ServiceAuthHeader>
	    </soap:Header>
	    <soap:Body>
	    <EnregistrerRetours xmlns="http://www.relaiscolis.com/WSRetourV2/">
	    <listRetourRequest>
	    <RetourRequest>
	    <CodeEnseigne>SL</CodeEnseigne>
	    <NumCommande>""" + numid + """</NumCommande>
	    <NumClient>""" + numid + """</NumClient>
	    <NomClient>""" + name + """</NomClient>
	    <NomClient4Lettre>""" + name4letters +  """</NomClient4Lettre>
	    <CodeRelais>""" + dropoff_point_id + """</CodeRelais>
	    <Teldomicile>""" + phone + """</Teldomicile>
	    <TelPortable>""" + phone + """</TelPortable>
	    <ReferenceEnseigne>RefReturnsPolicy</ReferenceEnseigne>
	    <TypeMateriel>00</TypeMateriel>
	    <ListPrestations></ListPrestations>
	    </RetourRequest>
	    </listRetourRequest>
	    </EnregistrerRetours>
	    </soap:Body>
	    </soap:Envelope>"""

		#xmlresult = ET.tostring(root, encoding='ascii', method='xml')
		xmlresponse = netw.sendRequest(RELAISCOLIS_URL, xml, "postcontent", "xml", "xml")
		#return str(xmlresponse.text)
		# xmlroot = ET.fromstring(xmlresponse)
		data_response = xmltodict.parse(xmlresponse.content)
		date_limite_depot = datetime.datetime.strptime(data_response['soap:Envelope']['soap:Body']['EnregistrerRetoursResponse']['EnregistrerRetoursResult']['ListRetourResponse']['RetourResponse']['RetourInfos']['DateLimite'], "%Y-%m-%dT%H:%M:%S.%f")
		transport_return_number = data_response['soap:Envelope']['soap:Body']['EnregistrerRetoursResponse']['EnregistrerRetoursResult']['ListRetourResponse']['RetourResponse']['RetourInfos']['NumRetour']
		cab_number = data_response['soap:Envelope']['soap:Body']['EnregistrerRetoursResponse']['EnregistrerRetoursResult']['ListRetourResponse']['RetourResponse']['RetourInfos']['NumCAB']

		name_file = str(time.time()) + ".pdf"
		pathToFile='/tmp/'+name_file
		c = canvas.Canvas(pathToFile)
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
		srbLogo = ImageReader('https://s3.eu-central-1.amazonaws.com/shoprunbackframework/images/srb_logo.jpg') #'Assets/relaiscolis/images/srb_logo.jpg'
		# srbLogo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Assets/relaiscolis/images/srb_logo.jpg')
		c.drawImage(srbLogo,240,705, width= 130, height= 50,mask='auto')
		#c.showPage();
		relaisColisLogo = ImageReader("https://s3.eu-central-1.amazonaws.com/shoprunbackframework/images/relais-colis_logo.jpeg") #'Assets/relaiscolis/images/relais-colis_logo.jpeg'
		c.drawImage(relaisColisLogo, 60, 705, width= 45, height= 50,mask='auto')

		c.drawString(45,680, 'EXPEDITEUR :')
		c.drawString(200,680, firstName + " " + lastName)
		c.drawString(200,665, 'Marchand : ' + company)
		c.drawString(200,650, streetNumber)
		c.drawString(200,635, zipCode + ", " + city)
		c.drawString(200,620, 'No Retour : ' + return_id)
		c.drawString(200,605, 'No Colis Retour : ' + transport_return_number)
		# GENERATION CAB
		img_data = data_response['soap:Envelope']['soap:Body']['EnregistrerRetoursResponse']['EnregistrerRetoursResult']['ListRetourResponse']['RetourResponse']['RetourInfos']['CAB']
		fh = open("Assets/relaiscolis/images/relaisColisBarcode.png", "rb")
		fh.close()

		with open("/tmp/relaisColisBarcode.png", "wb") as fh:
			# fh.write(img_data.decode('base64'))
			fh.write(base64.b64decode(img_data.encode('ascii')))

		relaisColisBarcode = '/tmp/relaisColisBarcode.png'
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
		# c.rect(30,40,530,60, stroke=1, fill=0)
		# srbLogo = 'srb_logo.jpg'

		srbLogo = ImageReader('https://s3.eu-central-1.amazonaws.com/shoprunbackframework/images/srb_logo.jpg') #'Assets/relaiscolis/images/srb_logo.jpg'
		c.rect(140,210,450,60, stroke=1, fill=0)
		c.drawImage(srbLogo, 320, 215, width= 130, height= 50,mask='auto')

		# LOGO RELAIS COLIS
		# relaisColisLogo = 'relais-colis_logo.jpeg'
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

		c = boto.connect_s3(os.environ["S3_KEY1"], os.environ["S3_KEY2"])
		b = c.get_bucket("srbstickers", validate=False)

		k = Key(b)
		k.key = name_file
		k.contentType="application/pdf"
		k.ContentDisposition="inline"
		# k.set_contents_from_string(img_data.decode('base64'))
		k.set_contents_from_filename(pathToFile)
		link_pdf="https://s3-us-west-2.amazonaws.com/srbstickers/"+name_file


		data = {
			"origin": event["origin"],
			"destination": event["destination"],
			"parcel": event["parcel"],
			"shipment_id": transport_return_number,
			"label_url": link_pdf
		}
		return data








		
	 