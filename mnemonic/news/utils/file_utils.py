import errno
import logging
import os
import shutil
import tempfile

_LOG = logging.getLogger(__name__)


class ShelveFile(object):
    def __init__(self, filepath, mode='w+', temp_dir=None):
        self.filepath = filepath
        self.mode = mode
        self.temp_dir = temp_dir

    def __enter__(self):
        args = {'mode': self.mode,
                'delete': False}
        if self.temp_dir:
            args['dir'] = self.temp_dir
        self.temp_file = tempfile.NamedTemporaryFile(**args)
        return self.temp_file

    def __exit__(self, *args):
        self.temp_file.close()
        tmp_path = os.path.join(tempfile.gettempdir(), self.temp_file.name)
        if args and args[0] is not None and issubclass(args[0], BaseException):
            _LOG.exception('Not moving file to destination - %s. Deleting temp file' % str(args))
            os.remove(tmp_path)
        else:
            shutil.move(tmp_path, self.filepath)


def mkdir_p(dirname):
    """Create a hierarchy of directories, if doesn't already exist see
    http://stackoverflow.com/a/600612/555656
    """
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(dirname):
            pass
        else:
            raise e
    else:
        _LOG.debug("Created directory {}".format(dirname))
