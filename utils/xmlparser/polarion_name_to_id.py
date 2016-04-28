from utils import *
from utils.xmlparser.xmlparser import XMLParser

class Polarion_Name_To_ID(XMLParser):

    def name_to_id(self):
        testcases = self.root.getElementsByTagName("testcase")
        if testcases.length == 0:
            logger.info("No test case found in %s" % self.builds_xml)
        else:
            for testcase in testcases:
                classname = testcase.getAttribute("classname")
                # name = testcase.getAttribute("name")
                case_id = re.findall(r"(?<=_)ID.*?(?=_)", classname, re.I)[0]
                testcase.setAttribute("name", "RHEL6-" + case_id)
                self.write_xml()
            logger.info("Succeeded to convert name to id in %s" % self.builds_xml)

if __name__ == "__main__":
    builds_xml = sys.argv[1]
    polarion_name_to_id = Polarion_Name_To_ID(builds_xml)
    polarion_name_to_id.name_to_id()
