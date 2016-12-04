#!/usr/bin/env python
#
# libvirt-test-API is copyright 2010 Red Hat, Inc.
#
# libvirt-test-API is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version. This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranties of TITLE, NON-INFRINGEMENT,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# The GPL text is available in the file COPYING that accompanies this
# distribution and at <http://www.gnu.org/licenses>.
#
# Filename: XMLParser.py
# Summary: parse and xml document into a python dictionary
# Description: The module is a tool to parses
# and xml document into a python dictionary

import os
from xml.dom import minidom
import StringIO

class XMLParser(object):
    """Class XMLParser. It parses and xml document into a python dictionary.
       The elements of the xml documents will be python dictionary keys. For
       example, the xml document:
          <firstel>firstdata</firstel>
          <secondel>
              <subinsecond> seconddata </subinsecond>
          </secondel>
       will be parsed into the python dictionary:
         { "firstel":"firstdata" , "secondel":{"subsinsecond":"seconddata"} }
       Then the data can be retrieve as:
       out = XMLParser.XMLParser().parse(xml)
       out["firstel"] (this will be firstdata )
       out["secondel"]["subinsecond"] (this will be seconddata)

       attributes will be put into attr hash, so say the xml document is:
       <source>
         <device path = '/dev/mapper/vg_hpdl120g501-lv_home'/>
       </source>

       It will be parsed into:
       out["source"]["device"]["attr"]["path"]
       which will be set to:
         "/dev/mapper/vg_hpdl120g501-lv_home"
    """
    def __init__(self):
        pass

    def parse(self, arg):
        out = None
        if type(arg) == file:
            out = self.parsefile(arg)
        elif os.path.exists(arg):
            print "file: %s " % arg
            out = self.parsefile(arg)
        else:
            streamstr = StringIO.StringIO(arg)
            out = self.parsefile(streamstr)
        if out != None:
            return out

    def parsefile(self, filepath):
        xmldoc = minidom.parse(filepath)
        thenode = xmldoc.firstChild
        outdic = dict()
        self.parseintodict(thenode, 0, outdic)
        return outdic

    def parseintodict(self, node, level, out, rootkey = None):
        for thenode in node.childNodes:
            if thenode.nodeType == node.ELEMENT_NODE:
                key = thenode.nodeName
                value = None
                try:
                    value = thenode.childNodes[0].data
                    if value.strip() == '':
                        value = None
                except:
                    value = None
                newdict = { key:value }
                attrdic = None
                if rootkey != None:
                    self.keyfindandset(out, rootkey, thenode)
                else:
                    if thenode.attributes != None:
                        tmpattr = dict()
                        if thenode.attributes.length > 0:
                            for key in thenode.attributes.keys():
                                tmpattr.update(
                                {key:thenode.attributes.get(key).nodeValue})
                            attrdic = { "attr":tmpattr }
                    if key in out:
                        if out[key] == None:
                            out[key] = value
                            if attrdic != None:
                                out[key].update(attrdic)
                        elif type(out[key]) == list:
                            if attrdic != None:
                                newdict.update(attrdic)
                            out[key].append(newdict)
                        elif type(out[key]) == dict:
                            if attrdic != None:
                                newdict.update(attrdic)
                            out[key].update(newdict)
                        else:
                            tmp = out[key]
                            out[key] = [tmp, value]
                    else:
                        out[key] = value
                        if attrdic != None:
                            out[key].update(attrdic)
                self.parseintodict(thenode, level+1, out, key)
        return out

    def keyfindandset(self, thedict, thekey, thenode):
        # get the key/value pair from the node.
        newvalkey = thenode.nodeName
        value = None
        try:
            value = thenode.childNodes[0].data
            if value.strip() == '':
                value = None
        except:
            value = None
        newval = { newvalkey:value }
        attrdic = None
        if thenode.attributes != None:
            tmpattr = dict()
            if thenode.attributes.length > 0:
                for key in thenode.attributes.keys():
                    tmpattr.update(
                    {key:thenode.attributes.get(key).nodeValue})
                attrdic = { "attr":tmpattr }
        if attrdic != None:
            if value == None:
                newval.update({newvalkey:attrdic})
            else:
                valdic = { "value":value }
                newval.update(valdic)
                newval.update(attrdic)
        for key in thedict.keys():
            if key == thekey:
                if type(thedict[key]) == dict:
                    if newvalkey in thedict[key]:
                        if newval[newvalkey] != None:
                            tmpdic = thedict[key][newvalkey]
                            thedict[key][newvalkey] = [tmpdic]
                            thedict[key][newvalkey].append(newval)
                        else:
                            if type(thedict[key][newvalkey]) == list:
                                thedict[key][newvalkey].append(dict())
                            else:
                                tmpdic = thedict[key][newvalkey]
                                thedict[key][newvalkey] = [tmpdic]
                                thedict[key][newvalkey].append(dict())
                    else:
                        thedict[key].update(newval)
                elif type(thedict[key]) == list:
                    if newvalkey in thedict[key][-1]:
                        thedict[key].append(newval)
                    else:
                        thedict[key][-1].update(newval)
                else:
                    thedict[key] = newval
            if type(thedict[key]) == dict:
                self.keyfindandset(thedict[key], thekey, thenode)

