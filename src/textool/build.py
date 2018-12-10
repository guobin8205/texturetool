#/usr/bin/python2
#coding=utf-8
#Python 3.6
import os
import plistlib
import codecs
import tempfile
import shutil
import zlib, zipfile
from utils import *
from convert import *
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
		self.no_convert_list = None
		if args.no_convert_list:
			self.no_convert_list = args.no_convert_list
			pass

	def execute(self):
		self.command = args.path
		print("BuildTool excute > %s" % self.command)
		start_time = time.time()
		try:
			self.project_path = args.input
			if self.command == "flist":
				self.make_flist()
			elif self.command == "res.flist":
				self.make_res_flist()
			elif self.command == "resource":
				if not is_texturepacker_valid():
					print("TexturePacker not found...")
					return
				self.project_path = args.output
				self.build_resource()
			elif self.command == "project":
				if not is_texturepacker_valid():
					print("TexturePacker not found...")
					return
				self.project_path = args.output
				self.build_project()
				pass
			else:
				pass
			print('total elapsed time %ds'% (time.time()-start_time))
			print("done!")
		except Exception as exc:
			print(exc)
			print("failed!")
		finally:
			pass
		
	def build_resource(self):
		if args.output == None:
			print(u"output not found!")
			return False
		if not os.path.exists(args.output):
			print(u"%s directory creating ..." % (args.output))
			copytree(args.input, args.output, args.ignore_copy_list)
			print(u"%s directory created!" % (args.output))
			pass
		else:
			print(u"%s check files!" % (args.output))
			copytree(args.input, args.output, args.ignore_copy_list)

		return_data = self.convert_resource()

		if not self.check_files():
			raise Exception("not all files converted!") 
		
		self.make_res_flist()
		pass

	def build_project(self):
		if args.output == None:
			print(u"output not found!")
			return False

		if args.input != args.output:
			if not os.path.exists(args.output):
				print(u"%s directory creating ..." % (args.output))
				copytree(args.input, args.output, args.ignore_copy_list)
				print(u"%s directory created!" % (args.output))
				pass
			else:
				print(u"%s check files!" % (args.output))
				copytree(args.input, args.output, args.ignore_copy_list)

		return_data = self.convert_resource()

		if not self.check_files():
			raise Exception("not all files converted!") 

		if return_data != None:
			self.make_plist(return_data)
		
		self.make_flist()
		pass

	def convert_resource(self):
		if args.image_option == "ETC1" or args.image_option == "PVRTC4":
			return_data = {}
			compress_data = {}
			files = get_all_files(self.project_path, (".png", ".jpg"), self.no_convert_list)
			print ("total converting %d files" % len(files))
			start_time = time.time()
			args.tempdir = tempfile.mkdtemp()
			
			if args.poolSize > 1 and len(files) > 0:
				pool = ThreadPool(args.poolSize)
				compress_data = pool.map(self.convert_to_etc1, files)
				pool.close()
				pool.join()
			else:
				for file in files:
					data = self.convert_to_etc1(file)
					compress_data.append(data)

			if os.path.isdir(args.tempdir):
				shutil.rmtree(args.tempdir)
				pass

			print('total converting time %d seconds'% (time.time()-start_time))
			for data in compress_data:
				relpath = os.path.relpath(data.get("color"), self.project_path)
				src_key = ""
				if data.get("exists_alpha"):
					src_key = relpath.replace('.pvr.ccz','.png').replace('\\','/')
				else:
					src_key = relpath.replace('.pvr.ccz','.jpg').replace('\\','/')
				src_val = relpath.replace('\\','/')
				return_data[src_key] = src_val
				pass
			# files = get_all_files(self.project_path, (".ccz"), self.no_convert_list)
			# for file in files:
			# 	relpath = os.path.relpath(file, self.project_path)
			# 	src_key = ""
			# 	if os.path.exists(file + "@alpha"):
			# 		src_key = relpath.replace('.pvr.ccz','.png').replace('\\','/')
			# 	else:
			# 		src_key = relpath.replace('.pvr.ccz','.jpg').replace('\\','/')
			# 	src_val = relpath.replace('\\','/')
			# 	return_data[src_key] = src_val
			return return_data
		
		return None 

	def convert_from_texturepacker(self, _file):
		dirname, _ = os.path.split(os.path.relpath(_file, self.project_path))
		output_dir = os.path.join(self.project_path, dirname)
		# tempdir = os.path.join(args.tempdir, dirname)
		data = convert_from_texturepacker(_file, output_dir)
		return data

	def convert_to_etc1(self, _file):
		dirname, _ = os.path.split(os.path.relpath(_file, self.project_path))
		output_dir = os.path.join(self.project_path, dirname)
		tempdir = os.path.join(args.tempdir, dirname)
		data = convert_to_etc1(_file, output_dir, tempdir, "", True, True)
		return data

	def check_files(self):
		if args.image_option == "ETC1" or args.image_option == "PVRTC4":
			files = get_all_files(self.project_path, (".png", ".jpg"), self.no_convert_list)
			if len(files) > 0:
				for file in files:
					fileName, fileSuffix = os.path.splitext(file)
					pvrpath = fileName + ".pvr.ccz"
					if os.path.exists(pvrpath):
						if get_file_modifytime(file) < get_file_modifytime(pvrpath):
							os.remove(file)
					else:
						return False
					pass
		
		return True

	def make_res_flist(self):
		zippath = os.path.join(self.project_path, "res.zip")
		if os.path.exists(zippath):
			os.remove(zippath)
		
		allfiles = get_all_files(self.project_path, None, self.ignore_list)
		is_res_res = lambda x:self.is_resource(x)
		files = list(filter(is_res_res, allfiles))
		res_files = self.get_file_datalist(files)
		res_file_list = {
			'version':args.res_version,
			'files':res_files
		}
		res_flist_data = serialize_luafile(res_file_list)
		res_flist =  os.path.join(self.project_path, "res.flist")
		resfile = codecs.open(res_flist, 'wb', 'utf-8')
		resfile.write(res_flist_data)
		resfile.close()
		print(u"res.flist %d files done!" % len(res_files))

		z = zipfile.ZipFile(zippath, mode = "w", compression = zipfile.ZIP_DEFLATED)
		z.write(res_flist, "res.flist")
		z.close()
		print(u"create res.zip done!")
		pass

	def make_flist(self):
		zippath = os.path.join(self.project_path, "flist.zip")
		if os.path.exists(zippath):
			os.remove(zippath)
			
		if os.path.exists(os.path.join(self.project_path, "res.zip")):
			os.remove(os.path.join(self.project_path, "res.zip"))

		app_flist =  os.path.join(self.project_path, "flist")
		if os.path.exists(app_flist):
			os.remove(app_flist)
		res_flist =  os.path.join(self.project_path, "res.flist")
		if os.path.exists(res_flist):
			os.remove(res_flist)
		allfiles = get_all_files(self.project_path, None, self.ignore_list)
		is_app_res = lambda x:not self.is_resource(x)
		files = list(filter(is_app_res, allfiles))
		app_files = self.get_file_datalist(files)
		app_file_list = {
			'version':args.app_version,
			'debug':0,
			'launcher':get_file_md5(os.path.join(self.project_path, "lib/launcher.lib")),
			'files':app_files
		}
		app_flist_data = serialize_luafile(app_file_list)
		appfile = codecs.open(app_flist, 'wb', 'utf-8')
		appfile.write(app_flist_data)
		appfile.close()
		print(u"flist %d files done!" % len(app_files))
		
		is_res_res = lambda x:self.is_resource(x)
		files = list(filter(is_res_res, allfiles))
		res_files = self.get_file_datalist(files)
		res_file_list = {
			'version':args.res_version,
			'files':res_files
		}
		res_flist_data = serialize_luafile(res_file_list)
		resfile = codecs.open(res_flist, 'wb', 'utf-8')
		resfile.write(res_flist_data)
		resfile.close()
		print(u"res.flist %d files done!" % len(res_files))

		z = zipfile.ZipFile(zippath, mode = "w", compression = zipfile.ZIP_DEFLATED)
		z.write(app_flist, "flist")
		z.write(res_flist, "res.flist")
		z.close()
		print(u"create flist.zip done!")
		pass

	def make_plist(self,d):
		if d == None or len(d) == 0:
			return False
		
		plist_file = os.path.join(args.output, "res.plist")
		resourse = {}
		resourse["metadata"] = { 'version':1 }
		resourse["filenames"] = d
		plist_string = plistlib.writePlist(resourse, plist_file)
		# file = open(plist_file, 'wb')
		# file.write(plist_string)
		# file.close()
		print(u"res.plist %d files done!" % len(d))
		pass

	def is_resource(self, _file):
		if self.resource_list == None or len(self.resource_list) == 0:
			return True
		if _file and self.resource_list:
			relpath = get_file_relpath(_file, self.project_path)
			for res in self.resource_list:
				if relpath.startswith(res):
					return True
		return False

	def get_file_datalist(self, files):
		data = []
		if files == None or len(files) == 0:
			return data
		pool = ThreadPool(args.poolSize)
		data = pool.map(self.single_file_data, files)
		pool.close()
		pool.join()
		return data
		
	def single_file_data(self, file):
		if os.path.isfile(file):
			return {
				'name' : get_file_relpath(file, self.project_path), 
				'code' : get_file_md5(file),
				'size' : os.path.getsize(file)
			}
		return None