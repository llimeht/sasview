# Setup and find Custom config dir
from __future__ import print_function

import sys
import os
from os.path import exists, expanduser, dirname, realpath, join as joinpath
import logging
import shutil
import importlib
import importlib.resources

from sasmodels.custom import load_module_from_path

logger = logging.getLogger(__name__)

def make_user_dir():
    """
    Create the user directory ~/.sasview if it doesn't already exist.
    """
    path = joinpath(expanduser("~"),'.sasview')
    if not exists(path):
        os.mkdir(path)
    return path

def load_local_config():
    logger = logging.getLogger(__name__)
    try:
        module = importlib.import_module('sas.local_config')
        #logger.info("GuiManager loaded %s", path)
        return module
    except Exception as exc:
        #logger.critical("Error loading %s: %s", path, exc)
        sys.exit()

def make_custom_config_path(user_dir):
    """
    The location of the cusstom config file.

    Returns ~/.sasview/config/custom_config.py
    """
    dirname = os.path.join(user_dir, 'config')
    # If the directory doesn't exist, create it
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    path = os.path.join(dirname, "custom_config.py")
    return path

def setup_custom_config(user_dir):
    path = make_custom_config_path(user_dir)
    if not os.path.isfile(path):
        try:
            # if the custom config file does not exist, copy the default from
            # the app dir
            with open(path, 'wt') as fh:
                fh.write(importlib.resources.read_text('sas.sasview', 'custom_config.py'))
        except Exception:
            logger.error("Could not copy default custom config.")

    #Adding SAS_OPENCL if it doesn't exist in the config file
    # - to support backcompability
    if not "SAS_OPENCL" in open(path).read():
        try:
            open(path, "a+").write("SAS_OPENCL = \"None\"\n")
        except Exception:
            logger.error("Could not update custom config with SAS_OPENCL.")

    custom_config = load_custom_config(path)
    return custom_config


def load_custom_config(path):
    if os.path.exists(path):
        try:
            module = load_module_from_path('sas.custom_config', path)
            #logger.info("GuiManager loaded %s", path)
            return module
        except Exception as exc:
            logger.error("Error loading %s: %s", path, exc)

    from sas.sasview import custom_config
    logger.info("GuiManager custom_config defaults to sas.sasview.custom_config")
    return custom_config
