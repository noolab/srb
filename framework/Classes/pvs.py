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

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
#from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pprint import pprint  #json read
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import datetime
from reportlab.graphics.barcode import code39
from reportlab.graphics.barcode import code93
from reportlab.graphics.barcode import code128
import textwrap

class pvs(Service):

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
		result = {
		    "available": True,
		    "response_time": 2.438041210174560,
		    "timeout": False,
		    "limit": 30000
		}
		return result
	
	def label(self,paramlist):
		name_file = str(time.time()) + ".pdf"
		pathToFile='/tmp/'+name_file
		c = canvas.Canvas(pathToFile)
		c.setFont('Helvetica', 15)
		c.setLineWidth(1)


		c.drawString(30,800, "Sender / Mittente")
		c.drawString(35,780, "MARIO ROSSI")
		c.drawString(24,760, "Via Garibaldi 31 / a")
		c.drawString(60,740, "43122")
		c.drawString(70,720, "PR")
		c.drawString(70,700, "Italy")

		c.rect(240,790,290,30, stroke=1, fill=0)

		c.setFillColorRGB(1,0,0)
		c.setFont('Helvetica', 8)
		c.drawString(250,800, "NOTA CORRIERE: NON SOVRAPPORRE ETICHETTE ALLA PRESENTE!")


		c.setFont('Helvetica', 15)
		c.setFillColorRGB(0,0,0)
		c.drawString(200,680, "SPEDIRE A")
		c.drawString(300,640, "LINEA BELLEZZA S.P.A.")
		c.drawString(280,620, "c/o PVS SERVICES ITALIA S.R.L.")
		c.drawString(290,600, "c/o Mag. La Giovane S.c.p.A.")
		c.drawString(340,580, "Magazzino 3")
		c.drawString(310,560, "Via Dell'Artigianto 2/a")
		c.drawString(350,540, "43122")
		c.drawString(350,520, "Parma")
		c.drawString(360,500, "Italy")
		c.setFont('Helvetica', 10)
		c.drawString(220,460, "POTO ASSEGNATO: Codice pagatore PVS ITA n. xxxxxxxxxx")

		c.setFont('Helvetica', 10)
		c.drawString(40,530, "Codice Pre-Bolla Mag. PVS ITA")
		c.drawString(45,500, "xxxxxxxxxxxxxxxxx")



		c.line(600,450,0,450)


		#per prenotare
		c.rect(10,320,580,55, stroke=1, fill=0)
		c.line(300,230,300,375)

		#nota
		c.rect(10,275,580,45, stroke=1, fill=0)

		#il costo
		c.rect(10,230,580,45, stroke=1, fill=0)

		#per
		c.rect(10,170,580,60, stroke=1, fill=0)


		c.line(150,30,150,170)


		#telefono
		c.rect(10,80,580,90, stroke=1, fill=0)

		#E-mail
		c.rect(10,30,580,50, stroke=1, fill=0)

		c.drawString(10,430, "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum sit amet arcu ornare, scelerisque ligula nec, tempus ipsum.")
		c.drawString(10,420, "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum sit amet arcu ornare, scelerisque ligula nec, tempus ipsum.")
		c.drawString(10,410, "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum sit amet arcu ornare, scelerisque ligula nec, tempus ipsum.")
		c.drawString(10,400, "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum sit amet arcu ornare, scelerisque ligula nec, tempus ipsum.")
		c.drawString(10,390, "Lorem ipsum dolor sit amet, consectetur adipiscing elit. ")
		c.drawString(15,360, "Per prenotare il ritiro del tuo pacco, contatta il corriere")
		c.drawString(13,350, "Lorem ipsum dolor sit amet, consectetur adipiscing elit sul sul.")
		c.drawString(18,340, "sito: : www.gls-italy.com alla voce SERVIZI PER L")
		c.drawString(20,330, "DESTINTARI - TROVA SEDE")
		c.drawString(400,345, "Corriere Utilizzabile")
		c.drawString(13,300, "nota: il giorno seguente ricontattare per ricevere n.")
		c.drawString(17,290, "spedizione. Tracciabilit sul sito:www.GLS..")
		c.drawString(17,260, "ll costo ella spedizione del reso e a carico di:")
		c.setFont('Helvetica-Bold', 10)
		c.drawString(430,295, "GLS")
		c.setFont('Helvetica', 10)
		c.drawString(400,260, "LINEA BELLEZZA S.P.A.")
		c.drawString(130,200, "Per maggiori informazioni contattare il ns. Customer Service:")
		c.setFont('Helvetica-Bold', 10)
		c.drawString(45,120, "Telefono:")
		c.drawString(280,120, "800-999-999")
		c.drawString(45,50, "E-mail:")
		c.drawString(250,50, "customerservice@lineabellezza.com")

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
			"origin": paramlist["origin"],
			"destination": paramlist["destination"],
			"parcel": paramlist["parcel"],
			"shipment_id": "transport_return_number",
			"label_url": link_pdf
		}
		return data

