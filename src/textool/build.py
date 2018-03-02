#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3
import plistlib

class BuildTool(object):
	def __init__(self, args):
		self.args = args
		print(self.args)
		pass

	def execute(self):
		print("BuildTool excute >")
		pass

	def make_plist(d):
		if d == None:
			return False
		plist_string = plistlib.writePlistToString(d)
		
		pass