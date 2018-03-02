import os
import sys
import hashlib
import zlib
import tempfile
import struct
import time,datetime
from config import *

def timestamp_to_time(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
    pass

def get_image_ext(image_file):
	for ext in pvr_file_ext:
		if image_file.endswith(ext):
			return ext
	return os.path.splitext(image_file)[1]

def get_file_modifytime(image_file):
    # image_file = unicode(image_file, 'utf8')
    t = os.path.getmtime(image_file)
    return t
    
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