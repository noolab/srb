from Classes.AbstractService import Service
from Modules.data_converter import data_converter as converter
from Modules.network import networking as netw
from Modules.data_validator import Validator 
from BuiltInService import requests
from BuiltInService import xmltodict
import os
import time
import datetime
import json
import re

import mandrill
import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
class shoprunback(Service):
	
	def root(self,paramlist):
		true=True
		false = False
		data={"/": {"get": true},"type": {"get": true},"status": {"get": true},"label":{"post":false},"pickup":{"post":true},"tracking":{"get":true}}
		return data
	def type(self,paramlist):
		print("type")
		true=True
		false=False
		data={"type": "pickup","postal": false,"pickup": true,"dropoff": false,"linehaul": false}
		return data
	def status(self,paramlist):
		paramtraking =""
		paramlabel={}
		parampickup={

		}
		objfunction=["root","type"]
		instance = Validator()
		api_url_request = os.environ["API_DEVEVELOPER_URL"]
		result = instance.get_all_status("shoprunback",api_url_request,objfunction,paramlabel,parampickup,"",paramtraking,"")
		return result
	def pickup(self,userparamlist):
		all_emails =[]
		shoprunbackMails = os.environ["SHOPRUNBACK_EMAILS"]
		shoprunbackMails = shoprunbackMails.split(';')
		for em in shoprunbackMails:
			dt= {
				"email":em,
				"type":"to"
			}
			all_emails.append(dt)
			
		req_list=["destination/company","origin/first_name","origin/last_name","origin/line1","origin/zipcode","origin/city","pickup/date","pickup/slot_start_at","pickup/slot_end_at"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			reqEmpty=["origin/line2","destination/line2"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
		else:
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		full_name = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
		pickup_time_window = str(paramlist["pickup"]["slot_start_at"])+" To "+str(paramlist["pickup"]["slot_end_at"])
		# merge_vars=[{
		# 	"brand_name":paramlist["destination"]["company"],
		# 	"full_name": full_name,
		# 	"pickup_date": paramlist["pickup"]["date"],
		# 	"pickup_time_window":pickup_time_window ,
		# 	"return_address1_from": paramlist["origin"]["line1"],
		# 	"return_zip_code_from": paramlist["origin"]["zipcode"],
		# 	"return_address2_from": paramlist["origin"]["line2"],
		# 	"return_city_from": paramlist["origin"]["city"],
		# }]
		merge_vars = [
			{'name':'brand_name' , 'content':paramlist["destination"]["company"] },
			{'name':'full_name' , 'content':full_name },
			{'name':'pickup_date' , 'content': paramlist["pickup"]["date"] },
			{'name':'pickup_time_window' , 'content':pickup_time_window },
			{'name':'return_address1_from' , 'content':paramlist["origin"]["line1"] },
			{'name':'return_zip_code_from' , 'content':paramlist["origin"]["zipcode"] },
			{'name':'return_address2_from' , 'content':paramlist["origin"]["line2"] },
			{'name':'return_city_from' , 'content': paramlist["origin"]["city"] }

		]

	# def sendemail(self,paramlist):
		mandrill_client = mandrill.Mandrill(os.environ["MANDRILL_TOKEN"])
		template_name = "notification-pickup-request"
		message = { 
			'from_email': 'hello@shoprunback.eu',
			'from_name': 'ShopRunBack',
			'to': all_emails,
		# 'subject': "Testing out Mandrill",
		# 'text': 'This is a message from Mandrill',
			"headers": { "Reply-To":"hello@shoprunback.eu" },
			"merge": True,
			"merge_language": 'handlebars',
			"global_merge_vars": merge_vars
		}
		try:
			data = mandrill_client.messages.send_template(template_name, [], message)
		except:
			return data
		return paramlist

# send_mail('template-1', ["sendto@email.com"], context={'Name': "Bob Marley"})