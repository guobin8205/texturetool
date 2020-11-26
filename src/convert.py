#!/usr/bin/python
#coding=utf-8
#Python 3.6

from PIL import Image

from utils import *

pathlock = Lock()

def pvr_compress_ccz(tempfile, destfile):
	pvr = open(tempfile, 'rb')
	pvrData = pvr.read()
	pvrccz = open(destfile, "wb")
	# print(destfile, len(pvrData))
	pvrccz.write(struct.pack(">4sHHII",b"CCZ!",0,1,0,len(pvrData)))
	pvrccz.write(zlib.compress(pvrData))
	pvr.close()
	pvrccz.close()
	return True

def convert_from_texturepacker(input_path, output_dir,  _suffix="", _zlib=True):
	start_time = time.time()
	args = get_args()
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
		dst_a_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr@alpha")

	if os.path.exists(dst_rgb_pvr_file):
		if get_file_modifytime(input_path) < get_file_modifytime(dst_rgb_pvr_file):
			if args.image_option == "ETC1" and exists_alpha:
				return {"color": dst_rgb_pvr_file, "alpha": dst_a_pvr_file, "exists_alpha": exists_alpha}

			return {"color": dst_rgb_pvr_file, "exists_alpha": exists_alpha}
		pass
	
	try:
		texture_option = "RGBA8888"
		if args.image_option == "PVRTC4":
			if exists_alpha:
				texture_option = "PVRTCI_4BPP_RGBA"
			else:
				texture_option = "PVRTCI_4BPP_RGB"
		elif args.image_option == "ETC1":
			texture_option = "ETC1_RGB"
		else:
			texture_option = args.image_option

		if _zlib:
			texture_format = "pvr3ccz"
		else:
			texture_format = "pvr3"

		command = "TexturePacker \"%s\" --sheet \"%s\" --opt %s --texture-format %s --format cocos2d --disable-rotation --padding 0 --extrude 0 --trim-mode Trim" %(input_path, dst_rgb_pvr_file, texture_option, texture_format)
		
		if args.image_option == "PVRTC4" or args.image_option == "ETC1":
			command = command + " --size-constraints POT"
		else:
			command = command + " --size-constraints NPOT"

		if args.image_option == "PVRTC4":
			command = command + " --force-squared"
			command = command + " --alpha-handling PremultiplyAlpha --dither-type FloydSteinbergAlpha"

		if args.log:
			log("convert_from_texturepacker command > %s" % command)
		
		p = Popen(command,stdout=PIPE, shell=True,stderr=PIPE)
		out, err = p.communicate()
		if p.returncode != 0:
			log("Non zero exit code:%s executing: %s" % (p.returncode, command))
			log(err)
			return

		if args.image_option == "ETC1" and exists_alpha:
			command = "TexturePacker \"%s\" --sheet \"%s\" --opt %s --texture-format %s --format cocos2d --disable-rotation --padding 0 --extrude 0 --trim-mode Trim" %(input_path, dst_a_pvr_file, "ETC1_A", texture_format)
			command = command + " --size-constraints POT"
			if args.log:
				log("convert_to_etc1 command alpha > %s" % command)
			
			p = Popen(command,stdout=PIPE, shell=True,stderr=PIPE)
			out, err = p.communicate()
			if p.returncode != 0:
				log("Non zero exit code:%s executing: %s" % (p.returncode, command))
				log(err)
				return
	except Exception as e:
		raise
	else:
		pass
	finally:
		microseconds = round((time.time()-start_time),2)
		log("convert %s elapsed time %.2fs" % (input_path, microseconds))

	if args.image_option == "ETC1" and exists_alpha:
		return {"color": dst_rgb_pvr_file, "alpha": dst_a_pvr_file, "exists_alpha": exists_alpha}

	return {"color": dst_rgb_pvr_file, "exists_alpha": exists_alpha}

def convert_to_etc1(input_path, output_dir, tempdir=None, _suffix="", _zlib=True):
	# log("convert_to_etc1 image path > %s"%(input_path))
	start_time = time.time()
	args = get_args()
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
			with open(input_path, 'rb') as f:
				im = Image.open(f)
				im = im.convert('RGBA')
				rgbData = im.tobytes("raw", "RGB")
				alphaData = im.tobytes("raw", "A")
				im.convert('RGB').save(tmp_rgb_file)
				Image.frombytes("L", im.size, alphaData).save(tmp_a_file)
				del im
				pass
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
		command = "%s -f ETC1 -i %s -o %s -q etcbest" %("PVRTexToolCLI", tmp_rgb_file, tmp_rgb_pvr_file)
		if args.log:
			log("convert_to_etc1 command > %s" % command)
		
		p = Popen(command,stdout=PIPE, shell=True,stderr=PIPE)
		out, err = p.communicate()
		if p.returncode != 0:
			log("Non zero exit code:%s executing: %s" % (p.returncode, command))
			log(err)
			return

		if exists_alpha:
			# tmp_a_pvr_file = tempfile.mktemp(".pvr")
			tmp_a_pvr_file = os.path.join(newtempdir, pre.replace(" ", "_") + _suffix + "_a.pvr")
			# log("convert_to_etc1 tmp_a_pvr_file path > ", os.getpid(), tmp_a_pvr_file)
			command = "%s -f ETC1 -i %s -o %s -q etcbest" %("PVRTexToolCLI", tmp_a_file, tmp_a_pvr_file)
			if args.log:
				log("convert_to_etc1 command alpha > %s" % command)
			# log(command)
			# os.system(command)
			p = Popen(command,stdout=PIPE, shell=True,stderr=PIPE)
			out, err = p.communicate()
			if p.returncode != 0:
				log("Non zero exit code:%s executing: %s" % (p.returncode, command))
				log(err)
				return
		
		if _zlib:
			if pvr_compress_ccz(tmp_rgb_pvr_file, dst_rgb_pvr_file):
				pass
			
			if exists_alpha:
				if pvr_compress_ccz(tmp_a_pvr_file, dst_a_pvr_file):
					pass
				pass
		else:
			os.rename(tmp_rgb_pvr_file, dst_rgb_pvr_file)
			if exists_alpha:
				os.rename(tmp_a_pvr_file, dst_a_pvr_file)

	except Exception as e:
		raise
	else:
		pass
	finally:
		if tempdir == None:
			shutil.rmtree(newtempdir)
		
		microseconds = round((time.time()-start_time),2)
		log("convert %s elapsed time %.2fs" % (input_path, microseconds))

	if exists_alpha:
		return {"color": dst_rgb_pvr_file, "alpha": dst_a_pvr_file}

	return {"color": dst_rgb_pvr_file}
