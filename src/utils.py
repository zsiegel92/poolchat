from werkzeug.routing import BaseConverter

class KwargConverter(BaseConverter):

	def to_python(self, value):
		return int(value.split('=')[1])

	def to_url(self, values):
		return '='.join(BaseConverter.to_url(value)
						for value in values)
