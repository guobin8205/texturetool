#!/usr/bin/python
#coding=utf-8
#Python 2.7.3
import os, sys
import tempfile
import shutil
import struct
import zlib
import multiprocessing
 
from subprocess import *
from PIL import Image
from utils import *
from config import *

pathlock = Lock()

def pvr_compress_ccz(tempfile, destfile):
	pvr = open(tempfile, 'rb')
	pvrData = pvr.read()
	pvrccz = open(destfile, "wb")
	pvrccz.write(struct.pack(">4sHHII","CCZ!",0,1,0,len(pvrData)))
	pvrccz.write(zlib.compress(pvrData))
	pvr.close()
	pvrccz.close()
	return True

def convert_to_etc1(input_path, output_dir, tempdir=None, _suffix="", _zlib=True):
	# log("convert_to_etc1 image path > %s"%(input_path))
	start_time = time.time()
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
		if get_file_modifytime(input_path) < get_file_modifytime(dst_rgb_pvr_file):
			if exists_alpha:
				return {"color": dst_rgb_pvr_file, "alpha": dst_a_pvr_file}

			return {"color": dst_rgb_pvr_file}
		pass
	# tmp_rgb_file = tempfile.mktemp(ext)
	
	try:
		if tempdir != None:
			newtempdir = tempdir
			if not os.path.isdir(newtempdir):
				if pathlock.acquire():
					if not os.path.isdir(newtempdir):
						os.makedirs(newtempdir)
					pathlock.release()
		else:
			newtempdir = tempfile.mkdtemp()

		tmp_rgb_file = os.path.join(newtempdir, pre.replace(" ", "_") + _suffix + "_rgb.png")
		# log("convert_to_etc1 tmp_rgb_file path > %s" %(tmp_rgb_file))
		if exists_alpha:
			# tmp_a_file = tempfile.mktemp(ext)
			tmp_a_file = os.path.join(newtempdir, pre.replace(" ", "_") + _suffix + "_a.png")
			# log("convert_to_etc1 tmp_a_file path > ", os.getpid(), tmp_a_file)
			im = Image.open(input_path, 'r')
			im = im.convert('RGBA')
			rgbData = im.tobytes("raw", "RGB")
			alphaData = im.tobytes("raw", "A")
			im.convert('RGB').save(tmp_rgb_file)
			Image.frombytes("L", im.size, alphaData).save(tmp_a_file)
			im.close()
			pass
			# command = "convert %s -alpha Off %s" %(input_path, tmp_rgb_file)
			# os.system(command)

			# command = "convert %s -channel A -alpha extract %s" %(input_path, tmp_a_file)
			# os.system(command)
		else:
			shutil.copy(input_path, tmp_rgb_file)

		# tmp_rgb_pvr_file = tempfile.mktemp(".pvr")
		tmp_rgb_pvr_file = os.path.join(newtempdir, pre.replace(" ", "_") + _suffix + "_rgb.pvr")
		# log("convert_to_etc1 tmp_rgb_pvr_file path > ", os.getpid(), tmp_rgb_pvr_file)
		command = "%s -f ETC1 -i %s -o %s -q etcfast" %("PVRTexToolCLI", tmp_rgb_file, tmp_rgb_pvr_file)
		
		p = Popen(command,stdin=PIPE,stdout=PIPE,stderr=PIPE)
		p.communicate()

		if exists_alpha:
			# tmp_a_pvr_file = tempfile.mktemp(".pvr")
			tmp_a_pvr_file = os.path.join(newtempdir, pre.replace(" ", "_") + _suffix + "_a.pvr")
			# log("convert_to_etc1 tmp_a_pvr_file path > ", os.getpid(), tmp_a_pvr_file)
			command = "%s -f ETC1 -i %s -o %s -q etcfast" %("PVRTexToolCLI", tmp_a_file, tmp_a_pvr_file)
			# log(command)
			# os.system(command)
			p = Popen(command,stdin=PIPE,stdout=PIPE,stderr=PIPE)
			p.communicate()
			# os.system(command)
			
			# time.sleep(0.5)
			# while p.poll() is None:
			#     time.sleep(0.1)
			# log("hijklmn", p.stdout.read())
			# log("remove tmp_a_file path > ", os.getpid(), tmp_a_pvr_file)
			# os.remove(tmp_a_file)
		
		if _zlib:
			if pvr_compress_ccz(tmp_rgb_pvr_file, dst_rgb_pvr_file):
				# time.sleep(0.5)
				# log("remove tmp_rgb_pvr_file path > ", os.getpid(), tmp_rgb_pvr_file)
				# os.remove(tmp_rgb_pvr_file)
				pass
			
			if exists_alpha:
				if pvr_compress_ccz(tmp_a_pvr_file, dst_a_pvr_file):
					# time.sleep(0.5)
					# log("remove tmp_a_pvr_file path > ", os.getpid(), tmp_a_pvr_file)
					# os.remove(tmp_a_pvr_file)
					pass
				pass
		else:
			os.rename(tmp_rgb_pvr_file, dst_rgb_pvr_file)
			if exists_alpha:
				os.rename(tmp_a_pvr_file, dst_a_pvr_file)

	except Exception, e:
		raise
	else:
		pass
	finally:
		if tempdir == None:
			shutil.rmtree(newtempdir)

		microseconds = round((time.time()-start_time),2)
		log('convert %s elapse %.2f s'% (input_path, microseconds))

	if exists_alpha:
		return {"color": dst_rgb_pvr_file, "alpha": dst_a_pvr_file}

	return {"color": dst_rgb_pvr_file}

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