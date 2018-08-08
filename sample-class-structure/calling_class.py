from called_class import CalledClass

class CallingClass(object):
	def __calling_class_function(self, msg=""):
		print("From CALLING CLASS: " + str(msg))
		
	def run(self):
		msg = "Hello, class!"
		self.__calling_class_function(msg)
		CalledClass.called_class_function(msg)


