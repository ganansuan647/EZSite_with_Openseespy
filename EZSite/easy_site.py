from collections import namedtuple
from loguru import logger

class ShouldNotInstantiateError(Exception):
    pass


class EZSite(object):
    def __init__(self, site_name):
        logger.error('EZSite is a abstract class!Should not be instantiated!')
        raise ShouldNotInstantiateError('Abstract class EZSite accidentally instantiated!')


if __name__ == "__main__":
   





