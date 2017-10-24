import sys
sys.path.append('./Classes')
from dhl import dhl
from relaiscolis import relaiscolis
from parcel import parcel
from bpostEasyPlus import bposteasyplus
from couriier import couriier
from royalmail import royalmail
from hermes import hermes
from envialia import envialia
from pvs import pvs
from swisspost import swisspost
from ups import ups
from colissimo import colissimo
from gophr import gophr
from postnord import postnord

class CheckStatus(object):

	def get_all_status(self,company,objfunction,paramlabel,parampickup,paramdropoff):
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
