from __future__ import absolute_import
import logging
import os
from os import path


__version__ = '0.5.1'

# logging
logger = logging.getLogger(__name__)
logger.propagate = False
# add loggers
ch = logging.StreamHandler()
CMSL1T_LOGLEVEL = logging.INFO
if os.environ.get("DEBUG", False):
    CMSL1T_LOGLEVEL = logging.DEBUG

ch.setLevel(CMSL1T_LOGLEVEL)
# log format
formatter = logging.Formatter(
    '%(asctime)s [%(name)s]  %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if 'PROJECT_ROOT' not in os.environ:
    logger.warning("Could not find environmental variable 'PROJECT_ROOT'")
    logger.warning("You should to run 'source setup.sh' first!")
    HERE = path.dirname(path.abspath(__file__))
    PROJECT_ROOT = path.abspath(path.join(HERE, path.pardir))
else:
    PROJECT_ROOT = os.environ['PROJECT_ROOT']
