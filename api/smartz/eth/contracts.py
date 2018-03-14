# -*- coding: utf-8 -*-
#
#   smartz.eth.contracts
#


def make_generic_function_spec(abi_array):
    """
    Generates ETHFunctionSpec for each function found in ABI.
    :param abi_array: contract Ethereum ABI
    :return: list of ETHFunctionSpec
    """
    raise NotImplementedError()


def merge_function_titles2specs(spec_array, titles_info):
    """
    Attach human-friendly titles and descriptions to passed ETHFunctionSpec list.

    Processed elements: function titles and descriptions, function input arguments titles and descriptions,
    titles and descriptions of function outputs.

    :param spec_array: list of ETHFunctionSpec
    :param titles_info: data according to function_titles_info.json schema
    :return: modified ETHFunctionSpec
    """
    raise NotImplementedError()
