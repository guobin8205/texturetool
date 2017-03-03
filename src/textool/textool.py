#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  
from __future__ import print_function

import os
import sys
import argparse
import dataparse
import flistparse
import hashlib
import json
import shutil

from PIL import Image
from parse import parse
from plistlib import readPlist
from collections import OrderedDict

usage = """
%(prog)s build D:/project/tag/v2.0 -i D:/project/tag/v1.0 -l -if ui/item0 ui/item1
%(prog)s unpack D:/project/tag/v2.0/ui/button.plist -o D:/prj/test
%(prog)s convert D:/project/tag/v2.0/ui/button.plist -o D:/prj/test
%(prog)s convert D:/project/tag/v2.0 -o D:/prj/test -r -if ui/item0 ui/item1
"""

pvr_file_ext = (".pvr", ".pvr.gz", ".pvr.ccz")
ignore_folder = (".svn")

def get_image_ext(image_file):
	for ext in pvr_file_ext:
		if image_file.endswith(ext):
			return ext
	return os.path.splitext(image_file)[1]
    
def get_file_md5(filename):
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        b = f.read()
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

def convert_pvr_to_png(image_file, image_ext):
	print("convert_pvr_to_png > ", image_file)
	pvr_path = image_file.replace(image_ext, "")
	if os.system("TexturePacker {pvr_pathname} --sheet {pvr_path}.png --data {pvr_path}_temp.plist --texture-format png --border-padding 0 --shape-padding 0 --disable-rotation --allow-free-size --no-trim".format(pvr_pathname = image_file, pvr_path = pvr_path)) == 0:
		os.remove(pvr_path + "_temp.plist")
		return True
	return False

