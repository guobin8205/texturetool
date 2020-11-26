#!/usr/bin/env python  
# coding=utf-8  
# Python 3.6
from multiprocessing.synchronize import Lock
from PIL import Image
from utils import *

pathlock = Lock()  # type: Lock

class TextureConvert(object):
    def __init__(self):
        self.args = get_args()
        self.tool = "PVRTexToolCLI"
        pass

    def execute(self):
        print("BuildTool excute >")
        pass

    def get_texture_format(self, option, exists_alpha=True):
        args = get_args()
        if args.convert_tool == "PVRTexToolCLI":
            if option == "ETC1":
                return "ETC1"
            elif option == "ETC2":
                if exists_alpha:
                    return "ETC2_RGBA"
                else:
                    return "ETC2_RGB"
        elif args.convert_tool == "etctool":
            if option == "ETC1":
                return "ETC1"
            elif option == "ETC2":
                if exists_alpha:
                    return "RGBA8"
                else:
                    return "RGB8"
        elif args.convert_tool == "TexturePacker":
            if option == "PVRTC4":
                if exists_alpha:
                    return "PVRTCI_4BPP_RGBA"
                else:
                    return "PVRTCI_4BPP_RGB"
            if option == "ETC1":
                return "ETC1_RGB"
            elif option == "ETC2":
                if exists_alpha:
                    return "RGBA8"
                else:
                    return "RGB8"
            pass
        return None

    def get_texture_quality(self, option):
        args = get_args()
        if args.convert_tool == "PVRTexToolCLI":
            # 'pvrtcfastest' | 'pvrtcfast' | 'pvrtcnormal' | 'pvrtchigh' | 'pvrtcbest' | 'etcfast' | 'etcslow' | 'etcfastperceptual' | 'etcslowperceptual'
            # | 'astcveryfast' | 'astcfast' | 'astcmedium' | 'astcthorough' | 'astcexhaustive']
            if option == "ETC1":
                return "etcfast"
            elif option == "PVRTC":
                return "pvrtcbest"
        elif args.convert_tool == "etctool":
            pass
        elif args.convert_tool == "TexturePacker":
            pass
        return None

    def pvr_compress_ccz(self, temp_file, destfile):
        pvr = open(temp_file, 'rb')
        pvrData = pvr.read()
        pvrccz = open(destfile, "wb")
        pvrccz.write(struct.pack(">4sHHII",b"CCZ!",0,1,0,len(pvrData)))
        pvrccz.write(zlib.compress(pvrData))
        pvr.close()
        pvrccz.close()
        return True

    def _convert_to_texture(self, input_file, output_file, exists_alpha):
        args = get_args()
        if args.convert_tool == "PVRTexToolCLI":
            command = "%s -i %s -o %s" % (args.convert_tool, input_file, output_file)
            texture_format = self.get_texture_format(args.image_option, exists_alpha)
            if texture_format is not None:
                command = command + " -f %s" % (texture_format)

            texture_quality = self.get_texture_quality(args.image_option)
            if texture_quality is not None:
                command = command + " -q %s" % (texture_quality)
        elif args.convert_tool == "etctool":
            command = "%s %s -output %s -j 4" % ("etctool", input_file, output_file)
            texture_format = self.get_texture_format(args.image_option, exists_alpha)
            if texture_format is not None:
                command = command + " -format %s" % (texture_format)
        elif args.convert_tool == "TexturePacker":
            command = "TexturePacker \"%s\" --sheet \"%s\" " % (input_file, output_file)

        if args.log:
            log("convert_to_texture command > %s" % command)

    def convert_to_texture(self, input_path,  _suffix="", _zlib=True):
        log("convert_to_texture image path > %s"%(input_path))
        start_time = time.time()
        args = get_args()
        dirname, _ = os.path.split(os.path.relpath(input_path, args.work_path))
        output_dir = os.path.join(args.output, dirname)
        tempdir = None
        if args.tempdir:
            tempdir = os.path.join(args.tempdir, dirname)

        _, filename = os.path.split(input_path)
        pre, ext = os.path.splitext(filename)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        exists_alpha = ext != ".jpg"
        dst_rgb_pvr_file = None
        dst_a_pvr_file = None
        if _zlib:
            dst_rgb_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr.ccz")
        else:
            dst_rgb_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr")

        if args.image_option == "ETC1":
            if _zlib:
                dst_a_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr.ccz@alpha")
            else:
                dst_a_pvr_file = os.path.join(output_dir, pre + _suffix + ".pvr@alpha")

        if os.path.exists(dst_rgb_pvr_file):
            # print("input_path > ", input_path)
            # print("input_path time > ", timestamp_to_time(get_file_modifytime(input_path)))
            # print("dst_rgb_pvr_file > ", dst_rgb_pvr_file)
            # print("dst_rgb_pvr_file time > ", timestamp_to_time(get_file_modifytime(dst_rgb_pvr_file)))
            if get_file_modifytime(input_path) < get_file_modifytime(dst_rgb_pvr_file):
                if args.image_option == "ETC1":
                    if dst_a_pvr_file is not None:
                        return {"file": dst_rgb_pvr_file, "alpha": dst_a_pvr_file, "ext": ext}
                return {"file": dst_rgb_pvr_file, "ext": ext}
            pass

        newtempdir = None
        try:
            if tempdir is not None:
                newtempdir = tempdir
                if not os.path.isdir(newtempdir):
                    if pathlock.acquire():
                        if not os.path.isdir(newtempdir):
                            os.makedirs(newtempdir)
                        pathlock.release()
            else:
                newtempdir = tempfile.mkdtemp()

            tmp_rgb_file = None
            tmp_a_file = None
            if args.image_option == "ETC1":
                if exists_alpha:
                    tmp_rgb_file = os.path.join(newtempdir, pre.replace(" ", "_") + _suffix + "_rgb.png")
                    tmp_a_file = os.path.join(newtempdir, pre.replace(" ", "_") + _suffix + "_a.png")
                    with open(input_path, 'rb') as f:
                        im = Image.open(f)
                        im = im.convert('RGBA')
                        alphadata = im.tobytes("raw", "A")
                        im.convert('RGB').save(tmp_rgb_file)
                        Image.frombytes("L", im.size, alphadata).save(tmp_a_file)
                        del im
                        pass
                    pass
                else:
                    tmp_rgb_file = input_path
            else:
                tmp_rgb_file = input_path

            tmp_rgb_pvr_file = os.path.join(newtempdir, pre.replace(" ", "_") + _suffix + ".pvr")

            command = "%s -i %s -o %s" % ("PVRTexToolCLI",  tmp_rgb_file, tmp_rgb_pvr_file)
            texture_format = self.get_texture_format(args.image_option, exists_alpha)
            if texture_format is not None:
                command = command + " -f %s" % (texture_format)

            texture_quality = self.get_texture_quality(args.image_option)
            if texture_quality is not None:
                command = command + " -q %s" % (texture_quality)

            # command = "%s %s -output %s -j 4" % ("etctool", tmp_rgb_file, tmp_rgb_pvr_file)
            # texture_format = self.get_etc_texture_format(args.image_option, exists_alpha)
            # if texture_format is not None:
            #     command = command + " -format %s" % (texture_format)
            if args.log:
                log("convert_to_texture command > %s" % command)

            p = Popen(command, stdout=PIPE, shell=True, stderr=PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                log("Non zero exit code:%s executing: %s" % (p.returncode, command))
                log(err)
                return

            tmp_a_pvr_file = None
            if args.image_option == "ETC1" and tmp_a_file is not None:
                tmp_a_pvr_file = os.path.join(newtempdir, pre.replace(" ", "_") + _suffix + "_a.pvr")
                command = "%s -i %s -o %s" % ("PVRTexToolCLI", tmp_a_file, tmp_a_pvr_file)
                texture_format = self.get_texture_format(args.image_option, exists_alpha)
                if texture_format is not None:
                    command = command + " -f %s" % (texture_format)
                texture_quality = self.get_texture_quality(args.image_option)
                if texture_quality is not None:
                    command = command + " -q %s" % (texture_quality)
                # command = "%s %s -output %s -j 4" % ("etctool", tmp_a_file, tmp_a_pvr_file)
                # texture_format = self.get_etc_texture_format(args.image_option, exists_alpha)
                # if texture_format is not None:
                #     command = command + " -format %s" % (texture_format)
                if args.log:
                    log("convert_to_texture command alpha > %s" % command)
                p = Popen(command, stdout=PIPE, shell=True, stderr=PIPE)
                out, err = p.communicate()
                if p.returncode != 0:
                    log("Non zero exit code:%s executing: %s" % (p.returncode, command))
                    log(err)
                    return

            if _zlib:
                if self.pvr_compress_ccz(tmp_rgb_pvr_file, dst_rgb_pvr_file):
                    pass
                if args.image_option == "ETC1" and dst_a_pvr_file is not None:
                    if self.pvr_compress_ccz(tmp_a_pvr_file, dst_a_pvr_file):
                        pass
                    pass
            else:
                os.rename(tmp_rgb_pvr_file, dst_rgb_pvr_file)

        except Exception as e:
            raise
        else:
            pass
        finally:
            if tempdir is None:
                shutil.rmtree(newtempdir)

            microseconds = round((time.time() - start_time), 2)
            log("convert %s elapsed time %.2fs" % (input_path, microseconds))

        if args.image_option == "ETC1":
            if dst_a_pvr_file is not None:
                return {"file": dst_rgb_pvr_file, "alpha": dst_a_pvr_file, "ext": ext}
            pass
        return {"file": dst_rgb_pvr_file, "ext": ext}
