import logging


def get_logger(name):
    log_format = '%(asctime)s  %(name)9s  %(levelname)6s  %(message)s'

    logging.basicConfig(level=logging.DEBUG,
                        format=log_format,
                        filename='bot.log',
                        filemode='w',
                        encoding='utf-8')

    console = logging.StreamHandler()

    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)

    return logging.getLogger(name)
