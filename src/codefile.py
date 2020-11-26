#/usr/bin/python2
#coding=utf-8
#Python 3.6
import os
import re

import chardet
import codecs
from opencc import OpenCC
from utils import *


class CodeFile(object):
    def __init__(self, filepath):
        self.args = get_args()
        self.filepath = filepath
        _, fileSuffix = os.path.splitext(self.filepath)
        self.pattern_comment = None
        self.pattern_ignore = None
        self.pattern_string = None
        self.chinese_list = []
        self.translated_list = []
        if fileSuffix == '.lua':
            self.pattern_comment = r'--\[((=*)\[(.|\n)*?)\]\2\]|--[^\r\n]*'
            self.pattern_ignore = r'((print(f|Info|))|dump)\s*\(.*\)'
            self.pattern_string = [r'("(\\.|[^\\"])*")', r"('(\\.|[^\\'])*')"]
        elif fileSuffix == '.cs':
            self.pattern_comment = r'//[^\r\n]*|/\*.*?\*/'
            self.pattern_ignore = r'(Console.WriteLine|WriteLog)\s*\(.*\)'
            self.pattern_string = [r'("(\\.|[^\\"])*")']
        elif fileSuffix == '.php':
            self.pattern_comment = r'--\[((=*)\[(.|\n)*?)\]\2\]|--[^\r\n]*'
            self.pattern_ignore = r'(print)\s*\(.*\)'
            self.pattern_string = [r'("(\\.|[^\\"])*")', r"('(\\.|[^\\'])*')"]
        elif fileSuffix == '.sql':
            self.pattern_comment = r'--[^\r\n]*|/\*.*?\*/'
            self.pattern_ignore = r'(print)\s*\(.*\)'
            self.pattern_string = [r'("(\\.|[^\\"])*")', r"('(\\.|[^\\'])*')"]
        else:
            # self.pattern_string = [r'("(\\.|[^\\"])*")']
            pass
        pass

    def find_chinese(self):
        f = open(self.filepath, 'rb')
        content = f.read()
        source_encoding = chardet.detect(content)['encoding']
        if (source_encoding == None):
            return []
        content = content.decode(source_encoding, 'ignore')
        f.close()
        if self.pattern_string != None:
            if isinstance(self.pattern_string, str):
                resultlist = re.findall(self.pattern_string, content, re.MULTILINE)
                print(resultlist)
                for result in resultlist:
                    tmp_str = result[0]
                    match = re.search(u'[\u4e00-\u9fff]+', tmp_str)
                    if match:
                        self.chinese_list.append(tmp_str)
            elif isinstance(self.pattern_string, list):
                for pat in self.pattern_string:
                    resultlist = re.findall(pat, content, re.DOTALL)
                    for result in resultlist:
                        tmp_str = result[0]
                        # print(str)
                        match = re.search(u'[\u4e00-\u9fff]+', tmp_str)
                        if match:
                            self.chinese_list.append(tmp_str)
        else:
            self.chinese_list.append(content)
        return self.chinese_list

    def convert_chinese(self, stype='s2twp'):
        cc = OpenCC(stype)
        for chinese in self.chinese_list:
            # if self.args.log:
            #     log("converting chinese file > %s -- %s" % (self.filepath, chinese))
            # if(self.filepath == "E:/server/Abroad/com.bf.sgs.stathw/Backup/Core/Json/JsonReader.cs"):
            #     log("aaa")
            self.translated_list.append(cc.convert(chinese))

    def replace_traslated(self):
        f = open(self.filepath, 'rb')
        content = f.read()
        source_encoding = chardet.detect(content)['encoding']
        f.close()
        if (source_encoding == None):
            return False
        if len(self.chinese_list) <= 0:
            return False
        content = content.decode(source_encoding, 'ignore')
        for i in range(len(self.chinese_list)):
            content = content.replace(self.chinese_list[i], self.translated_list[i])

        output_path = self.filepath
        if self.args.output:
            if os.path.isdir(self.args.output):
                relpath = os.path.relpath(self.filepath, self.args.path)
                if relpath and relpath != '.':
                    output_path = os.path.join(self.args.output, relpath)
                    pass
                else:
                    output_path = self.filepath
            elif os.path.exists(self.args.output):
                output_path = self.args.output
        codecs.open(output_path, 'w', encoding='utf-8').write(content)


    def translate_cht(self):
        if self.args.log:
            log("translating file > %s" % self.filepath)
        # try:
            self.find_chinese()
            if self.args.log:
                log("find strings file > %s, total strings=%d" % (self.filepath, len(self.chinese_list)))
            self.convert_chinese()
            if self.args.log:
                log("relaceing chinese file > %s" % self.filepath)
            self.replace_traslated()
            if self.args.log:
                log("relace done file > %s" % self.filepath)
        # except:
        #     return False
        return True

    def list_chinese(self):
        args = get_args()
        if args.log:
            log("list_chinese file > %s" % self.filepath)

        if os.path.isdir(self.filepath):
            return []
        f = open(self.filepath, 'rb')
        content = f.read()
        source_encoding = chardet.detect(content)['encoding']
        if(source_encoding == None):
            return []
        content = content.decode(source_encoding, 'ignore')
        if self.pattern_comment != None:
            content = re.sub(self.pattern_comment, "", content)
        if self.pattern_ignore != None:
            content = re.sub(self.pattern_ignore, "", content)
            self.chinese_list = []
        if self.pattern_string != None:
            if isinstance(self.pattern_string, str):
                resultlist = re.findall(self.pattern_string, content)
                for result in resultlist:
                    temp_str = result[0]
                    match = re.search(u'[\u4e00-\u9fff]+', temp_str)
                    if match:
                        self.chinese_list.append(temp_str)
            elif isinstance(self.pattern_string, list):
                for pat in self.pattern_string:
                    resultlist = re.findall(pat, content)
                    for result in resultlist:
                        temp_str = result[0]
                        match = re.search(u'[\u4e00-\u9fff]+', temp_str)
                        if match:
                            self.chinese_list.append(temp_str)
        return self.chinese_list

    def replace_tag(self):
        # I18NHelper.FormatString(mContext, "1539933872")
        if os.path.isdir(self.filepath):
            return
        if self.chinese_list and len(self.chinese_list) > 0:
            f = open(self.filepath, 'rb')
            content = f.read()
            source_encoding = chardet.detect(content)['encoding']
            if (source_encoding == None):
                return
            content = content.decode(source_encoding, 'ignore')
            for chinese in self.chinese_list:
                md5str = hashlib.md5(chinese.encode('utf-8')).hexdigest()
                # print(md5str, chinese, "I18NHelper.FormatString(Context, \"{0}\")".format(md5str))
                # if content.find(chinese):
                #     print(content.find(chinese))
                # else:
                #     print(False)
                # print(content)
                # print(chardet.detect(content)['encoding'])
                content = content.replace(chinese, u"I18NHelper.FormatString(\"{0}\")".format(md5str))
                # print(content)
            codecs.open(self.filepath, 'w', encoding='utf-8').write(content)