#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  

import os,sys
from parse import *
from collections import OrderedDict

section_type = [
	"\t\t{{name = \"{name}\", code = \"{code}\", size = {size:d}}},\n",
	"\t\t{{name = \"{name}\"}},\n",
	"\t{name} = \"{value}\",\n", 
	"\t{name} = {value:d},\n", 
	"\t{name} = {value}\n", 
	]

def match_section(data):
	for sec_type,sec in enumerate(section_type):
		sec_data = parse(sec, data)
		if sec_data:
			return sec_type+1, sec_data
		pass
	return 0,None

def parse_data(data):
	pass

def read_flist(flist_path):
	if os.path.isdir(flist_path):
		flist_file = os.path.join(flist_path, 'flist')
	elif os.path.isfile(flist_path) and flist_path.endswith("flist"):
		flist_file = flist_path
	else:
		print("fail: not match flist > ", file_name)
		return
	
	try:
		f = open(flist_file)
		flist_data = OrderedDict()
		for line in f:
			sec_type, sec_data = match_section(line)
			if sec_type == 1:
				flist_data['fileInfoList'][sec_data["name"]] = {
					"code" : sec_data["code"],
					"size" : sec_data["size"]
				}
				pass
			elif sec_type == 2:
				flist_data['dirPaths'][sec_data["name"]] = sec_data["name"]
				pass
			elif sec_type == 3 or sec_type == 4 or sec_type == 5:
				if (sec_data["value"] == "{"):
					flist_data[sec_data["name"]] = OrderedDict()
					data = flist_data[sec_data["name"]]
				else:
					flist_data[sec_data["name"]] = sec_data["value"]
				pass
			else:
				pass
			pass
		return flist_data
		#print(flist_data)
	except Exception, e:
		print "[Error]: ", e
		print("fail: can't find cache_path > ", flist_file)
	finally:
		f.close()

def build_flist(flist_path, flist_data):
	if not flist_data or not flist_path:
		return False

	flist_path = os.path.join(flist_path, 'flist')
	if not os.path.exists(os.path.dirname(flist_path)):
		os.makedirs(os.path.dirname(flist_path))

	buf = "local flist = {\n" 
	if flist_data["version"]:
		buf = buf + "\tversion = \"%s\",\n" %flist_data["version"]
	buf = buf + "\tdebug = %d,\n" %flist_data["debug"]
	if flist_data["launcher"]:
		buf = buf + "\tlauncher = \"%s\",\n" %flist_data["launcher"]
	if flist_data["dirPaths"]:
		buf = buf + "\tdirPaths = {\n" 
		for path in flist_data["dirPaths"]:
			buf = buf + "\t\t{name = \"" + path + "\"},\n" 
			pass
		buf = buf + "\t},\n"
	if flist_data["fileInfoList"]:
		buf = buf + "\tfileInfoList = {\n"
		for name in flist_data["fileInfoList"]:
			buf = buf + "\t\t{name = \"%s\", code = \"%s\", size = %d},\n" %(name, flist_data["fileInfoList"][name]['code'], flist_data["fileInfoList"][name]['size'])
			pass
		buf = buf + "\t},\n"

	buf = buf + "}\n\n" 
	buf = buf + "return flist"

	with open(flist_path, 'wb+') as f:
		f.write(buf)
	return True