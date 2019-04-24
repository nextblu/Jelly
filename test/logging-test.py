import logging
import logging.config

logging.config.fileConfig('../config/logging.ini')

logger = logging.getLogger('root')
logger.debug('TEST DEBUG')
