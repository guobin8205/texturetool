#/usr/bin/python2
#coding=utf-8
#Python 2.7.3
from __future__ import print_function

import os
import sys
import argparse
import dataparse
import flistparse
import hashlib
import json
import shutil
import zlib
import tempfile
import struct
import plistlib
import audiotranscode
import subprocess

from utils import *
from convert import *
from build import BuildTool
from textureconvert import TextureConvert
from PIL import Image
from parse import parse
from plistlib import readPlist
from collections import OrderedDict
from multiprocessing import Pool, Lock
from multiprocessing.dummy import Pool as ThreadPool

usage = """
%(prog)s build D:/project/tag/v2.0 -i D:/project/tag/v1.0 -l -if ui/item0 ui/item1
%(prog)s unpack D:/project/tag/v2.0/ui/button.plist -o D:/prj/test
%(prog)s convert D:/project/tag/v2.0/ui/button.plist -o D:/prj/test
%(prog)s convert D:/project/tag/v2.0 -o D:/prj/test -r -if ui/item0 ui/item1
"""

class TextureTool(object):
	def __init__(self):
		self.image_file = {}

	def run(self):
		self.command = args.command.lower()
		if self.command == 'build':
			return self.command_build()
		elif self.command == 'convert':
			return self.command_convert()
		elif self.command == 'unpack':
			return self.command_unpack()
		elif self.command == 'pack':
			return self.command_pack()
		elif self.command == 'test':
			return self.command_test()
		else:
			print("unkown command,> ", self.command)

	def command_build(self):
		build = BuildTool()
		return build.execute()
    	pass

	def command_test3(self):
		build = BuildTool()
		build.make_flist()
		# for file in files:
		# 	print ("file=" + file)
		# 	return
		# print ("files=\n" + '\r\n'.join(files))\
		#ffmpeg -i E:\quickv3\sanguosha\res\audio\skill\SKILL_32_1_2.mp3 -f wav - |oggenc2 -q 0 -Q - -o D:/project/SKILL_32_1_2.ogg
		pass

	def testfile3(self, file):
		print(file)
		pass

	def command_test2(self):
		print(args.path)
		files = self.getAudioFiles()
		at = audiotranscode.AudioTranscode(debug=True)
		print(at.available_encoder_formats())
		print(at.available_decoder_formats())
		for file in files:
			at.transcode(file,'D:/project/test.ogg',bitrate=128)
			return
		# print ("files=\n" + '\r\n'.join(files))\
		#ffmpeg -i E:\quickv3\sanguosha\res\audio\skill\SKILL_32_1_2.mp3 -f wav - |oggenc2 -q 0 -Q - -o D:/project/SKILL_32_1_2.ogg
		pass

	def command_test(self):
		# build = BuildTool(args.path)
		# build.execute()
		files = self.getConvertFiles()
		if args.image_option != "ETC1":
			return
		resourse = {}
		resourse["metadata"] = { 'version':1 }
		resourse["filenames"] = {}
		for file in files:
			if args.image_option == "ETC1":
				dirname, _ = os.path.split(os.path.relpath(file, args.path))
				_, filename = os.path.split(file)
				pre,_ = os.path.splitext(filename)
				src_key = os.path.join(dirname, filename).replace('\\','/')
				src_val = os.path.join(dirname, pre + ".pvr.ccz").replace('\\','/')
				resourse["filenames"][src_key] = src_val
				pass
			pass
		# print(resourse)
		plist_string = plistlib.writePlistToString(resourse)
		# print(plist_string)
		plist_file = os.path.join(args.output, "res.plist")
		print(plist_file)
		file = open(plist_file, 'wb')
		file.write(plist_string)
		file.close()
		pass

	def command_pack(self):
		if os.path.isdir(args.path):
			self.packer_dir(args.path)
		else:
			print("invalid path, not a directory > ", args.path)
		pass

	def command_unpack(self):
		if os.path.isdir(args.path):
			self.unpacker_dir(args.path)
		elif os.path.isfile(args.path):
			self.unpacker(args.path)
		else:
			print("invalid path, not a directory > ", args.path)

	def initArgs(self):
		if os.path.isdir(args.path):
			self.res_path = os.path.join(args.path, 'res')
			self.res_build_path = os.path.join(args.path, 'res_ios')
			if not os.path.isdir(self.res_path):
				print("invalid path, can't find res path > ", args.path)
				return False
		else:
			print("invalid path, not a directory > ", args.path)
			return False
		pass

	def getAudioFiles(self):
		return get_all_files(args.path, (".mp3"))

	def getTextureFiles(self):
		return get_all_files(args.path, (".png", ".jpg"))

	def getConvertFiles(self):
		tempfiles = []
		print("path > ", args.path)
		if os.path.isdir(args.path):
			for root, _, files in os.walk(args.path):
				for name in files:
					_, fileSuffix = os.path.splitext(name)
					if fileSuffix == '.png' or fileSuffix == '.jpg':
						fullPath = args.path + root[len(args.path):]
						fullName = fullPath + '/' + name
						if not os.path.exists(fullName):
							continue

						tempfiles.append(fullName)
				else:
					continue
				break
		elif os.path.exists(args.path):
			tempfiles.append(args.path)
			pass

		print ("total converting %d files" % len(tempfiles))
		# print ("files=\n" + '\r\n'.join(tempfiles))
		return tempfiles

	def command_convert(self):
		if args.image_option != "ETC1":
			return

		start_time = time.time()
		files = self.getTextureFiles()
		if args.image_option == "ETC1":
			args.tempdir = tempfile.mkdtemp()
			return_data = []
			if args.poolSize > 1:
				pool = ThreadPool(args.poolSize)
				return_data = pool.map(self.convert_to_etc1, files)
				pool.close()
				pool.join()
			else:
				for file in files:
					data = self.convert_to_etc1(file)
					return_data.append(data)
			
			if os.path.isdir(args.tempdir):
				# shutil.rmtree(args.tempdir)
				# print(args.tempdir)
				pass
			print('total elapsed time %ds'% (time.time()-start_time))
		pass

	def convert_to_etc1(self, _file):
		dirname, _ = os.path.split(os.path.relpath(_file, args.path))
		output_dir = os.path.join(args.output, dirname)
		tempdir = os.path.join(args.tempdir, dirname)
		return convert_to_etc1(_file, output_dir, tempdir)
	
	def initbuildArgs(self):
		if os.path.isdir(args.path):
			self.res_path = os.path.join(args.path, 'res')
			self.res_build_path = os.path.join(args.path, 'res_ios')
			if not os.path.isdir(self.res_path):
				print("invalid path, can't find res path > ", args.path)
				return False
		else:
			print("invalid path, not a directory > ", args.path)
			return False

		if args.log:
			print("res_path >", self.res_path)
			print("res_build_path >", self.res_build_path)

		self.res_in_path = None
		self.res_in_build_path = None
		if args.input and os.path.isdir(args.input) and os.path.isdir(os.path.join(args.input, 'res_ios')):
			self.res_in_path = os.path.join(args.input, 'res')
			self.res_in_build_path = os.path.join(args.input, 'res_ios')
			if args.log:
				print("res_in_path >", self.res_in_path)
				print("res_in_build_path >", self.res_in_build_path)

		return True

	def command_build2(self):
		init = self.initbuildArgs()
		if not init:
			return

		self.res_flist_data = flistparse.read_flist(os.path.join(self.res_path, 'flist'))
		if self.res_in_path and self.res_in_build_path:
			self.res_in_flist_data = flistparse.read_flist(self.res_in_path)
			self.res_in_build_flist_data = flistparse.read_flist(self.res_in_build_path)
			pass

		#find all plist file
		self.plist_filelist = OrderedDict()
		if self.res_flist_data and self.res_flist_data['fileInfoList']:
			for name in self.res_flist_data['fileInfoList']:
				full_name = os.path.join(self.res_path, name)
				if full_name.endswith('.plist'):
					self.plist_filelist[name] = self.res_flist_data['fileInfoList'][name]['code']
					pass
				pass
			pass
		
		if self.res_flist_data and self.res_flist_data['fileInfoList'] and args.image_folder:
			for name in self.res_flist_data['fileInfoList']:
				for folder in args.image_folder:
					if name.startswith(folder):
						self.plist_filelist[name] = self.res_flist_data['fileInfoList'][name]['code']
						pass
			pass

		for file in self.plist_filelist:
			self.build_convert(file)

		ret = flistparse.build_flist(self.res_build_path, self.res_flist_data)
		print("build_flist >", ret)

		return True

	def build_convert(self, plist_file):
		is_copy = self.copy_file(plist_file)
		if is_copy:
			return
		
		self.unpacker(plist_file)

	def copy_file(self, plist_file):
		if not self.res_in_path or not self.res_in_build_path or not self.res_in_flist_data or not self.res_in_build_flist_data:
			return False

		code = self.res_flist_data['fileInfoList'][plist_file]['code']
		if self.res_in_flist_data and self.res_in_flist_data['fileInfoList'] \
			and self.res_in_flist_data['fileInfoList'].has_key(plist_file)	\
			and self.res_in_flist_data['fileInfoList'][plist_file].has_key('code'):
			compairCode = self.res_in_flist_data['fileInfoList'][plist_file]['code']
			if compairCode != code:
				return False
		else:
			return False
		

		file_ext = get_image_ext(plist_file)

		if file_ext == ".plist":
			source_plist = os.path.join(self.res_in_build_path, plist_file)
			source_pvr = os.path.join(self.res_in_build_path, plist_file.replace(".plist", ".pvr.ccz"))
			dest_plist = os.path.join(self.res_build_path, plist_file)
			dest_pvr = os.path.join(self.res_build_path, plist_file.replace(".plist", ".pvr.ccz"))
			if not os.path.isfile(source_plist):
				print('source_plist not file >', source_plist)
				return False
			if not os.path.isfile(source_pvr):
				print('source_pvr not file >', source_pvr)
				return False
			if args.log:
				print("copy_file >", source_plist)
				print("copy_file >", source_pvr)

			if not os.path.exists(os.path.dirname(dest_pvr)):
				os.makedirs(os.path.dirname(dest_pvr))

			shutil.copyfile(source_plist, dest_plist)
			shutil.copyfile(source_pvr, dest_pvr)
			self.update_file(plist_file)
		else:
			source_pvr = os.path.join(self.res_in_build_path, plist_file.replace(".png", ".pvr.ccz"))
			dest_pvr = os.path.join(self.res_build_path, plist_file.replace(".png", ".pvr.ccz"))
			if not os.path.isfile(source_pvr):
				return False
			if args.log:
				print("copy_file >", source_pvr)
			if not os.path.exists(os.path.dirname(dest_pvr)):
				os.makedirs(os.path.dirname(dest_pvr))
			shutil.copyfile(source_pvr, dest_pvr)
			self.update_file(plist_file)

		return True

	def unpacker(self, plist_file):
		print('unpacker >', plist_file)
		full_path = plist_file
		if self.command == 'build':
			full_path = os.path.join(self.res_path, plist_file)
		if not os.path.isfile(full_path):
			print("fail: can't find plist_file >" + full_path)
			return False

		file_path,_ = os.path.split(full_path)
		file_ext = get_image_ext(plist_file)
		# create output dir
		if self.command == 'build':
			output_dir,_ = os.path.splitext(os.path.join(self.res_build_path, plist_file))
		else:
			if args.output:
				output_dir = args.output
				relpath = os.path.relpath(plist_file, args.path)
				if relpath and relpath != '.':
					output_dir = os.path.join(args.output, os.path.relpath(plist_file, args.path).replace(file_ext, ''))
					pass
			else:
				output_dir,_ = os.path.splitext(os.path.join(plist_file))
		
		if file_ext == ".png" or file_ext == ".pvr.ccz":
			return self.package_png_to_pvrccz(plist_file)
		pass

		# file_md5 = get_file_md5(full_path)
		
		try:
			data = readPlist(full_path)
		except Exception, _:
			print("fail: read plist file failed >", full_path)
			return False

		# check file format
		frame_data_list = dataparse.parsedata(data)
		if not frame_data_list:
			print("fail: unsupport format >", full_path)
			return False

		# check image format
		image_file = os.path.join(file_path , data.metadata.textureFileName)
		if self.command == 'build' or self.command == 'convert':
			self.image_file[plist_file] = plist_file.replace('.plist' , get_image_ext(data.metadata.textureFileName))
		
		if not os.path.isfile(image_file):
			print("fail: can't find image_file >", image_file)
			return False
		image_ext = get_image_ext(image_file)
		if image_ext in pvr_file_ext:
			if convert_pvr_to_png(image_file, image_ext):
				image_file = image_file.replace(image_ext, ".png")
			else:
				print("fail: can't convert pvr to png, are you sure installed TexturePacker command line tools ? More infomation:\nhttps://www.codeandweb.com/texturepacker/documentation#install-command-line")
				return False

			
		if not os.path.exists(os.path.dirname(output_dir)):
			os.makedirs(os.path.dirname(output_dir))
		
		try:
			src_image = Image.open(image_file)
		except Exception, _:
			print("fail: can't open image %s " %image_file)
			return False

		for frame_data in frame_data_list:
			temp_image = src_image.crop(frame_data["src_rect"])
			if frame_data["rotated"]:
				temp_image = temp_image.rotate(90, expand=1)

			# create dst image
			dst_image = Image.new('RGBA', frame_data["source_size"], (0,0,0,0))
			dst_image.paste(temp_image, frame_data["offset"], mask=0)

			output_path = os.path.join(output_dir, frame_data["name"])
			if not os.path.exists(os.path.dirname(output_path)):
				os.makedirs(os.path.dirname(output_path))
			dst_image.save(output_path)

		if self.command == 'build' or self.command == 'convert':
			ret = self.package_png_to_pvrccz(plist_file, output_dir)
			if ret:
				pass
			if image_ext in pvr_file_ext:
				os.remove(image_file)
			shutil.rmtree(output_dir)
			pass
			
		if args.log:
			print("success:", full_path)
		return True

	def pack(self, image_folder):
		if args.log:
			print("pack > ", image_folder)
		if image_folder and os.path.isdir(image_folder):
			_, file_name = os.path.split(image_folder)
			if args.output:
				output_dir = os.path.join(args.output, file_name)
			else:
				output_dir = image_folder
			file_ext = ".png"
			if args.texture_format.lower() == "pvr2ccz":
				file_ext = ".pvr.ccz"
			elif args.texture_format.lower() == "pvr2":
				file_ext = ".pvr"
			else:
				pass
			if args.multipack:
				output_dir = output_dir + "{n1}"
			elif args.multipack_list:
				for image in args.multipack_list:
					if image == "*" or image == file_name:
						output_dir = output_dir + "{n1}"
						break
				pass

			cmd = "TexturePacker {image_folder} --sheet {output_dir}{file_ext} --data {output_dir}.plist --format cocos2d --texture-format {texture_format} --opt {opt} --border-padding 0 --shape-padding 0 --max-size 2048 --enable-rotation".format( \
				image_folder = image_folder, output_dir = output_dir, file_ext = file_ext, texture_format = args.texture_format.lower(), opt = args.image_option)
			if args.no_trim_image:
				for image in args.no_trim_image:
					if image == "*" or image == file_name:
						cmd = cmd + " --no-trim"
						break
				pass
			if args.image_option == "RGBA8888":
				cmd = cmd + " --size-constraints NPOT"
			else:
				cmd = cmd + " --size-constraints POT"
			if args.multipack:
				cmd = cmd + " --multipack"
				pass
			if args.multipack_list:
				for image in args.multipack_list:
					if image == "*" or image == file_name:
						cmd = cmd + " --multipack"
						break
				pass
			if args.log:
				print("cmd > ", cmd)
			else:
				cmd = cmd + " --quiet"
			if os.system(cmd) == 0:
				if args.log:
					print("success:", image_folder)
				return True
		else:
			print("fail: can't find image_folder or plist_file")
			return False

		return False

	def package_png_to_pvrccz(self, plist_file, image_folder=None):
		if args.log:
			print("package_png_to_pvrccz > ", plist_file)
		opt = args.image_option
		if image_folder and os.path.isdir(image_folder):
			_,file_name = os.path.split(plist_file)
			cmd = "TexturePacker {pvr_folder} --sheet {pvr_folder}.pvr.ccz --data {pvr_folder}.plist --format cocos2d --texture-format pvr2ccz --opt {pvr_opt} --border-padding 2 --shape-padding 2 --max-size 2048 --enable-rotation".format(pvr_folder = image_folder, pvr_opt = opt)
			if self.image_file and self.image_file.has_key(plist_file) \
			and get_image_ext(self.image_file[plist_file]) in pvr_file_ext:
				pass
			else:
				cmd = cmd + " --premultiply-alpha"
			if args.no_trim_image:
				for image in args.no_trim_image:
					if image == "*" or image == file_name:
						cmd = cmd + " --no-trim"
						break
				pass
			if args.other_option:
				cmd = cmd + " " + args.other_option.replace('+', ' ').replace('_', '-')
			if opt == "RGBA8888":
				cmd = cmd + " --size-constraints NPOT"
			else:
				cmd = cmd + " --size-constraints POT"
			if args.log:
				print("cmd > ", cmd)
			else:
				cmd = cmd + " --quiet"
			if os.system(cmd) == 0:
				if self.command == 'build':
					self.update_file(plist_file)
				return True
			return False
		elif (plist_file.endswith('.png') or plist_file.endswith('.pvr.ccz')):
			_,file_name = os.path.split(plist_file)
			image_ext = get_image_ext(plist_file)
			if self.command == 'build':
				png_path = os.path.join(self.res_path, plist_file)
				pvr_path = os.path.join(self.res_build_path, plist_file).replace(image_ext, '')
			else:
				png_path = plist_file
				if args.output:
					pvr_path = os.path.join(args.output, os.path.relpath(plist_file, args.path)).replace(image_ext, '')
				else:
					pvr_path,_ = os.path.splitext(os.path.join(plist_file))
			cmd = "TexturePacker {png_path} --sheet {pvr_path}.pvr.ccz --data {pvr_path}.plist --format cocos2d --texture-format pvr2ccz --opt {pvr_opt} --border-padding 0 --shape-padding 0 --disable-rotation --allow-free-size --no-trim".format(png_path = png_path, pvr_path = pvr_path, pvr_opt = opt)
			if plist_file.endswith('.pvr.ccz'):
				pass
			else:
				cmd = cmd + " --premultiply-alpha"
			if opt == "RGBA8888":
				cmd = cmd + " --size-constraints NPOT"
			else:
				cmd = cmd + " --size-constraints POT"
			if args.log:
				print("cmd > ", cmd)
			else:
				cmd = cmd + " --quiet"
			if os.system(cmd) == 0:
				os.remove(pvr_path+'.plist')
				if self.command == 'build':
					self.update_file(plist_file)
				return True
			return False
		else:
			print("fail: can't find image_folder or plist_file")
			return False
		return False

	def update_file(self, plist_file):
		if self.res_flist_data and self.res_flist_data['fileInfoList'][plist_file]:
			if plist_file.endswith('.plist'):
				full_path = os.path.join(self.res_build_path, plist_file)
				pvr_fullpath = full_path.replace('.plist', '.pvr.ccz')
				pvr_path = plist_file.replace('.plist', '.pvr.ccz')
				if self.image_file and self.image_file.has_key(plist_file) and self.res_flist_data['fileInfoList'].has_key(self.image_file[plist_file]):
					del self.res_flist_data['fileInfoList'][self.image_file[plist_file]]
				else:
					if self.res_flist_data['fileInfoList'].has_key(plist_file.replace('.plist', '.pvr.ccz')):
						del self.res_flist_data['fileInfoList'][plist_file.replace('.plist', '.pvr.ccz')]
					if self.res_flist_data['fileInfoList'].has_key(plist_file.replace('.plist', '.png')):
						del self.res_flist_data['fileInfoList'][plist_file.replace('.plist', '.png')]

				self.res_flist_data['fileInfoList'][plist_file]['code'] = get_file_md5(full_path)
				self.res_flist_data['fileInfoList'][plist_file]['size'] = os.path.getsize(full_path)
				self.res_flist_data['fileInfoList'][pvr_path] = {
					'code' : get_file_md5(pvr_fullpath),
					'size' : os.path.getsize(pvr_fullpath)
				}
			elif plist_file.endswith('.png') or plist_file.endswith('.pvr.ccz'):
				if plist_file and self.res_flist_data['fileInfoList'].has_key(plist_file):
					del self.res_flist_data['fileInfoList'][plist_file]
				pvr_path = plist_file.replace('.png', '.pvr.ccz')
				pvr_fullpath = os.path.join(self.res_build_path, pvr_path)
				self.res_flist_data['fileInfoList'][pvr_path] = {
					'code' : get_file_md5(pvr_fullpath),
					'size' : os.path.getsize(pvr_fullpath)
				}
			pass

	def packer_dir(self, path):
		if args.log:
			print("packer_dir >", path)
		recursive = args.recursive
		if not os.path.isdir(path):
			print("packer_dir is not dir >", path)
			return

		if recursive:
			for name in os.listdir(path):
				full_name = os.path.join(path, name)
				if not os.path.isdir(full_name):
					continue
				if name in ignore_folder:
					continue
				if args.ignore_list and name in args.ignore_list:
					continue
				if args.image_folder:
					if name in args.image_folder:
						self.pack(full_name)
				else:
					self.pack(full_name)
		else:
			self.pack(path)

	# Get the all files & directories in the specified directory (path).
	def unpacker_dir(self, path):
		if args.log:
			print("unpacker_dir >", path)
		recursive = args.recursive
		for name in os.listdir(path):
			full_name = os.path.join(path, name)
			if full_name.endswith('.plist'):
				self.unpacker(full_name)
				pass
			elif args.image_folder and (full_name.endswith('.png') or full_name.endswith('.pvr.ccz')):
				for folder in args.image_folder:
					if folder == "*" or os.path.relpath(path, args.path).replace("\\", "/").startswith(folder.replace("\\", "/")):
						self.unpacker(full_name)
						break
				if args.image_folder[0] == "*":
					self.unpacker(full_name)
					pass
			elif recursive and os.path.isdir(full_name):
				self.unpacker_dir(full_name)

			
