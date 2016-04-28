from utils import *
from utils.xmlparser.xmlparser import XMLParser

class Polarion_Name_To_ID(XMLParser):

    def name_to_id(self, polarion_txt):
        testcases = self.root.getElementsByTagName("testcase")
        if testcases.length == 0:
            logger.info("No test case found in %s" % self.xml_file)
        else:
            for testcase in testcases:
                classname = testcase.getAttribute("classname")
                # name = testcase.getAttribute("name")
                case_id = re.findall(r"(?<=_ID).*?(?=_)", classname, re.I)[0]
                polarion_case_id = "RHEL6-" + case_id
                testcase.setAttribute("name", polarion_case_id)
                # self.write_file(polarion_txt, polarion_case_id + "=" + polarion_case_id)
                self.write_xml()
            logger.info("Succeeded to convert name to id in %s" % self.xml_file)

    def write_file(self, mfile, content):
        fileHandle = open(mfile, 'a')
        fileHandle.write(content)
        fileHandle.close()

if __name__ == "__main__":
    builds_xml = sys.argv[1]
    polarion_txt = sys.argv[2]
    polarion_name_to_id = Polarion_Name_To_ID(builds_xml)
    polarion_name_to_id.name_to_id(polarion_txt)
