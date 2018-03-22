#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3

import plistlib
from utils import *

class BuildTool(object):
	def __init__(self):
		global args
		args = get_args()
		pass

	def execute(self):
		print("BuildTool excute >")
		pass

	def make_flist(self):
		# print(args)
		files = get_all_files(args.path, None, ("flist"))
		# print ("files=\n" + '\r\n'.join(files))
		# if args.poolSize > 1:
		# 	pool = ThreadPool(args.poolSize)
		# 	return_data = pool.map(self.convert_to_etc1, files)
		# 	pool.close()
		# 	pool.join()
		# else:
		# 	for file in files:
		# 		data = self.convert_to_etc1(file)
		# 		return_data.append(data)
		# 		pass
		# print ("files=\n" + '\r\n'.join(files))
		pass

	def make_plist(self,d):
		if d == None:
			return False
		plist_string = plistlib.writePlistToString(d)
		
		pass