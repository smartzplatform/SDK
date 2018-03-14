# -*- coding: utf-8 -*-
#
#   constructor_engine.api
#

from abc import ABCMeta, abstractmethod


class ConstructorInstance(metaclass=ABCMeta):
    """
    Constructor interface.
    """

    @abstractmethod
    def get_params(self):
        """
        Get json schema of construct() parameters.

        Returns: {
            'schema': json_schema,
            'ui_schema': ui_schema
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
            'result': "success",
            'source': source code string,
            'contract_name': main contract name
        }

        or on global error: {
            "result": "error",
            "error": error string
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
            'function_specs': list of ETHFunctionSpec,
            'dashboard_functions': list of function names
        }

        Should not throw.
        """
        raise NotImplementedError()
