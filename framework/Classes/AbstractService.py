class Service:
	def listServices(self):
		raise NotImplementedError("The list all service function should have been implemented.")

	def pickup(self, paramlist):
		raise NotImplementedError("The service pickup shoud have been implemented.")

	def dropoff(self, paramlist):
		raise NotImplementedError("The service dropoff should have been implemented.")

	def label(self, paramlist):
		raise NotImplementedError("The service label should have been implemented.")