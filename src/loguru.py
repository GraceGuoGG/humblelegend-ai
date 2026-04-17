import logging

logger = logging.getLogger('loguru')
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

class logger:
    @staticmethod
    def info(msg):
        logging.info(msg)
    
    @staticmethod
    def error(msg):
        logging.error(msg)
    
    @staticmethod
    def warning(msg):
        logging.warning(msg)
    
    @staticmethod
    def debug(msg):
        logging.debug(msg)