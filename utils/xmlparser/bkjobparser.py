from utils import *
from utils.xmlparser.xmlparser import XMLParser

class BKJobParser(XMLParser):

    beakerjobs_path = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "beaker/jobxml/"))
    runtime_path = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))

    def update_param(self, task_name, param_name, param_value):
        for taskitem in self.root.getElementsByTagName("task"):
            if taskitem.getAttribute("name") == task_name:
                for paramitem in taskitem.getElementsByTagName("param"):
                    if paramitem.getAttribute("name") == param_name:
                        paramitem.setAttribute("value", param_value)
                        self.write_xml()

    def update_task(self, task_name, new_value):
        for taskitem in self.root.getElementsByTagName("task"):
            if taskitem.getAttribute("name") == task_name:
                taskitem.setAttribute("name", new_value)
                self.write_xml()

    def update_distroRequires(self, tag_name, distro_name):
        for distroitem in self.root.getElementsByTagName("distroRequires"):
            distroitem.getElementsByTagName(tag_name)[0].setAttribute("value", distro_name)
            self.write_xml()

    def update_whiteboard(self, job_name):
        self.root.getElementsByTagName("whiteboard")[0].firstChild.replaceWholeText(job_name)
        self.write_xml()

    def add_packages(self, packages):
        for packages_section in self.root.getElementsByTagName("packages"):
            for item in packages:
                package = self.xmldom.createElement('package')
                package.setAttribute("name", item)
                packages_section.appendChild(package)
        self.write_xml()

    @classmethod
    def runtime_job_copy(self, job_xml):
        if not self.check_path_exist(self.runtime_path):
            self.create_path(self.runtime_path)
        self.xml_copy(os.path.join(self.beakerjobs_path, job_xml), self.runtime_path)
        return os.path.join(self.runtime_path, job_xml)

if __name__ == "__main__":
    pass
