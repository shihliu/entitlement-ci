#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pycurl
import StringIO

# checkurl = "https://virtlab-ent.englab.nay.redhat.com"
# b = StringIO.StringIO()
#   
# c = pycurl.Curl()
# c.setopt(pycurl.URL, checkurl)
# c.setopt(pycurl.HTTPHEADER, ["Accept:"])
# c.setopt(pycurl.WRITEFUNCTION, b.write)
# c.setopt(pycurl.FOLLOWLOCATION, 1)
# c.setopt(pycurl.MAXREDIRS, 5)
# c.setopt(pycurl.SSL_VERIFYPEER, False)
# c.perform()
#   
# print b.getvalue()
# print c.getinfo(c.HTTP_CODE)
# b.close()
# c.close()
# 
# fp = StringIO.StringIO()
# #  
# c = pycurl.Curl()
# c.setopt(pycurl.WRITEFUNCTION, fp.write)
# c.setopt(pycurl.FOLLOWLOCATION, 1)
# c.setopt(pycurl.MAXREDIRS, 5)
# c.setopt(pycurl.CONNECTTIMEOUT, 60)
# c.setopt(pycurl.TIMEOUT, 300)
# c.setopt(pycurl.SSL_VERIFYPEER, False)
# c.setopt(c.POST, 1)
#   
# # https://virtlab-ent.englab.nay.redhat.com/accounts/login/
#   
# c.setopt(c.URL, "https://virtlab-ent.englab.nay.redhat.com/job/uploadxml/")
# # 设置post请求，           上传文件的字段名               上传的文件
# c.setopt(c.HTTPPOST, [("id_xml_file", (c.FORM_FILE, "/root/Desktop/virt-lab.xml"))])
# c.perform()  # 执行上述访问网址的操作
# print fp.getvalue()
# print c.getinfo(c.HTTP_CODE)
# c.close()  # Curl对象无操作时，也会自动执行close操作
# print "the python shell over!"
