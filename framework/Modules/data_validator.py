# import sys
# sys.path.insert(0, "../Classes")
# from dhl import dhl
# from relaiscolis import relaiscolis
# from parcel import parcel
# from bpostEasyPlus import bposteasyplus
# from couriier import couriier
# from royalmail import royalmail
# from hermes import hermes
# from envialia import envialia
# from pvs import pvs
# from swisspost import swisspost
# from ups import ups
# from colissimo import colissimo
# from gophr import gophr
# from postnord import postnord


import re
import json
from BuiltInService import requests
class Validator(object):
	"""
		paramter
			- self: default class parameter
			- req_list: list of required fields
			- json_object: object to be validated (send from client)
	"""
	def json_check_required_Original(self, req_list, json_obj):
		message = ""
		status = True
		for req_field in req_list:
				arr_field = req_field.split("/")
				str_arr ="json_obj"
				for i in range(len(arr_field)):
					str_arr += "[arr_field["+str(i)+"]]"
					print(str_arr)
				try:
					value = eval(str_arr)
					if str(value).strip() =="":
						message += arr_field[len(arr_field)-1]+" cannot be empty\n"
						status = False
				except Exception as e:
					message += arr_field[len(arr_field)-1]+" is required\n"
					status = False
				finally:
					pass
		return {"status":status, "message":message}	

	def json_check_required(self, req_list, json_obj):
		message = ""
		status = True
		for req_field in req_list:
				arr_field = req_field.split("/")
				str_arr ="json_obj"
				for i in range(len(arr_field)):
					str_arr += "[arr_field["+str(i)+"]]"
					print(str_arr)
				try:
					value = eval(str_arr)
					if str(value).strip() =="":
						if(len(arr_field)==1):
							message += arr_field[len(arr_field)-1]+" cannot be empty or null\n"
							status = False
						elif(len(arr_field)==2):
							message += arr_field[len(arr_field)-2]+"/"+arr_field[len(arr_field)-1]+" cannot be empty or null\n"
							status = False
				except Exception as e:
					if(len(arr_field)==1):
						message += arr_field[len(arr_field)-1]+" is required\n"
						status = False
					elif(len(arr_field)==2):
						message += arr_field[len(arr_field)-2]+"/"+arr_field[len(arr_field)-1]+" is required\n"
						status = False
				finally:
					pass
		return {"status":status, "message":message}		

	def jsonCheckEmpty(self,req_field,json_obj):
		for fil in req_field:
			arr_filname = fil.split('/')
			if (len(arr_filname))==1:
				if arr_filname[0] not in json_obj:
					json_obj[arr_filname[0]] =""
			elif (len(arr_filname))==2:
				if arr_filname[0] not in json_obj:
					json_obj[arr_filname[0]]={}
					json_obj[arr_filname[0]][arr_filname[1]] =""
				else:
					if arr_filname[1] not in json_obj[arr_filname[0]]:
						json_obj[arr_filname[0]][arr_filname[1]] =""

		return json_obj

	def json_check_line1(self,line1):
		# street_number =re.search(r'(\d+\s*(?:[A-Z](?![A-Z]))?)', str(line1)).group(1)
		street_number = re.sub(r'[^\d+]','',str(line1))
		street_name =  re.sub(r'[\d+]','',str(line1))
		data={"street_number":str(street_number),"street_name":str(street_name)}
		return data

	def getCountryName(self,countrycode):
	 	url ='https://restcountries.eu/rest/v2/alpha/'+countrycode
	 	data = requests.get(url)
	 	country = json.loads(data.content)
	 	return country["name"]

	def getLatLng(self,location):
		api_key='AIzaSyD-LxdE3GSzycdq_AQodgokDu7nlqfT5ek'
		api_url ='https://maps.googleapis.com/maps/api/geocode/json?address='+str(location)+'&key=AIzaSyD-LxdE3GSzycdq_AQodgokDu7nlqfT5ek'
		data = requests.get(api_url)
		data = json.loads(data.content)
		latlng = data["results"][0]["geometry"]["location"]
		return  latlng

	def check_status(self,company,objfunction,paramlabel,parampickup,paramdropoff):
		start = time.time()
		available = True
		allresponseTime=[]
		response_time = 0
		timeout = False
		for service in objfunction:
			selected_class = globals()[company]
			instance = selected_class()
			method = getattr(instance, service)
			try:
				if service=="label":
					data = method(paramlabel)
				elif service =="pickup":
					data =method(parampickup)
				elif service =="dropoff":
					data = method(paramdropoff)
				else:
				    data = method(param="")
				if response_time == 0:
			  		response_time = time.time() - start
			  		allresponseTime.append(response_time)

				if response_time > 30:
					timeout = True
					available = False
					response_time = -1
					result={
						"available": available,
						"response_time": response_time,
						"timeout": timeout,
						"service":service,
						"limit": 30000
					}
					return result
			except:
				available = False
				response_time = -1
				result={
			  		"available": available,
			  		"response_time": response_time,
			  		"timeout": timeout,
			  		"service":service,
			  		"limit": 30000
			  	}
				return result

		final_responseTime=max(allresponseTime)
		result={
	  		"available": available,
	  		"response_time": final_responseTime,
	  		"timeout": timeout,
	  		"limit": 30000
	  	}
		return result









"""
================================================================
Test the function 
"""
# (Sample) obejct send from client 
json_obj = {
	"date":" ",
	"student":{
		"id":"100",
		"name":"Bruce Wayne",
		"title":"Batman"
	},
	"teacher":{
		"id":"001",
		"name":"Barry Allen",
		"title":" "
	},
	"address":{
		"location":{
			"street":"A72"
		},
	}
}

# List of required fields 
req_list1 = ["date", "school", "student/id", "student/salary", "teacher/title", "address/location/street", "address/location/building"]
req_list2 = ["address", "student","aa"]

#Test Case 1
instance = Validator()
result1 = instance.json_check_required(req_list1, json_obj)
print(result1["status"]) # False = Validation is Faild, True = Validation is OK
print(result1["message"]) # Report of how many field are missing

#Test Case 2
result2 = instance.json_check_required(req_list2, json_obj)
if result2["status"]:
	print(json_obj["address"])
	print(json_obj["student"])
else:
	print(result2["message"])



# set deafult value field not required
# check conditiion again
