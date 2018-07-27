# -*- coding: utf-8 -*-
#
#   smartz.api.constructor_engine
#

from abc import ABCMeta, abstractmethod


class ConstructorInstance(metaclass=ABCMeta):
    """
    Constructor interface (v2).
    """

    @abstractmethod
    def get_version(self):
        """
        Get version of constructor api. If function is not exist version 0 would be used
        Since version 1 of constructor api

        Returns: {
            "result": "success",
            "blockchain": "ethereum", # string, ethereum or eos
            "version": 2 # integer
        }

        or throws exception.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_params(self):
        """
        Get json schema of construct() parameters.

        Returns: {
            "result": "success",
            "schema": json_schema,
            "ui_schema": ui_schema
        }

        or throws exception.
        """
        raise NotImplementedError()

    @abstractmethod
    def construct(self, fields):
        """
        Constructs contract source code.

        :param fields: data which is compatible to schema provided by get_params()

        Returns on success: {
            "result": "success",
            "source": source code string,
            "contract_name": main contract name
        }

        or on global error: {
            "result": "error",
            "error_descr": error string
        }

        or on error specific to some provided fields: {
            "result": "error",
            "errors": {
                field name: error string,
                ...
            }
        }
        """
        raise NotImplementedError()

    @abstractmethod
    def post_construct(self, fields, abi_array):
        """
        Called after compiling constructed source to get extra contract info.

        :param fields: fields data provided during construct
        :param abi_array: Ethereum ABI of compiled contract
        :return: {
            "result": "success",
            "function_specs": ETHFunctionAdditionalDescriptions (see json-schema/constructor.json),
            "dashboard_functions": list of function names
        }

        Should not throw.
        """
        raise NotImplementedError()
