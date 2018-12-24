#!/usr/bin/env python  
# coding=utf-8  
# Python 3.6
import os, sys
import tempfile
import shutil
import struct
import zlib

from subprocess import *
from PIL import Image
from utils import *
from config import *

class TextureConvert(object):
    def __init__(self):
        self.args = get_args()
        pass

    def execute(self):
        print("BuildTool excute >")
        pass

    def pvr_compress_ccz(self,tempfile, destfile):
        pvr = open(tempfile, 'rb')
        pvrData = pvr.read()
        pvrccz = open(destfile, "wb")
        pvrccz.write(struct.pack(">4sHHII","CCZ!",0,1,0,len(pvrData)))
        pvrccz.write(zlib.compress(pvrData))
        pvr.close()
        pvrccz.close()
        return True

    def convert_to_etc1(self, input_path, output_dir, _suffix="", _zlib=True):
        log("convert_to_etc1 image path > ", input_path)
        filepath, filename = os.path.split(input_path)
        pre,ext = os.path.splitext(filename)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        exists_alpha = ext != ".jpg"

        if _zlib:
            self.dst_rgb_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr.ccz")
            self.dst_a_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr.ccz@alpha")
        else:
            self.dst_rgb_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr")
            self.dst_a_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr" + "@alpha")

        if os.path.exists(self.dst_rgb_pvr_file):
            # print("input_path > ", input_path)
            # print("input_path time > ", timestamp_to_time(get_file_modifytime(input_path)))
            # print("dst_rgb_pvr_file > ", dst_rgb_pvr_file)
            # print("dst_rgb_pvr_file time > ", timestamp_to_time(get_file_modifytime(dst_rgb_pvr_file)))
            if get_file_modifytime(input_path) < get_file_modifytime(self.dst_rgb_pvr_file):
                return
            pass

        self.tmp_rgb_file = tempfile.mktemp(ext)
        # log("convert_to_etc1 tmp_rgb_file path > ", input_path, self.tmp_rgb_file)
        if exists_alpha:
            self.tmp_a_file = tempfile.mktemp(ext)
            # log("convert_to_etc1 tmp_a_file path > ", input_path, self.tmp_a_file)
            im = Image.open(input_path, 'r')
            im = im.convert('RGBA')
            rgbData = im.tobytes("raw", "RGB")
            alphaData = im.tobytes("raw", "A")
            im.convert('RGB').save(self.tmp_rgb_file)
            Image.frombytes("L", im.size, alphaData).save(self.tmp_a_file)
            im.close()
            pass
        # command = "convert %s -alpha Off %s" %(input_path, tmp_rgb_file)
        # os.system(command)

        # command = "convert %s -channel A -alpha extract %s" %(input_path, tmp_a_file)
        # os.system(command)
        else:
            shutil.copy(input_path, self.tmp_rgb_file)

        self.tmp_rgb_pvr_file = tempfile.mktemp(".pvr")
        # log("convert_to_etc1 tmp_rgb_pvr_file path > ", input_path, self.tmp_rgb_pvr_file)
        command = "%s -f ETC1 -i %s -o %s -q etcfast" %("PVRTexToolCLI", self.tmp_rgb_file, self.tmp_rgb_pvr_file)
        # log(command)
        p = Popen(command,stdin=PIPE,stdout=PIPE,stderr=PIPE)
        p.communicate()
        # time.sleep(0.5)
        # while p.poll() is None:
        # 	time.sleep(0.1)
        # log("abcdefg", p.stdout.read())
        # os.system(command)
        if os.path.exists(self.tmp_rgb_file):
            os.remove(self.tmp_rgb_file)

        if exists_alpha:
            self.tmp_a_pvr_file = tempfile.mktemp(".pvr")
            # log("convert_to_etc1 tmp_a_pvr_file path > ", input_path, self.tmp_a_pvr_file)
            command = "%s -f ETC1 -i %s -o %s -q etcfast" %("PVRTexToolCLI", self.tmp_a_file, self.tmp_a_pvr_file)
            # print(command)
            # os.system(command)
            p = Popen(command,stdin=PIPE,stdout=PIPE,stderr=PIPE)
            p.communicate()
            # time.sleep(0.5)
            # while p.poll() is None:
            #     time.sleep(0.1)
            # log("hijklmn", p.stdout.read())
            if os.path.exists(self.tmp_a_file):
                os.remove(self.tmp_a_file)

        if _zlib:
            if self.pvr_compress_ccz(self.tmp_rgb_pvr_file, self.dst_rgb_pvr_file):
                # time.sleep(0.5)
                if os.path.exists(self.tmp_rgb_pvr_file):
                    os.remove(self.tmp_rgb_pvr_file)
                pass

            if exists_alpha:
                if self.pvr_compress_ccz(self.tmp_a_pvr_file, self.dst_a_pvr_file):
                    # time.sleep(0.5)
                    if os.path.exists(self.tmp_a_pvr_file):
                        os.remove(self.tmp_a_pvr_file)
                    pass
                pass
        else:
            os.rename(self.tmp_rgb_pvr_file, self.dst_rgb_pvr_file)
            if exists_alpha:
                os.rename(self.tmp_a_pvr_file, self.dst_a_pvr_file)

        if exists_alpha:
            return {"color": self.dst_rgb_pvr_file, "alpha": self.dst_a_pvr_file}

        return self.dst_rgb_pvr_file