def main():
	parser = argparse.ArgumentParser(prog="textool", usage=usage)
	parser.add_argument("command", type=str, help="textool command")
	parser.add_argument("path", type=str, help="plist file name or directory")

	group_file = parser.add_argument_group('For file')
	group_file.add_argument("-i", "--input", type=str, metavar="input", help="input directory to compair")
	group_file.add_argument("-o", "--output", type=str, metavar="output", help="specified output directory")
	group_file.add_argument("-f", "--image_file", nargs="*", type=str, metavar="image_file", help="specified image file for plist")
	group_file.add_argument("-if", "--image_folder", nargs="*", type=str, metavar="image_folder", help="specified image folder")
	group_dir = parser.add_argument_group('For directory')
	group_dir.add_argument("-r", "--recursive", action="store_true", default=False)

	group_option = parser.add_argument_group('For option')
	group_option.add_argument("-p", "--platform", type=str, metavar="platform", default='android')
	group_option.add_argument("-tf", "--texture_format", type=str, metavar="texture_format", default='png')
	group_option.add_argument("-opt", "--image_option", type=str, metavar="image_opt", default='RGBA8888')
	group_option.add_argument("-mpk", "--multipack", action="store_true", default=False)
	group_option.add_argument("-mpl", "--multipack_list", nargs="*", type=str, metavar="multipack_list", help="multipack image list")
	group_option.add_argument("-nti", "--no_trim_image", nargs="*", type=str, metavar="no_trim_image", help="no-trim image list")
	group_option.add_argument("-oo", "--other_option", type=str, metavar="other_option", default='')
	group_option.add_argument("-ncl", "--no_convert_list", nargs="*", type=str, metavar="no_convert_list", help="no convert list when convert")
	group_option.add_argument("-igl", "--ignore_list", nargs="*", type=str, metavar="ignore_list", help="ignore list when pack")
	group_option.add_argument("-l", "--log", action="count", default=0)
	group_option.add_argument("-ps", "--poolSize", type=int, default=1, help="ThreadPool size")
	group_option.add_argument("-rl", "--resource_list", nargs="*", type=str, metavar="resource_list", help="resouce list when build")
	group_option.add_argument("-av", "--app_version", type=str, metavar="app_version", default='1.0.0', help="app list version when build")
	group_option.add_argument("-rv", "--res_version", type=int, metavar="res_version", default=0, help="res list version when build")
	group_option.add_argument("-de", "--debug", type=int, metavar="debug", default=0, help="res list debug when build")

	param = parser.parse_args()
	g_init(param)
	global args
	args = get_args()
	if args.log:
		print("command >", args.command.lower())
		print("path >", args.path)

	textureTool = TextureTool()
	textureTool.run()
	
if __name__ == '__main__':
	main()