from Classes.AbstractService import Service
from Modules.data_converter import data_converter as converter
from Modules.network import networking as netw
import os
import xml.etree.ElementTree as ET
import time
import datetime


class couriier(Service):

	def root(self,paramlist):
		true=True
		data={
			"/": {
				"get": true
			},
			"type": {
				"get": true
			},
			"pickup/slots": {
				"get": true
			},
			"status": {
				"get": true
			}
		}
		return data

	def status(self,paramlist):
		start = time.time()
		available = True
		response_time = 0

		try:
			headersConfig = {'apikey': '8411eecbb657112d7ff930080adb8d73'}
			response = netw.sendRequest(urlreq, "", "get", headersConfig,"")
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

	def slots(self ,paramlist):
		headers = {'apikey': '8411eecbb657112d7ff930080adb8d73'}
		# today = datetime.date.today()
		# url="https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=" + (today + relativedelta(days=+1)).strftime('%Y-%m-%d') + "&dateTo=" + (today + relativedelta(days=+8)).strftime('%Y-%m-%d')
		date = datetime.datetime.now()
		tmr = date + datetime.timedelta(days=1)
		eightDay = date + datetime.timedelta(days=8)
		url="https://dropit.soixanteseize-lab.com/ecommerce/shifts?dateFrom=" + (tmr).strftime('%Y-%m-%d') + "&dateTo=" + (eightDay).strftime('%Y-%m-%d')
		response = netw.sendRequestHeaderConfig(url, "", "get", headers)
		return response.text