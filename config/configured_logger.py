import logging
import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger('root')