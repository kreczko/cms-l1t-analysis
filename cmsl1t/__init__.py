from __future__ import absolute_import
import logging
import os
from os import path
import sys


__version__ = '0.5.1'

# logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# add loggers
ch = logging.StreamHandler()
if not os.environ.get("DEBUG", False):
    ch.setLevel(logging.INFO)
else:
    ch.setLevel(logging.DEBUG)
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

PY3 = sys.version_info[0] == 3
