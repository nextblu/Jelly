import logging
import logging.config
from config import configured_logger

logger = configured_logger.logger
logger.debug('TEST DEBUG')
logger.info('TEST INFO')
