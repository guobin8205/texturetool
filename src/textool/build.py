#!/usr/bin/python
#coding=utf-8
#Python 2.7.3
import os
import plistlib
import codecs
from utils import *
from multiprocessing.dummy import Pool as ThreadPool

class BuildTool(object):
	def __init__(self):
		global args
		args = get_args()
		# self.resouce_list = ["audio_hq", "ui/bface", "ui/face", "ui/icon"]
		self.resource_list = []
		if args.resource_list:
			self.resource_list = args.resource_list
			pass
		self.ignore_list = None
		if args.ignore_list:
			self.ignore_list = args.ignore_list
			pass

	def execute(self):
		print("BuildTool excute >")
		pass

	def make_res_flist(self):
		allfiles = get_all_files(args.path, None, self.ignore_list)
		is_res_res = lambda x:self.is_resource(x)
		files = filter(is_res_res, allfiles)
		res_files = self.get_file_datalist(files)
		res_file_list = {
			'version':args.res_version,
			'files':res_files
		}
		res_flist_data = serialize_lua(res_file_list)
		res_flist =  os.path.join(args.path, "res.flist")
		resfile = codecs.open(res_flist, 'wb', 'utf-8')
		resfile.write(res_flist_data)
		resfile.close()
		print(u"res.flist %d files done!" % len(res_files))
		pass

	def make_flist(self):
		allfiles = get_all_files(args.path, None, self.ignore_list)
		is_app_res = lambda x:not self.is_resource(x)
		files = filter(is_app_res, allfiles)
		app_files = self.get_file_datalist(files)

		app_file_list = {
			'version':args.app_version,
			'debug':0,
			'launcher':get_file_md5(os.path.join(args.path, "lib/launcher.lib")),
			'files':app_files
		}
		app_flist_data = serialize_lua(app_file_list)
		app_flist =  os.path.join(args.path, "app.flist")
		appfile = open(app_flist, 'wb')
		appfile.write(app_flist_data)
		appfile.close()
		print(u"app.flist %d files done!" % len(app_files))
		
		is_res_res = lambda x:self.is_resource(x)
		files = filter(is_res_res, allfiles)
		res_files = self.get_file_datalist(files)
		res_file_list = {
			'version':args.res_version,
			'files':res_files
		}
		res_flist_data = serialize_lua(res_file_list)
		res_flist =  os.path.join(args.path, "res.flist")
		resfile = codecs.open(res_flist, 'wb', 'utf-8')
		resfile.write(res_flist_data)
		resfile.close()
		print(u"res.flist %d files done!" % len(res_files))
		pass

	def make_plist(self,d):
		if d == None:
			return False
		plist_string = plistlib.writePlistToString(d)
		
		pass


	def is_resource(self, file):
		if file and self.resource_list:
			relpath = get_file_relpath(file, args.path)
			for res in self.resource_list:
				if relpath.startswith(res):
					return True
		return False

	def get_file_datalist(self, files):
		pool = ThreadPool(args.poolSize)
		data = pool.map(self.single_file_data, files)
		pool.close()
		pool.join()
		return data
    	pass

	def single_file_data(self, file):
		if os.path.isfile(file):
			return {
				'name' : get_file_relpath(file, args.path), 
				'code' : get_file_md5(file),
				'size' : os.path.getsize(file)
			}
		return None