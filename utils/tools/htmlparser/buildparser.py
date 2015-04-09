"""
parse all builds from HTML into a list
"""
from utils import logger
from sgmllib import SGMLParser
from utils import constants
from utils.tools.htmlparser import htmlsource

class BuildParser(SGMLParser):
	build_url = ""
	product_name = ""

	def reset(self):
		self.is_a = 0
		self.build_lists = []
		SGMLParser.reset(self)

	def start_a(self, attrs):
		self.is_a = 1

	def end_a(self):
		self.is_a = 0

	def handle_data(self, data):
		if self.is_a and self.is_build(data):
			logger.debug("Found %s " % data)
			self.build_lists.append(data)

	def parse(self, product_name): 
		self.product_name = product_name
		self.build_url = constants.get_build_tree(product_name)
		self.feed(htmlsource.get_html_source(self.build_url))
		self.close()
		return self.build_lists

	def is_build(self, data):
		if data.startswith(self.product_name):
			return 1
		else:
			return 0
		# raise NotImplementedError, "Cannot call abstract method"

# class SAMBuildParser(BuildParser):
# 	"""  """
# 	build_url = constants.SAM_BUILD_URL
# 	def is_build(self, data):
# 		if data.startswith('SAM'):
# 			return 1
# 		else:
# 			return 0
# 
# class RHELBuildParser(BuildParser):
# 	"""  """
# 	build_url = constants.RHEL_BUILD_URL
# 	def is_build(self, data):
# 		if data.startswith('RHEL'):
# 			return 1
# 		else:
# 			return 0
# 
# def build_list(product_name):
# 	parserName = "%sBuildParser" % product_name
# 	parser = globals()[parserName]()
# 	return parser.parse()
# 
# if __name__ == "__main__":
# 	logger.debug(build_list("SAM"))
# 	logger.debug(build_list("RHEL"))
