import logging

def get_logger():
    logFormatStr = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    formatter = logging.Formatter(logFormatStr,'%m-%d %H:%M:%S')

    fileHandler = logging.FileHandler("logs/summary.log")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)

    return fileHandler, streamHandler