import shutil, codecs
from utils import *
from xml.dom import minidom

class XMLParser(object):

    xml_file = None
    xmldom = None
    root = None
    def __init__(self, xml_file=""):
        self.xml_file = xml_file
        if self.xml_file != "":
            self.xmldom = minidom.parse(xml_file)
            self.root = self.xmldom.documentElement

    @classmethod
    def xml_copy(self, source, destination):
        shutil.copy(source, destination) 
    @classmethod
    def check_file_exist(self, file_name):
        return os.path.isfile(file_name)
    @classmethod
    def check_path_exist(self, path_name):
        return os.path.exists(path_name)
    @classmethod
    def create_path(self, path_name):
        os.makedirs(path_name)

    def write_xml(self):
        minidom.Element.writexml = fixed_writexml
        xmlfile = codecs.open(self.xml_file, 'w', 'utf-8')
        self.xmldom.writexml(xmlfile, addindent='' , newl='\n')
        xmlfile.close()

def fixed_writexml(self, writer, indent="", addindent="", newl=""):
    writer.write(indent + "<" + self.tagName)

    attrs = self._get_attributes()
    a_names = attrs.keys()
    a_names.sort()

    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        minidom._write_data(writer, attrs[a_name].value)
        writer.write("\"")
    if self.childNodes:
        if len(self.childNodes) == 1 \
          and self.childNodes[0].nodeType == minidom.Node.TEXT_NODE:
            writer.write(">")
            self.childNodes[0].writexml(writer, "", "", "")
            writer.write("</%s>%s" % (self.tagName, newl))
            return
        writer.write(">%s" % (newl))
        for node in self.childNodes:
            if node.nodeType is not minidom.Node.TEXT_NODE:
                node.writexml(writer, indent + addindent, addindent, newl)
        writer.write("%s</%s>%s" % (indent, self.tagName, newl))
    else:
        writer.write("/>%s" % (newl))

if __name__ == "__main__":
    pass
