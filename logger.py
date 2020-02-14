import logging
import logging.handlers
import errno
import time
import os


# mkdir
def mk_dir(path):
    try:
        if not (os.path.isdir(path)):
            os.makedirs(os.path.join(str(path)))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory.")
            raise

# Logging
def get_info_logger_rs():

    LOGGER_NAME = "INFO_LOGGER"
    # 로그레벨(DEBUG: 10, INFO: 20, WARNING: 30)
    LOGLEVEL = 20
    # 로그 PATH
    LOGPATH = "C:\\Users\\admin\\PycharmProjects\\webCrawl\\log\\"

    logger = logging.getLogger(LOGGER_NAME)

    if len(logger.handlers)==0:
        fileMaxByte = 1024 * 1024 * 10 #10MB

        y = time.strftime("%Y")
        m = time.strftime("%m")
        dir_y = "{0}\\{1}".format(LOGPATH,y)
        dir_m = "{0}\\{1}\\{2}".format(LOGPATH,y,m)

        mk_dir(dir_y)
        mk_dir(dir_m)

        fileh = logging.handlers.RotatingFileHandler("{0}\\{1}\\{2}\\{3}_resolution_info.log".format(LOGPATH, y, m, time.strftime("%Y%m%d")), maxBytes=fileMaxByte, backupCount=100)
        streamh = logging.StreamHandler()

        formatter = logging.Formatter("[%(asctime)s | %(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

        fileh.setFormatter(formatter)
        streamh.setFormatter(formatter)

        logger.addHandler(fileh)
        logger.addHandler(streamh)

        logger.setLevel(LOGLEVEL)

    return logger

# Logging
def get_error_logger_rs():

    LOGGER_NAME = "ERROR_LOGGER"
    # 로그레벨(DEBUG: 10, INFO: 20, WARNING: 30)
    LOGLEVEL = 20
    # 로그 PATH
    LOGPATH = "C:\\Users\\admin\\PycharmProjects\\webCrawl\\log\\"

    logger = logging.getLogger(LOGGER_NAME)

    if len(logger.handlers)==0:
        fileMaxByte = 1024 * 1024 * 10 #10MB

        y = time.strftime("%Y")
        m = time.strftime("%m")
        dir_y = "{0}\\{1}".format(LOGPATH,y)
        dir_m = "{0}\\{1}\\{2}".format(LOGPATH,y,m)

        mk_dir(dir_y)
        mk_dir(dir_m)

        fileh = logging.handlers.RotatingFileHandler("{0}\\{1}\\{2}\\{3}_resolution_error.log".format(LOGPATH, y, m, time.strftime("%Y%m%d")), maxBytes=fileMaxByte, backupCount=100)
        streamh = logging.StreamHandler()

        formatter = logging.Formatter("[%(asctime)s | %(levelname)s | %(filename)s : %(lineno)s] %(message)s", "%Y-%m-%d %H:%M:%S")

        fileh.setFormatter(formatter)
        streamh.setFormatter(formatter)

        logger.addHandler(fileh)
        logger.addHandler(streamh)

        logger.setLevel(LOGLEVEL)

    return logger

# Logging
def get_info_logger_nt():

    LOGGER_NAME = "INFO_LOGGER"
    # 로그레벨(DEBUG: 10, INFO: 20, WARNING: 30)
    LOGLEVEL = 20
    # 로그 PATH
    LOGPATH = "C:\\Users\\admin\\PycharmProjects\\webCrawl\\log\\"

    logger = logging.getLogger(LOGGER_NAME)

    if len(logger.handlers)==0:
        fileMaxByte = 1024 * 1024 * 10 #10MB

        y = time.strftime("%Y")
        m = time.strftime("%m")
        dir_y = "{0}\\{1}".format(LOGPATH,y)
        dir_m = "{0}\\{1}\\{2}".format(LOGPATH,y,m)

        mk_dir(dir_y)
        mk_dir(dir_m)

        fileh = logging.handlers.RotatingFileHandler("{0}\\{1}\\{2}\\{3}_notice_info.log".format(LOGPATH, y, m, time.strftime("%Y%m%d")), maxBytes=fileMaxByte, backupCount=100)
        streamh = logging.StreamHandler()

        formatter = logging.Formatter("[%(asctime)s | %(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

        fileh.setFormatter(formatter)
        streamh.setFormatter(formatter)

        logger.addHandler(fileh)
        logger.addHandler(streamh)

        logger.setLevel(LOGLEVEL)

    return logger

# Logging
def get_error_logger_nt():

    LOGGER_NAME = "ERROR_LOGGER"
    # 로그레벨(DEBUG: 10, INFO: 20, WARNING: 30)
    LOGLEVEL = 20
    # 로그 PATH
    LOGPATH = "C:\\Users\\admin\\PycharmProjects\\webCrawl\\log\\"

    logger = logging.getLogger(LOGGER_NAME)

    if len(logger.handlers)==0:
        fileMaxByte = 1024 * 1024 * 10 #10MB

        y = time.strftime("%Y")
        m = time.strftime("%m")
        dir_y = "{0}\\{1}".format(LOGPATH,y)
        dir_m = "{0}\\{1}\\{2}".format(LOGPATH,y,m)

        mk_dir(dir_y)
        mk_dir(dir_m)

        fileh = logging.handlers.RotatingFileHandler("{0}\\{1}\\{2}\\{3}_notice_error.log".format(LOGPATH, y, m, time.strftime("%Y%m%d")), maxBytes=fileMaxByte, backupCount=100)
        streamh = logging.StreamHandler()

        formatter = logging.Formatter("[%(asctime)s | %(levelname)s | %(filename)s : %(lineno)s] %(message)s", "%Y-%m-%d %H:%M:%S")

        fileh.setFormatter(formatter)
        streamh.setFormatter(formatter)

        logger.addHandler(fileh)
        logger.addHandler(streamh)

        logger.setLevel(LOGLEVEL)

    return logger
