import logging
import logging.config
import os

file_dir = os.path.split(os.path.realpath(__file__))[0]
logging.config.fileConfig(os.path.join(file_dir, 'logging.ini'),
                          disable_existing_loggers=False)
logger = logging.getLogger('root')
