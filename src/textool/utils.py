#!/usr/bin/python
#coding=utf-8
#Python 2.7.3
import os
import sys
import hashlib
import zlib
import tempfile
import struct
import time,datetime
from config import *
from multiprocessing import Lock
from distutils.spawn import find_executable

def g_init(param):
    global args
    args = param
    if args.path:
        args.path = args.path.replace('\\','/')
    if args.input:
        args.input = args.input.replace('\\','/')
    if args.output:
        args.output = args.output.replace('\\','/')
    pass

def get_args():
    return args

def command_available(command):
    return bool(find_executable(command))

def is_pvrtool_valid():
    return command_available("PVRTexToolCLI")

def is_ignore_path(relpath, ignores):
    if relpath and ignores:
        for path in ignores:
            if relpath.startswith(path):
                return True
    return False

loglock = Lock()
def log(s):
    if loglock.acquire():
        print(s)
        loglock.release()
    pass

def timestamp_to_time(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
    pass

def get_file_relpath(path, basepath):
    return path[len(basepath)+1:].replace("\\", "/")

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

def get_all_dirfiles(path, extentions=None, ignores=None):
    tempfiles = []
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for name in files:
                fileName, fileSuffix = os.path.splitext(name)
                if (extentions == None or (fileSuffix in extentions))  \
                and (ignores == None or not (fileSuffix in ignores)):
                    fullPath = path + root[len(path):]
                    fullName = fullPath + '/' + name
                    if not os.path.exists(fullName):
                        continue

                    tempfiles.append(fullName)
            else:
                continue
            break
    elif os.path.exists(path):
        fileName, fileSuffix = os.path.splitext(path)
        if extentions == None or (fileSuffix in extentions):
            tempfiles.append(path)
        pass

    return tempfiles

def get_all_files(path, extentions=None, ignores=None):
    tempfiles = []
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for name in files:
                fileName, fileSuffix = os.path.splitext(name)
                fullName = os.path.join(root, name)
                fullName = fullName.replace('\\','/')
                relpath = get_file_relpath(fullName, path)
                if (extentions == None or (len(fileSuffix) > 0 and fileSuffix in extentions))  \
                and (ignores == None or not is_ignore_path(relpath, ignores)) \
                and (ignores == None or not (fileSuffix in ignores)):
                    if not os.path.exists(fullName):
                        continue

                    tempfiles.append(fullName)
            else:
                continue
            break
    elif os.path.exists(path):
        fileName, fileSuffix = os.path.splitext(path)
        if extentions == None or (fileSuffix in extentions):
            tempfiles.append(path)
        pass

    return tempfiles

def convert_pvr_to_png(image_file, image_ext):
	print("convert_pvr_to_png > ", image_file)
	pvr_path = image_file.replace(image_ext, "")
	if os.system("TexturePacker {pvr_pathname} --sheet {pvr_path}.png --data {pvr_path}_temp.plist --texture-format png --border-padding 0 --shape-padding 0 --disable-rotation --allow-free-size --no-trim".format(pvr_pathname = image_file, pvr_path = pvr_path)) == 0:
		os.remove(pvr_path + "_temp.plist")
		return True
	return False

def serialize_luafile(data):
    return "return " + serialize_lua(data)

def serialize_lua(data):
    lua = ""
    vtype = type(data)
    # print(vtype)
    if vtype == int or vtype == long or vtype == float:
        lua = lua + str(data)
        pass
    elif vtype == bool:
        if data:
            lua = lua + "true"
        else:
            lua = lua + "false"
        pass
    elif vtype == str:
        lua = lua + '"' + data + '"'
        pass
    elif vtype == list:
        lua = lua + "{"
        temp = []
        for value in data:
            temp.append(serialize_lua(value))
            pass
        lua = lua + ",\n".join(temp)
        lua = lua + "}"
        pass
    elif vtype == dict:
        lua = lua + "{"
        temp = []
        for key, value in sorted(data.iteritems(), key=lambda (k,v):dict_sorts.index(k) if k in dict_sorts else 999):
            temp.append("[" + serialize_lua(key) + "]=" + serialize_lua(value))
        lua = lua + ",\n".join(temp)
        lua = lua + "}"
        pass
    else:
        return ""
    return lua
    pass