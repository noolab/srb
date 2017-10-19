# -*- coding: utf-8 -*-
from ServiceManager import ServiceManager
import datetime
import sys
# from BuiltInService 
import re 
import json


# from flask import Flask
# from flask import request

# app = Flask(__name__)

myservice = ServiceManager()

# test dhl dropoff service
# paramdhl = {}
# paramdhl["pickup_date"] = "2017-05-26"
# paramdhl["ready_by_time"] = "10:20"
# paramdhl["close_time"] = "14:20"
# myservice.call_service("dhl","pickup", paramdhl)

print ("\n")
# test parcel pickup service
# paramparcel = {}
# paramparcel['from'] = "France"
# paramparcel['to'] = "Cambodia"
# myservice.call_service("parcel", "pickup", paramparcel)


#========================= API GETWAY ================================
# @app.route("/<company>/<service>", methods = ["POST"])
def lamda_function(event, context):
	# paramlist = request.get_json(silent=True)
	# company=event["stage"]
	# company=re.sub(r'[^\w+]','',str(company))
	# service=event["resource_path"]
	# service=re.sub(r'[^\w+]','',str(service))
	content=event["resource_path"]
	resource=content.split("/")
	company=resource[1]
	if len(resource)==3:
		service=resource[2]
	elif len(resource)==4:
		service=resource[2]+resource[3]
	else:
		service=""
	dataparam = re.sub(r'(\bnull\b(?=[^"]*(?:"[^"]*\"[^"]*)*$))|(\bnil\b(?=[^"]*(?:"[^"]*\"[^"]*)*$))',"\"\"",str(event["body"]),flags=re.I)

	# dataparam  = re.sub(r'\bnil\b|\bnull\b',"",str(dataparam),flags=re.I)
	dataparam  = re.sub(r'\"null\"|\"nil\"',"\"\"",str(dataparam),flags=re.I)
	dataparam = re.sub(r"\\'","'",str(dataparam))
	dataparam = re.sub(r"[^\x00-\x7F]+","",str(dataparam))
	paramlist=json.loads(dataparam)
	# paramlist=json.loads(event["body"])
	if company!="" and service=="":
		service="root"
	elif "tracking" in service:
		service=resource[2]
		paramlist=event["id"] #resource[3]
	elif "dropoff" in service:
		service = resource[2]
	return myservice.call_service(company, service, paramlist)
if __name__=="__main__":
	app.run()

#============ README ==========
# """
# 	Please use postman or other api testing tool to test with the following information
# 	1. URL: http://localhost:5000/company/service (ex. http://localhost:5000/dhl/pickup, http://localhost:5000/parcel/dropoff)
# 	2. requestType: post
# 	3A. request object format for dhl:
# 		{
# 			"pickup_date": "2017-05-26",
# 			"ready_by_time":"12:20",
# 			"close_time":"16:20"
# 		}

# 	3B. request object format for parcel: 
# 		{
# 			"from": "Australia",
# 			"to":"France"
# 		}
	
# """