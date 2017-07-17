FILE DESCRIPTION 

1. ServiceManager.py(Very important): is a factory function that will decide which class and method to call.
	The parameters are:
	- company = class_name (ex. dhl, parcel, ...)
	- service = method (ex. pickup, dropoff, ...)

2. test_by_console.py: Is not a part of the framework that use for testing output from console. 
	Please modify this file as need to test your application.

3. test_by_url.py: The same as "test_by_console.py" but the testing should be done using an api tester (eg. postman)