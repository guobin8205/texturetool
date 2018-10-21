#/usr/bin/python2
#coding=utf-8
#Python 3.6

class CodeFile(object):
    def __init__(self, filepath):
        self.filepath = filepath
        _, fileSuffix = os.path.splitext(self.filepath)
        if fileSuffix == '.lua':
			pattern_comment = [r'--[[.*]]', r'--']
            pass
        elif fileSuffix == '.cs':
            pattern_comment = [r'(///*(/s|.)*?/*//)|(////.*)']
            pass
		pass
    
    