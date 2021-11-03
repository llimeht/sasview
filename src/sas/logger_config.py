from __future__ import print_function

import logging
import logging.config
import os
import os.path

import importlib.resources

from sas import get_custom_config

'''
Module that manages the global logging
'''


class SetupLogger(object):
    '''
    Called at the beginning of run.py or sasview.py
    '''

    def __init__(self, logger_name):
        self._find_config_file()
        self.name = logger_name

    def config_production(self):
        logger = logging.getLogger(self.name)
        if not logger.root.handlers:
            self._read_config_file()
            logging.captureWarnings(True)
            logger = logging.getLogger(self.name)
        logging.getLogger('matplotlib').setLevel(logging.WARN)
        return logger

    def config_development(self):
        '''
        '''
        self._read_config_file()
        logger = logging.getLogger(self.name)
        self._update_all_logs_to_debug(logger)
        logging.captureWarnings(True)
        self._disable_debug_from_config()
        logging.getLogger('matplotlib').setLevel(logging.WARN)
        return logger

    def _disable_debug_from_config(self):
        '''disable DEBUG logs as per user configuration (DEBUG logs disabled by default)'''
        disable_debug = True
        custom_config = get_custom_config()

        if hasattr(custom_config, "FILTER_DEBUG_LOGS"):
            if type(custom_config.FILTER_DEBUG_LOGS) is bool:
                disable_debug = custom_config.FILTER_DEBUG_LOGS
            else:
                logging.warning("FILTER_DEBUG_LOGS has invalid value in custom_config.py")

        if disable_debug:
            # logging.info("Note: DEBUG logs are disabled.")
            logging.disable(logging.DEBUG)

    def _read_config_file(self):
        if self.config_file is not None:
            logging.config.fileConfig(self.config_file)

    def _update_all_logs_to_debug(self, logger):
        '''
        This updates all loggers and respective handlers to DEBUG
        '''
        for handler in logger.handlers or logger.parent.handlers:
            handler.setLevel(logging.DEBUG)
        for name, _ in logging.Logger.manager.loggerDict.items():
            logging.getLogger(name).setLevel(logging.DEBUG)

    def _find_config_file(self, filename="logging.ini"):
        '''
        The config file is in:
        Debug ./sasview/
        Packaging: sas/sasview/
        Packaging / production does not work well with absolute paths
        thus importlib is used to find a filehandle to the resource
        wherever it is actually located.
        '''
        self.config_file = None
        try:
            self.config_file = importlib.resources.open_text('sas', filename)
        except FileNotFoundError:
            print("ERROR: logging.ini not found...")
