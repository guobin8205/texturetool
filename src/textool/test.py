#/usr/bin/python2
#coding=utf-8
#Python 2.7
from opencc import OpenCC
import re

cc = OpenCC('s2t')
print(cc.convert(u"sss你好，中国？"))
