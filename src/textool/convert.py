#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  
import os, sys
import tempfile
import shutil
import struct
import zlib
from PIL import Image
from utils import *
from config import *

def pvr_compress_ccz(tempfile, destfile):
		pvr = open(tempfile, 'rb').read()
		pvrccz = open(destfile, "wb")
		pvrccz.write(struct.pack(">4sHHII","CCZ!",0,1,0,len(pvr)))
		pvrccz.write(zlib.compress(pvr))
		pvrccz.close()

def convert_to_etc1(input_path, output_dir, _suffix="", _zlib=True):
	print("convert_to_etc1 image path > ", input_path)
	filepath, filename = os.path.split(input_path)
	pre,ext = os.path.splitext(filename)
	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)
	exists_alpha = ext != ".jpg"

	if _zlib:
		dst_rgb_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr.ccz")
		dst_a_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr.ccz@alpha")
	else:
		dst_rgb_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr")
		dst_a_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr" + "@alpha")

	if os.path.exists(dst_rgb_pvr_file):
		# print("input_path > ", input_path)
		# print("input_path time > ", timestamp_to_time(get_file_modifytime(input_path)))
		# print("dst_rgb_pvr_file > ", dst_rgb_pvr_file)
		# print("dst_rgb_pvr_file time > ", timestamp_to_time(get_file_modifytime(dst_rgb_pvr_file)))
		if input_path != "E:\\quickv3\\sanguosha\\res\\ui\\anim\\spineButton\\jinmenhuan/skeleton.png":
			if get_file_modifytime(input_path) < get_file_modifytime(dst_rgb_pvr_file):
				return
			pass
		pass
		
	tmp_rgb_file = tempfile.mktemp(ext)
	tmp_a_file = tempfile.mktemp(ext)

	if exists_alpha:
		im = Image.open(input_path, 'r')
		im = im.convert('RGBA')
		rgbData = im.tobytes("raw", "RGB")
		alphaData = im.tobytes("raw", "A")
		im.convert('RGB').save(tmp_rgb_file)
		Image.frombytes("L", im.size, alphaData).save(tmp_a_file)
		pass
		# command = "convert %s -alpha Off %s" %(input_path, tmp_rgb_file)
		# os.system(command)

		# command = "convert %s -channel A -alpha extract %s" %(input_path, tmp_a_file)
		# os.system(command)
	else:
		shutil.copy(input_path, tmp_rgb_file)

	tmp_rgb_pvr_file = tempfile.mktemp(".pvr")
	tmp_a_pvr_file = tempfile.mktemp(".pvr")
	
	command = "%s -f ETC1 -i %s -o %s -q etcfast" %("PVRTexToolCLI", tmp_rgb_file, tmp_rgb_pvr_file)
	# print(command)
	os.system(command)
	os.remove(tmp_rgb_file)

	if exists_alpha:
		command = "%s -f ETC1 -i %s -o %s -q etcfast" %("PVRTexToolCLI", tmp_a_file, tmp_a_pvr_file)
		# print(command)
		os.system(command)
		os.remove(tmp_a_file)
	
	if _zlib:
		pvr_compress_ccz(tmp_rgb_pvr_file, dst_rgb_pvr_file)
		os.remove(tmp_rgb_pvr_file)

		if exists_alpha:
			pvr_compress_ccz(tmp_a_pvr_file, dst_a_pvr_file)
			os.remove(tmp_a_pvr_file)

	else:
		os.rename(tmp_rgb_pvr_file, dst_rgb_pvr_file)
		os.rename(tmp_a_pvr_file, dst_a_pvr_file)

	if exists_alpha:
		return {"color": dst_rgb_pvr_file, "alpha": dst_a_pvr_file}

	return dst_rgb_pvr_file

def packer_dir(path, ignore_list, image_folder, recursive):
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