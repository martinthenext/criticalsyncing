import os
import shutil
import logging

logger = logging.getLogger(__name__)


class TmpDirectory:
    def __init__(self, destination, tmp):
        self.tmp = tmp
        self.destination = destination

    def create(self, directory):
        logger.debug("create directory: %s", directory)
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        elif os.path.exists(directory):
            os.remove(directory)
        if os.path.isdir(self.destination):
            shutil.copytree(self.destination, directory)
        else:
            os.makedirs(directory)

    def __enter__(self):
        self.create(self.tmp)
        return self.tmp

    def __exit__(self, etype, evalue, tb):
        if etype is not None:
            logger.debug("failed, remove directory: %s", self.tmp)
            shutil.rmtree(self.tmp)
        else:
            logger.debug("ok, moving %s -> %s", self.tmp, self.destination)
            old = self.destination + "_old"
            if os.path.isdir(old):
                shutil.rmtree(old)
            os.rename(self.destination, old)
            os.rename(self.tmp, self.destination)
        return etype is None
