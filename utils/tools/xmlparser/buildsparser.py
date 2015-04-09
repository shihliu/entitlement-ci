import os
from utils import logger
from utils import constants
from utils.tools.xmlparser.xmlparser import XMLParser

class BuildsParser(XMLParser):

    runtime_path = constants.RUNTIME_PATH
    builds_xml = os.path.join(runtime_path, "builds.xml")

    def __init__(self):
        if not self.check_path_exist(self.runtime_path):
            self.create_path(self.runtime_path)
        if not self.check_file_exist(self.builds_xml):
            self.__create_builds_xml()
#         self.xml_file = self.builds_xml
        super(BuildsParser, self).__init__(self.builds_xml)

    def get_builds(self, product_name):
        '''product_name: "sam", "rhel", '''
        product_name = product_name.lower()
        build_list = []
        product_section = self.root.getElementsByTagName("%s" % product_name)
        if product_section.length == 0:
            # if product not in xml file, then add it
            logger.info("Adding %s build version to builds.xml" % product_name)
            self.__add_product(product_name)
        else:
            # get every build in <build>XXX</build>
            for build in product_section[0].getElementsByTagName("build"):
                for node in build.childNodes:
                    if node.nodeType in (node.TEXT_NODE,):
                        build_list.append(node.data)
        logger.info("All %s builds in builds.xml : %s" % (product_name, build_list))
        return build_list
    
    def add_build(self, product_name, build_name):
        ''' '''
        product_section = self.root.getElementsByTagName("%s" % product_name.lower())[0]
        build = self.xmldom.createTextNode('%s' % build_name)
        item = self.xmldom.createElement('build')
        item.appendChild(build)
        product_section.appendChild(item)
        logger.info("Add build %s to builds.xml" % (build_name))
        self.write_xml()
    
    def reset_builds(self, product_name, build_list):
        ''' reset product builds '''
        product_section = self.root.getElementsByTagName("%s" % product_name.lower())[0]
    
        # remove all builds in product
        for build in product_section.getElementsByTagName("build"):
            product_section.removeChild(build)
    
        # add builds from build_list to builds.xml
        for item in build_list:
            build = self.xmldom.createTextNode('%s' % item)
            item = self.xmldom.createElement('build')
            item.appendChild(build)
            product_section.appendChild(item)
        self.write_xml()
    
    def __add_product(self, product_name):
        item = self.xmldom.createElement(product_name)
        self.root.appendChild(item)
        self.write_xml()

    def __create_builds_xml(self):
        data_path = constants.DATA_PATH
        self.xml_copy(data_path + "/builds.xml", self.runtime_path)

if __name__ == "__main__":
    pass
