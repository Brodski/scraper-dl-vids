# logging_config.py
import logging
import env_file as env_varz
import os
from controllers.MicroTranscriber.cloudwatch import Cloudwatch

class LoggerConfig:
    def __init__(self, name, is_cloudwatch_logs=False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.get_log_level()) # Both the logger and the handler must be set (handler >= logger)
            
        dateformat = '%H:%M:%S'
        formatter_bski: logging.Formatter = logging.Formatter('%(asctime)s.%(msecs)03d |%(name)-6.6s %(funcName)-10.10s| %(message)s', dateformat)

        if not self.logger.handlers:  # prevent duplicate handlers
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.get_log_level())

            console_handler.setFormatter(formatter_bski)
            self.logger.addHandler(console_handler)
            
            # Add CloudWatch
            if is_cloudwatch_logs == True:
                print("Adding CloudWatch")
                cloudwatch = Cloudwatch()
                cloudwatch.setFormatter(formatter_bski) # cloudwatch.formatter is inherited from "logging.Handler" (the python lib)
                self.logger.addHandler(cloudwatch)


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