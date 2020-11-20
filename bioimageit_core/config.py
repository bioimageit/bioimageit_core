# -*- coding: utf-8 -*-
"""BioImagePy config module.

This module contains classes that allows to read
and manage configuration parameters

Example
-------
    You need to use the ConfigAccess which is a singleton to read config

    >>> # first call to load the configuration
    >>> ConfigAccess("config.json")
    >>> # or
    >>> ConfigAccess.instance().load("config.json")
    >>>
    >>> # then to access the config variables
    >>> var = ConfigAccess.instance().get('key_name')
    >>> # or access the config dictionary
    >>> config_dict = ConfigAccess.instance().var

Classes
-------
Config
ConfigManager

"""

import os
import json


class ConfigKeyNotFoundError(Exception):
    """Raised when key is not found in the config"""

    pass


class Config:
    """Allows to access config variables

    The configuration can be instantiate manually but the
    usage is to instantiate it with the singleton ConfigManager

    Parameters
    ----------
    config_file
        File where the configuration is stored in JSON format

    Attributes
    ----------
    config
        Dictionary containing the config variables

    """
    def __init__(self, config_file: str = ''):
        self.config_file = config_file
        self.config = {}
        if config_file != '':
            self.load(config_file)

    def load(self, config_file: str):
        """Read the metadata from the a json file"""
        self.config_file = config_file
        if os.path.getsize(self.config_file) > 0:
            with open(self.config_file) as json_file:
                self.config = json.load(json_file)

    def is_key(self, key: str) -> bool:
        """Check if a key exists in the config dictionary

        Parameters
        ----------
        key
            Key to check

        Returns
        -------
        bool
            True if the key exists, False otherwise

        """
        if key in self.config:
            return True
        else:
            return False

    def set(self, key: str, value):
        """Add a variable to the config

        If the variable exists it is changed

        Parameters
        ----------
        key
            Key of the variable
        value
            Value to set (can be str, dict, list)

        """
        self.config[key] = value

    def get(self, key: str) -> dict:
        """Read a variable from the config dictionary

        Parameters
        ----------
        key
            Key of the variable to read

        Returns
        -------
        Value of the config variable

        Raises
        ------
        ConfigKeyNotFoundError: if the configuration key does not exists

        """
        if key in self.config:
            return self.config[key]
        else:
            raise ConfigKeyNotFoundError('No key ' + key + ' in the config')


class ConfigAccess:
    """Singleton to access the Config

    Parameters
    ----------
    config_file
        JSON file where the config is stored

    Raises
    ------
    Exception: if multiple instantiation of the Config is tried

    """

    __instance = None

    def __init__(self, config_file: str):
        """ Virtually private constructor. """
        # if ConfigAccess.__instance != None:
        #    raise Exception("ConfigManager can be initialized only once!")
        # else:
        #    ConfigAccess.__instance = Config(config_file)
        ConfigAccess.__instance = Config(config_file)

    @staticmethod
    def instance():
        """ Static access method to the Config. """
        if ConfigAccess.__instance is None:
            ConfigAccess.__instance = Config()
        return ConfigAccess.__instance
