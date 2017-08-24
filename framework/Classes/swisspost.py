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
SWISSPOST_URL = os.environ["SWISSPOST_STATUS_URL"]
class swisspost(Service):

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
				"post":true
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
		allresponseTime=[]
		paramlist=""

		start=time.time()
		available=True
		response_time=0
		try:
			# xmlresponse=netw.sendRequest(SWISSPOST_URL,"","get","","")
			paramlist = {
		      "shipment_id" : "4444" ,
		      "origin": {"first_name": "Walter",
		               "last_name": "Wechlin" ,
		               "street_number": "25",
		               "line1": "avenue du temple",
		               "zipcode": "10012",
		               "city": "lausanne",
		               "country_code": "CH"
		               },
		       "destination":{"company": "WITHINGS"},
		       "parcel":{}
		    }
			xmlresponse= self.label(paramlist)
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


		final_responseTime=min(allresponseTime)
		result = {
		    "available": available,
		    "response_time": final_responseTime,
		    "timeout": timeout,
		    "limit": 30000
		}
		return result

	def label(self,userparamlist):
		req_list=["shipment_id","origin/first_name","origin/last_name","origin/city","origin/street_number","origin/line1","origin/zipcode","origin/country_code","destination/company",]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			data=userparamlist
		else:
			return checkparamlist["message"]
		if "street_name" not in paramlist["origin"]:
			data["origin"]["street_name"] =""
		if "street_number" not in paramlist["origin"]:
			data["origin"]["street_number"] = ""
		data_line1 = str(data["origin"]["street_number"])+str(data["origin"]["street_name"])

		shipment_id = data['shipment_id']
		firstName = data['origin']['first_name']
		lastName = data['origin']['last_name']
		streetNumber = data['origin']['street_number']
		line1 =  data_line1#data['origin']['line1']
		line1 = line1[:18]
		zipCode = data['origin']['zipcode']
		city = data['origin']['city']
		countryCode = data['origin']['country_code']
		company = data['destination']['company']

		returnIdCondition = shipment_id.zfill(8)
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
		GASbarcode = ImageReader('https://s3.eu-central-1.amazonaws.com/shoprunbackframework/images/GASbarcode.jpg')
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
		SwissPost = ImageReader('https://s3.eu-central-1.amazonaws.com/shoprunbackframework/images/Swiss_Post.jpg')
		c.drawImage(SwissPost,115,775, width=105, height=27)

		c.setFont('Helvetica', 17)
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


		data_final = {
			"origin": data["origin"],
			"destination": data["destination"],
			"parcel": data["parcel"],
			"carrier_shipment_id": "transport_return_number",
			"label_url": link_pdf
		}
		return data_final