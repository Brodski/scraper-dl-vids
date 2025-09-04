# logging_config.py
import logging
import env_file as env_varz
import os


class LoggerConfig:
    def __init__(self, name, log_file='app.log', level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.get_log_level()) # Both the logger and the handler must be set (handler >= logger)

        if not self.logger.handlers:  # prevent duplicate handlers
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.get_log_level())
            dateformat = '%H:%M:%S'
            formatter = logging.Formatter('%(asctime)s.%(msecs)03d |%(name)-6.6s %(funcName)-10.10s| %(message)s', dateformat)

            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)


    def get_log_level(self):
        LOG_LEVEL = env_varz.DEBUG_LEVEL.upper() if env_varz.DEBUG_LEVEL else "DEBUG"
        level = logging.INFO
        if LOG_LEVEL == "DEBUG":
            level = logging.DEBUG
        if LOG_LEVEL == "INFO":
            level = logging.INFO
        if LOG_LEVEL == "WARNING":
            level = logging.WARNING
        if LOG_LEVEL == "ERROR":
            level = logging.ERROR
        if LOG_LEVEL == "CRITICAL":
            level = logging.CRITICAL
        return level


    def get_logger(self) -> logging.Logger:
        return self.logger