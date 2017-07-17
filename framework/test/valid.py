import json
import re


def validateInput():
	paramlist={
	  "name":"hello",
	  "phone":"09999",
	  "company":"Optional "
	}
	# with open("model_json.json") as data_file:
	# 	json_model = json.load(data_file)

	json_model=[
		{
			"name":"name",
			"status":"required"
		},
		{
			"name":"phone",
			"status":"required"
		},
		{
			"name":"company",
			"status":"optional"
		}
	]
	resp=True
	for obj in json_model:
		if obj["status"]=="required":
			# print (obj["name"])
			keyName=obj["name"]
			if keyName in paramlist:
				result=paramlist[keyName]
				if result=="":
					print ("param required "+str(paramlist[keyName]))
				else:
					print ("True")
			else:
				print ("not found")



def myValid():
	json_model={
	  	"requestor": {
	    	"name": "Rikhil",
	    	"phone": "23162",
	    	"company": "Saurabh"
	  	}
	}

	json_input={
		"requestor": {
	    	"name": "Rikhil",
	    	"phone": "23162",
	    	"company": ""
	  	}
	}

	for field in json_model:
		for inp in json_input:
			if field 
# validateInput()
