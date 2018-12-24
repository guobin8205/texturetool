#!/usr/bin/env python
# coding=utf-8
# Python 3.6
from opencc import OpenCC
import re

cc = OpenCC('s2t')
print(cc.convert(u"sss你好，中国？"))
