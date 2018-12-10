# -*- coding: utf8 -*-
import os
import subprocess

class OpenCC(object):
    def __init__(
            self,
            config,
            opencc_path=os.path.join(BIN_PATH, 'opencc'),
            data_path=DATA_PATH
    ):
        """

        config is the path to opencc configuration, it can also be a name in
        BUILDIN_CONFIGS, and opencc_path is the path to the opencc executable
        file, default is 'opencc'

        """
        if config in BUILDIN_CONFIGS:
            config = BUILDIN_CONFIGS[config]
        #: the path to configuration of opencc
        self.confg = config
        #: the path to opencc executable
        self.opencc_path = opencc_path
        #: the path to data_path
        self.data_path = data_path

    def convert(self, text):
        """Convert text

        """
        proc = subprocess.Popen([self.opencc_path, '-c', self.confg],
                                cwd=self.data_path,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        proc.stdin.write(text.encode('utf8'))
        proc.stdin.close()

        result, err = proc.communicate()
        if err:
            raise RuntimeError('Failed to call opencc with exit code %s' % err)
        # code = proc.wait()
        # if code:
        #     raise RuntimeError('Failed to call opencc with exit code %s' % code)
        # result = proc.stdout.read()
        return result.decode('utf8')