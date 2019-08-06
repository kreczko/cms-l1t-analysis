import os

import six.moves.urllib as urllib

from .. import logger


class RemoteFile(object):

    def __init__(self, file_name):
        is_remote = file_name.startswith('http')
        has_local_prefix = file_name.startswith('file://')
        if not is_remote and not has_local_prefix:
            file_name = os.path.abspath(file_name)
            file_name = 'file://' + file_name
        logger.debug('Opening file {}'.format(file_name))
        try:
            self.file_obj = urllib.request.urlopen(file_name)
        except urllib.error.URLError as e:
            if is_remote:
                raise urllib.error.URLError(e)
            else:
                raise IOError(e)

    def __enter__(self):
        return self.file_obj

    def __exit__(self, type, value, traceback):
        self.file_obj.close()