class TextureTool(object):
	def __init__(self, args):
		self.args = args
		self.image_file = {}

	def run(self):
		self.command = self.args.command.lower()
		if self.command == 'build':
			return self.command_build()
		elif self.command == 'convert':
			return self.command_unpack()
		elif self.command == 'unpack':
			return self.command_unpack()
		elif self.command == 'pack':
			return self.command_pack()
		else:
			print("unkown command,  > ", self.command)

	def command_pack(self):
		if os.path.isdir(self.args.path):
			self.packer_dir(self.args.path)
		else:
			print("invalid path, not a directory > ", self.args.path)
		pass

	def command_unpack(self):
		if os.path.isdir(self.args.path):
			self.unpacker_dir(self.args.path)
		elif os.path.isfile(self.args.path):
			self.unpacker(self.args.path)
		else:
			print("invalid path, not a directory > ", self.args.path)

	def command_convert(self):

		pass

	def initbuildArgs(self):
		if os.path.isdir(self.args.path):
			self.res_path = os.path.join(self.args.path, 'res')
			self.res_build_path = os.path.join(self.args.path, 'res_ios')
			if not os.path.isdir(self.res_path):
				print("invalid path, can't find res path > ", self.args.path)
				return False
		else:
			print("invalid path, not a directory > ", self.args.path)
			return False

		if self.args.log:
			print("res_path >", self.res_path)
			print("res_build_path >", self.res_build_path)

		self.res_in_path = None
		self.res_in_build_path = None
		if self.args.input and os.path.isdir(self.args.input) and os.path.isdir(os.path.join(self.args.input, 'res_ios')):
			self.res_in_path = os.path.join(self.args.input, 'res')
			self.res_in_build_path = os.path.join(self.args.input, 'res_ios')
			if self.args.log:
				print("res_in_path >", self.res_in_path)
				print("res_in_build_path >", self.res_in_build_path)

		return True
	
	def command_build(self):
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
		
		if self.res_flist_data and self.res_flist_data['fileInfoList'] and self.args.image_folder:
			for name in self.res_flist_data['fileInfoList']:
				for folder in self.args.image_folder:
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
			if self.args.log:
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
			if self.args.log:
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

		file_path,file_name = os.path.split(full_path)
		file_ext = get_image_ext(plist_file)
		# create output dir
		if self.command == 'build':
			output_dir,_ = os.path.splitext(os.path.join(self.res_build_path, plist_file))
		else:
			if self.args.output:
				output_dir = self.args.output
				relpath = os.path.relpath(plist_file, self.args.path)
				if relpath and relpath != '.':
					output_dir = os.path.join(self.args.output, os.path.relpath(plist_file, self.args.path).replace(file_ext, ''))
					pass
			else:
				output_dir,_ = os.path.splitext(os.path.join(plist_file))
		
		if file_ext == ".png" or file_ext == ".pvr.ccz":
			return self.package_png_to_pvrccz(plist_file)
		pass

		# file_md5 = get_file_md5(full_path)
		
		try:
			data = readPlist(full_path)
		except Exception, e:
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
		except Exception, e:
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
			
		if self.args.log:
			print("success:", full_path)
		return True

	def pack(self, image_folder):
		if self.args.log:
			print("pack > ", image_folder)
		if image_folder and os.path.isdir(image_folder):
			file_path, file_name = os.path.split(image_folder)
			if self.args.output:
				output_dir = os.path.join(self.args.output, file_name)
			else:
				output_dir = image_folder
			file_ext = ".png"
			if self.args.texture_format.lower() == "pvr2ccz":
				file_ext = ".pvr.ccz"
			elif self.args.texture_format.lower() == "pvr2":
				file_ext = ".pvr"
			else:
				pass
			if self.args.multipack:
				output_dir = output_dir + "{n1}"
			elif self.args.multipack_list:
				for image in self.args.multipack_list:
					if image == "*" or image == file_name:
						output_dir = output_dir + "{n1}"
						break
				pass

			cmd = "TexturePacker {image_folder} --sheet {output_dir}{file_ext} --data {output_dir}.plist --format cocos2d --texture-format {texture_format} --opt {opt} --border-padding 2 --shape-padding 2 --max-size 2048 --enable-rotation".format( \
				image_folder = image_folder, output_dir = output_dir, file_ext = file_ext, texture_format = self.args.texture_format.lower(), opt = self.args.image_option)
			if self.args.no_trim_image:
				for image in self.args.no_trim_image:
					if image == "*" or image == file_name:
						cmd = cmd + " --no-trim"
						break
				pass
			if self.args.image_option == "RGBA8888":
				cmd = cmd + " --size-constraints NPOT"
			else:
				cmd = cmd + " --size-constraints POT"
			if self.args.multipack:
				cmd = cmd + " --multipack"
				pass
			if self.args.multipack_list:
				for image in self.args.multipack_list:
					if image == "*" or image == file_name:
						cmd = cmd + " --multipack"
						break
				pass
			if self.args.log:
				print("cmd > ", cmd)
			else:
				cmd = cmd + " --quiet"
			if os.system(cmd) == 0:
				if self.args.log:
					print("success:", image_folder)
				return True
		else:
			print("fail: can't find image_folder or plist_file")
			return False

		return False

	def package_png_to_pvrccz(self, plist_file, image_folder=None):
		if self.args.log:
			print("package_png_to_pvrccz > ", plist_file)
		opt = self.args.image_option
		if image_folder and os.path.isdir(image_folder):
			file_path,file_name = os.path.split(plist_file)
			cmd = "TexturePacker {pvr_folder} --sheet {pvr_folder}.pvr.ccz --data {pvr_folder}.plist --format cocos2d --texture-format pvr2ccz --opt {pvr_opt} --border-padding 2 --shape-padding 2 --max-size 2048 --enable-rotation".format(pvr_folder = image_folder, pvr_opt = opt)
			if self.image_file and self.image_file.has_key(plist_file) \
			and get_image_ext(self.image_file[plist_file]) in pvr_file_ext:
				pass
			else:
				cmd = cmd + " --premultiply-alpha"
			if self.args.no_trim_image:
				for image in self.args.no_trim_image:
					if image == "*" or image == file_name:
						cmd = cmd + " --no-trim"
						break
				pass
			if self.args.other_option:
				cmd = cmd + " " + self.args.other_option.replace('+', ' ').replace('_', '-')
			if opt == "RGBA8888":
				cmd = cmd + " --size-constraints NPOT"
			else:
				cmd = cmd + " --size-constraints POT"
			if self.args.log:
				print("cmd > ", cmd)
			else:
				cmd = cmd + " --quiet"
			if os.system(cmd) == 0:
				if self.command == 'build':
					self.update_file(plist_file)
				return True
			return False
		elif (plist_file.endswith('.png') or plist_file.endswith('.pvr.ccz')):
			file_path,file_name = os.path.split(plist_file)
			image_ext = get_image_ext(plist_file)
			if self.command == 'build':
				png_path = os.path.join(self.res_path, plist_file)
				pvr_path = os.path.join(self.res_build_path, plist_file).replace(image_ext, '')
			else:
				png_path = plist_file
				if self.args.output:
					pvr_path = os.path.join(self.args.output, os.path.relpath(plist_file, self.args.path)).replace(image_ext, '')
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
			if self.args.log:
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
		if self.args.log:
			print("packer_dir >", path)
		recursive = self.args.recursive
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
				if self.args.ignore_list and name in self.args.ignore_list:
					continue
				if self.args.image_folder:
					if name in self.args.image_folder:
						self.pack(full_name)
				else:
					self.pack(full_name)
		else:
			self.pack(path)

	# Get the all files & directories in the specified directory (path).
	def unpacker_dir(self, path):
		if self.args.log:
			print("unpacker_dir >", path)
		recursive = self.args.recursive
		for name in os.listdir(path):
			full_name = os.path.join(path, name)
			if full_name.endswith('.plist'):
				self.unpacker(full_name)
				pass
			elif self.args.image_folder and (full_name.endswith('.png') or full_name.endswith('.pvr.ccz')):
				for folder in self.args.image_folder:
					if folder == "*" or os.path.relpath(path, self.args.path).replace("\\", "/").startswith(folder.replace("\\", "/")):
						self.unpacker(full_name)
						break
				if self.args.image_folder[0] == "*":
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
	group_option.add_argument("-tf", "--texture_format", type=str, metavar="texture_format", default='png')
	group_option.add_argument("-opt", "--image_option", type=str, metavar="image_opt", default='RGBA8888')
	group_option.add_argument("-mpk", "--multipack", action="store_true", default=False)
	group_option.add_argument("-mpl", "--multipack_list", nargs="*", type=str, metavar="multipack_list", help="multipack image list")
	group_option.add_argument("-nti", "--no_trim_image", nargs="*", type=str, metavar="no_trim_image", help="no-trim image list")
	group_option.add_argument("-oo", "--other_option", type=str, metavar="other_option", default='')
	group_option.add_argument("-igl", "--ignore_list", nargs="*", type=str, metavar="ignore_list", help="ignore list when pack")
	group_option.add_argument("-l", "--log", action="count", default=0)

	args = parser.parse_args()
	if args.log:
		print("command >", args.command.lower())
		print("path >", args.path)

	textureTool = TextureTool(args)
	textureTool.run()
	
if __name__ == '__main__':
	main()