from Classes.AbstractService import Service

class parcel(Service):	
	def dropoff(self, paramlist):
		print ("Dropoff from Parcel Force")
		return "This Parcel force dropoff need to be implemented"

	def pickup(self, paramlist):
		print ("Pickup from Parcel Force")
		print ("From: "+paramlist['from'])
		print ("To: "+paramlist['to'])

		return "Parcel Force pickup from "+paramlist['from']+" to "+paramlist['to']

	# more function can be implemented her ...
