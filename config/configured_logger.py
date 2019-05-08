import logging.config
import os
import coloredlogs

file_dir = os.path.split(os.path.realpath(__file__))[0]
logging.config.fileConfig(os.path.join(file_dir, 'logging.ini'),
                          disable_existing_loggers=False)
logger = logging.getLogger('root')
coloredlogs.install(level='DEBUG', logger=logger, fmt=logger.__dict__['parent'].handlers[0].formatter._fmt)
