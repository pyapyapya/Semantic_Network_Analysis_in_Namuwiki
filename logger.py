import logging


def make_logger(query: str = __name__) -> logging:
    logger = logging.getLogger(f'{query}')
    logger.setLevel(logging.DEBUG)
    fmtr = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')

    file_hdlr = logging.FileHandler(f'./{query}.log')
    file_hdlr.setLevel(logging.INFO)
    file_hdlr.setFormatter(fmtr)
    logger.addHandler(file_hdlr)
    stream_hdlr = logging.StreamHandler()
    stream_hdlr.setLevel(logging.INFO)
    logger.info('Program Execute')
    return logger