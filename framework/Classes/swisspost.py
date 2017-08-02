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
from reportlab.lib.utils import ImageReader
# from olefile import *
# from PIL import ImageDraw
# from PIL import ImageDraw2
# from PIL import Image

class swisspost(Service):

	def root(self,paramlist):
		return {}

	def label(self,paramlist):
		
		data = {
	      "return_id" : "4444" ,
	      "origin": {"first_name": "Walter",
	               "last_name": "Wechlin" ,
	               "street_number": "25",
	               "line1": "avenue du temple",
	               "zipcode": "10012",
	               "city": "lausanne",
	               "country_code": "CH"
	               },
	       "destination":{"company": "WITHINGS"}
	    }

		return_id = data['return_id']
		firstName = data['origin']['first_name']
		lastName = data['origin']['last_name']
		streetNumber = data['origin']['street_number']
		line1 = data['origin']['line1']
		zipCode = data['origin']['zipcode']
		city = data['origin']['city']
		countryCode = data['origin']['country_code']
		company = data['destination']['company']

		returnIdCondition = return_id.zfill(8)
		name_file = str(time.time()) + ".pdf"
		pathToFile='/tmp/'+name_file
		c = canvas.Canvas(pathToFile)
		c.setFont('Helvetica-Bold', 20)
		c.setLineWidth(1)
		c.rect(8,520,450,315, stroke=1, fill=0)


		c.setFont('Helvetica', 12)
		c.rotate(90)
		c.drawString(540,-47, firstName + " " + lastName)
		c.drawString(540,-62, streetNumber + " " + line1)
		c.drawString(540,-77, zipCode + " " + city )
		c.drawString(540,-92, countryCode )
		# GASbarcode = 'GASbarcode.png'
		GASbarcode = ImageReader('https://s3.eu-central-1.amazonaws.com/shoprunbackframework/images/GAS-barcode.png')
		try:
			c.drawImage(GASbarcode,687,-320, width=86, height=50)
		except:
			return {'Imaging Library not available, unable to import bitmaps only jpegs..'}

		c.rotate(-90)
		c.setFont('Helvetica-Bold', 14)
		c.drawString(160,596, company)
		c.drawString(160,579,'c/o Alois Scherrer AG')
		c.drawString(160,562,'Nebengrabenstrasse 16')
		c.drawString(160,545,'9430 St. Margrethen')


		c.setFont('Helvetica', 12)
		# SwissPost = 'Swiss_Post.png'
		SwissPost = ImageReader('https://s3.eu-central-1.amazonaws.com/shoprunbackframework/images/Swiss_Post.png')
		c.drawImage(SwissPost,115,770, width=105, height=27)

		c.setFont('Helvetica', 18)
		c.drawString(32,680,"99.60.121419."+returnIdCondition)

		barcode = code128.Code128("9960121419"+returnIdCondition ,barWidth=0.5*mm,barHeight=25*mm)
		barcode.drawOn(c,15,700)

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